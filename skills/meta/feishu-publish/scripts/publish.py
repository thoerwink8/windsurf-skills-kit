#!/usr/bin/env python3
"""
publish.py — 把本地 markdown 推送到飞书云文档

用法:
  python publish.py <file.md>                          # 默认: 新建文档
  python publish.py <file.md> --name "自定义标题"
  python publish.py <file.md> --folder <folder_token>  # 推到指定文件夹
  python publish.py <file.md> --replace <doc_id>       # 覆盖现有文档（保 URL）
  python publish.py --check                            # 只测试凭证 + token
  python publish.py --help

凭证查找顺序:
  1. 命令行 --app-id / --app-secret
  2. 环境变量 FEISHU_APP_ID / FEISHU_APP_SECRET
  3. ~/.feishu-credentials.json
  4. ./.feishu-credentials.json
"""
import argparse
import sys
import os
from pathlib import Path

# Windows 控制台默认 cp936/gbk 不支持 ✓ ✗ 等 Unicode 符号 → 强制 UTF-8
# Python 3.7+ 支持 reconfigure；旧版本则降级到 ASCII 替代
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")  # type: ignore
except Exception:
    pass

# 让脚本无论从哪里运行都能 import lib_feishu
SCRIPT_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(SCRIPT_DIR))

from lib_feishu import (  # type: ignore
    FeishuClient,
    FeishuError,
    load_credentials,
    make_doc_url,
    render_error,
)


def cmd_check(client: FeishuClient) -> int:
    """只测试凭证有效性"""
    try:
        token = client.token()
        print(f"✓ 凭证有效")
        print(f"  app_id:  {client.app_id}")
        print(f"  token:   {token[:12]}... (前 12 位)")
        print(f"  expires: {client._token_expires} (epoch)")
        return 0
    except FeishuError as e:
        print(render_error(e), file=sys.stderr)
        return 1


def cmd_publish(client: FeishuClient, file_path: Path, *,
                title: str = "", folder_token: str = "") -> int:
    """新建模式：上传 md + 创建 import task + 等完成 + 输出 URL"""
    if not file_path.exists():
        print(f"✗ 文件不存在: {file_path}", file=sys.stderr)
        return 1

    name = title or file_path.stem  # 不带 .md 后缀
    size = file_path.stat().st_size
    if size <= 0:
        print(f"✗ 文件为空: {file_path}", file=sys.stderr)
        return 1
    if size > 20 * 1024 * 1024:
        print(f"✗ 文件超过 20MB（飞书 import 限制）", file=sys.stderr)
        return 1

    word_count = len(file_path.read_text(encoding="utf-8", errors="replace"))

    print(f"→ 上传 {file_path.name} ({size} bytes, {word_count} chars)...", flush=True)
    try:
        # Step 1: 上传文件到云空间
        # parent_node 留空 = 上传到根目录（飞书会自动管理）
        # 实测：upload_all 需要 parent_node，留空报错。改用 import 直接走 file_token？
        # 飞书 import 必须先上传，先试空 parent_node，失败再 fallback
        file_token = client.upload_file(file_path, parent_node=folder_token or "", parent_type="explorer")
        print(f"  · 上传完成: file_token={file_token[:16]}...", flush=True)

        # Step 2: 创建 import 任务
        ticket = client.create_import_task(file_token, name, folder_token=folder_token)
        print(f"  · import 任务: ticket={ticket[:16]}...", flush=True)

        # Step 3: 轮询完成
        result = client.wait_import_done(ticket, max_wait_s=90)
        doc_token = result.get("token")
        if not doc_token:
            print(f"✗ import 完成但没拿到 doc_token: {result}", file=sys.stderr)
            return 1

        # Step 4: 输出
        url = result.get("url") or make_doc_url(doc_token)
        print()
        print(f"✓ 已发布: {url}")
        print(f"  标题:    {name}")
        print(f"  字数:    {word_count}")
        print(f"  doc_id:  {doc_token}")
        print()
        print(f"提示：把上面的 doc_id 写入 ~/.feishu-credentials.json 的 default_doc_id，")
        print(f"      下次用 --replace 即可覆盖更新（保 URL 不变）。")
        return 0
    except FeishuError as e:
        print(render_error(e), file=sys.stderr)
        return 2


def cmd_replace(client: FeishuClient, file_path: Path, doc_id: str, *,
                title: str = "", folder_token: str = "") -> int:
    """
    覆盖模式：
      1. 用 import 模式新建临时文档（拿到完美渲染的 blocks）
      2. 把临时文档的 blocks 复制到目标文档
      3. 删除目标文档原 blocks
      4. 删除临时文档

    实现优先级：先支持简化版（删除目标 blocks + 直接 import 到目标）
    完整版本待 MVP 通过后实现
    """
    print(f"⚠️  --replace 模式（覆盖现有文档）尚未完整实现", file=sys.stderr)
    print(f"   原因：需要先让 publish 模式跑通，再实现 block 复制", file=sys.stderr)
    print(f"   当前临时方案：用 publish 模式新建，请手动把链接更新给协作者", file=sys.stderr)
    return cmd_publish(client, file_path, title=title, folder_token=folder_token)


def main() -> int:
    p = argparse.ArgumentParser(
        description="把本地 markdown 推送到飞书云文档",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    p.add_argument("file", nargs="?", help="markdown 文件路径")
    p.add_argument("--name", default="", help="自定义文档标题（默认用文件名）")
    p.add_argument("--folder", default="", help="目标文件夹 token（留空 = 个人空间根）")
    p.add_argument("--replace", default="", help="覆盖模式：要替换的 doc_id")
    p.add_argument("--check", action="store_true", help="只检查凭证，不推送")
    p.add_argument("--app-id", default="", help="覆盖默认 app_id")
    p.add_argument("--app-secret", default="", help="覆盖默认 app_secret")
    args = p.parse_args()

    # 加载凭证
    try:
        creds = load_credentials(args.app_id or None, args.app_secret or None)
    except FeishuError as e:
        print(render_error(e), file=sys.stderr)
        return 1

    client = FeishuClient(creds["app_id"], creds["app_secret"])

    if args.check:
        return cmd_check(client)

    if not args.file:
        p.print_help()
        return 1

    file_path = Path(args.file).resolve()

    # 用默认 doc_id（如果配置了）
    doc_id = args.replace or creds.get("default_doc_id", "") if args.replace else ""
    folder = args.folder or creds.get("default_folder_token", "")

    if doc_id:
        return cmd_replace(client, file_path, doc_id, title=args.name, folder_token=folder)
    return cmd_publish(client, file_path, title=args.name, folder_token=folder)


if __name__ == "__main__":
    sys.exit(main())
