"""
飞书 OpenAPI 客户端 — 自建应用版

只用 stdlib（urllib + json），不需要 pip install。

功能：
  - 凭证加载（多源回退）
  - tenant_access_token 获取 + 缓存
  - 文件上传 (drive/v1/files/upload_all)
  - 导入任务 (drive/v1/import_tasks)
  - 文档块操作 (docx/v1/documents/{id}/blocks)
  - 错误码映射

不依赖：requests / lark-oapi
"""
import json
import os
import sys
import time
import uuid
import mimetypes
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib import request as urlreq, parse as urlparse, error as urlerr

API_BASE = "https://open.feishu.cn/open-apis"
TOKEN_CACHE_PATH = Path(os.environ.get("TEMP", "/tmp")) / "feishu-token.json"
DEFAULT_TIMEOUT = 30

# 已知错误码 → 友好提示
ERROR_HINTS: Dict[int, str] = {
    99991663: "app_secret 不正确（去飞书开放平台「凭证与基础信息」核对）",
    99991668: "tenant_access_token 失效（脚本会自动重试）",
    99991672: "应用未发布（去飞书开放平台「版本管理与发布」点发布版本）",
    1061002: "应用没有权限操作此文档（在飞书文档「分享」里把应用加为可编辑协作者）",
    1069902: "文档不存在或已删除",
    99991661: "API 调用频率超限（稍后重试）",
}


class FeishuError(Exception):
    def __init__(self, code: int, msg: str, hint: str = ""):
        self.code = code
        self.msg = msg
        self.hint = hint
        super().__init__(f"[{code}] {msg}{('  → ' + hint) if hint else ''}")


# ---------- 凭证加载 ----------

def load_credentials(cli_app_id: Optional[str] = None, cli_app_secret: Optional[str] = None) -> Dict[str, str]:
    """
    凭证查找优先级：
      1. 命令行参数
      2. 环境变量 FEISHU_APP_ID / FEISHU_APP_SECRET
      3. ~/.feishu-credentials.json
      4. ./.feishu-credentials.json (项目根，需 gitignore)

    返回: {"app_id": str, "app_secret": str, "default_doc_id": Optional, "default_folder_token": Optional}
    """
    if cli_app_id and cli_app_secret:
        return {"app_id": cli_app_id, "app_secret": cli_app_secret}

    env_id = os.environ.get("FEISHU_APP_ID")
    env_sec = os.environ.get("FEISHU_APP_SECRET")
    if env_id and env_sec:
        return {"app_id": env_id, "app_secret": env_sec}

    candidates = [
        Path.home() / ".feishu-credentials.json",
        Path.cwd() / ".feishu-credentials.json",
    ]
    for p in candidates:
        if p.exists():
            try:
                d = json.loads(p.read_text(encoding="utf-8"))
                if d.get("app_id") and d.get("app_secret"):
                    return d
            except Exception:
                continue

    raise FeishuError(
        0,
        "找不到飞书凭证",
        "去飞书开放平台 https://open.feishu.cn/app 创建自建应用，"
        "拿到 app_id + app_secret，写入 ~/.feishu-credentials.json，"
        "格式见 references/feishu-setup.md"
    )


# ---------- HTTP 工具 ----------

def _http(method: str, url: str, *, headers: Optional[Dict[str, str]] = None,
          body: Optional[bytes] = None, json_body: Optional[dict] = None,
          timeout: int = DEFAULT_TIMEOUT) -> Tuple[int, dict]:
    """
    统一 HTTP 调用。返回 (status, parsed_body)。
    json_body: 自动序列化为 JSON
    """
    h = dict(headers or {})
    if json_body is not None:
        body = json.dumps(json_body).encode("utf-8")
        h["Content-Type"] = "application/json; charset=utf-8"

    req = urlreq.Request(url, data=body, method=method, headers=h)
    try:
        with urlreq.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            status = resp.status
    except urlerr.HTTPError as e:
        raw = e.read()
        status = e.code
    except urlerr.URLError as e:
        raise FeishuError(0, f"网络错误: {e.reason}")

    try:
        data = json.loads(raw.decode("utf-8"))
    except Exception:
        data = {"_raw": raw.decode("utf-8", errors="replace")}

    return status, data


def _check_api(data: dict):
    """飞书 API 标准: code=0 表示成功，否则有 msg"""
    code = data.get("code", -1)
    if code != 0:
        msg = data.get("msg", "unknown error")
        hint = ERROR_HINTS.get(code, "")
        raise FeishuError(code, msg, hint)


# ---------- 客户端 ----------

class FeishuClient:
    def __init__(self, app_id: str, app_secret: str):
        self.app_id = app_id
        self.app_secret = app_secret
        self._token: Optional[str] = None
        self._token_expires: int = 0

    def token(self) -> str:
        """获取 tenant_access_token，自动缓存 + 刷新"""
        now = int(time.time())
        # 内存缓存
        if self._token and now < self._token_expires - 60:
            return self._token
        # 文件缓存
        if TOKEN_CACHE_PATH.exists():
            try:
                cache = json.loads(TOKEN_CACHE_PATH.read_text(encoding="utf-8"))
                if (cache.get("app_id") == self.app_id and
                        now < cache.get("expires", 0) - 60):
                    self._token = cache["token"]
                    self._token_expires = cache["expires"]
                    return self._token
            except Exception:
                pass
        # 重新获取
        url = f"{API_BASE}/auth/v3/tenant_access_token/internal"
        status, data = _http("POST", url, json_body={
            "app_id": self.app_id, "app_secret": self.app_secret
        })
        _check_api(data)
        self._token = data["tenant_access_token"]
        self._token_expires = now + int(data.get("expire", 7200))
        try:
            TOKEN_CACHE_PATH.write_text(json.dumps({
                "app_id": self.app_id,
                "token": self._token,
                "expires": self._token_expires,
            }), encoding="utf-8")
        except Exception:
            pass  # 缓存失败不致命
        return self._token

    def _auth_headers(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self.token()}"}

    # ---------- Drive: 上传文件 ----------

    def upload_file(self, file_path: Path, parent_node: str = "",
                    parent_type: str = "explorer") -> str:
        """
        上传文件到飞书云空间。
        parent_node: 父目录 token，留空则上传到「我的空间」根目录（个人空间根 token 需另行获取）
        parent_type: explorer (云空间) / docx_file (文档附件) / ...

        返回: file_token （后续 import_task 要用）
        """
        # 飞书云空间 v1 单文件上传：multipart/form-data
        # 注意：parent_type=explorer 需要 parent_node 是文件夹 token；
        # 如果用户没指定，试用 import 方式（飞书 import 会自己处理）

        url = f"{API_BASE}/drive/v1/files/upload_all"
        size = file_path.stat().st_size
        boundary = f"----feishuformboundary{uuid.uuid4().hex}"

        fields = {
            "file_name": file_path.name,
            "parent_type": parent_type,
            "parent_node": parent_node,
            "size": str(size),
        }
        body = self._encode_multipart(fields, file_path, boundary)

        headers = self._auth_headers()
        headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"

        status, data = _http("POST", url, headers=headers, body=body, timeout=120)
        _check_api(data)
        return data["data"]["file_token"]

    @staticmethod
    def _encode_multipart(fields: Dict[str, str], file_path: Path, boundary: str) -> bytes:
        """手写 multipart/form-data 编码（避免依赖 requests）"""
        lines: List[bytes] = []
        bdr = f"--{boundary}".encode()

        for k, v in fields.items():
            lines.append(bdr)
            lines.append(f'Content-Disposition: form-data; name="{k}"'.encode())
            lines.append(b"")
            lines.append(str(v).encode("utf-8"))

        # 文件部分
        lines.append(bdr)
        lines.append(f'Content-Disposition: form-data; name="file"; filename="{file_path.name}"'.encode())
        ctype = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
        lines.append(f"Content-Type: {ctype}".encode())
        lines.append(b"")
        lines.append(file_path.read_bytes())

        lines.append(f"--{boundary}--".encode())
        lines.append(b"")
        return b"\r\n".join(lines)

    # ---------- Drive: Import (markdown → docx) ----------

    def create_import_task(self, file_token: str, file_name: str,
                           folder_token: str = "") -> str:
        """
        创建导入任务。markdown → docx。
        folder_token: 目标文件夹 token。留空 = 用户个人空间根目录。
        返回: ticket（用于查询任务状态）
        """
        url = f"{API_BASE}/drive/v1/import_tasks"

        # mount_type=1: 我的空间（个人）；mount_key 留空则根目录
        # mount_type=2: 知识库 wiki
        # 这里用「我的空间」最简单
        point: Dict[str, Any] = {"mount_type": 1, "mount_key": folder_token}

        body = {
            "file_extension": "md",
            "file_token": file_token,
            "type": "docx",
            "file_name": file_name,
            "point": point,
        }
        status, data = _http("POST", url, headers=self._auth_headers(), json_body=body)
        _check_api(data)
        return data["data"]["ticket"]

    def query_import_task(self, ticket: str) -> Dict[str, Any]:
        """查询导入任务进度。返回: {job_status, token, type, url, ...}"""
        url = f"{API_BASE}/drive/v1/import_tasks/{ticket}"
        status, data = _http("GET", url, headers=self._auth_headers())
        _check_api(data)
        return data["data"]["result"]

    def wait_import_done(self, ticket: str, max_wait_s: int = 60,
                         poll_interval_s: float = 1.5) -> Dict[str, Any]:
        """
        轮询直到 import 完成或超时。

        飞书 import_task job_status:
          0   = 成功（result.token / result.url 有值）
          1   = 初始化中
          2   = 处理中（已上传，正在解析转换）
          3-9 = 部分错误
          >=100 = 严重错误（不支持格式等）

        以是否拿到 token 为最终判定，避免对不同版本 API 状态码语义的猜测。
        """
        deadline = time.time() + max_wait_s
        last: Optional[Dict[str, Any]] = None
        while time.time() < deadline:
            r = self.query_import_task(ticket)
            last = r
            js = r.get("job_status", -1)
            tok = r.get("token", "")
            # 拿到 token 即视为成功（最权威信号）
            if tok:
                return r
            # 已知失败状态
            if js >= 3:
                msg = r.get("job_error_msg", "") or f"import failed (job_status={js})"
                raise FeishuError(js, msg)
            # 0/1/2 都是中间或成功状态，但没 token 说明还在处理 → 继续等
            time.sleep(poll_interval_s)
        raise FeishuError(0, f"import 任务超时 ({max_wait_s}s)，最后状态: {last}")

    # ---------- Docx: 文档块 ----------

    def list_blocks(self, doc_id: str, page_size: int = 500) -> List[Dict[str, Any]]:
        """列出文档所有 block（自动翻页）"""
        url = f"{API_BASE}/docx/v1/documents/{doc_id}/blocks"
        items: List[Dict[str, Any]] = []
        page_token = ""
        while True:
            q = f"?page_size={page_size}"
            if page_token:
                q += f"&page_token={urlparse.quote(page_token)}"
            status, data = _http("GET", url + q, headers=self._auth_headers())
            _check_api(data)
            d = data["data"]
            items.extend(d.get("items", []))
            if not d.get("has_more"):
                break
            page_token = d.get("page_token", "")
            if not page_token:
                break
        return items

    def delete_blocks(self, doc_id: str, parent_block_id: str,
                       start_index: int, end_index: int) -> None:
        """
        删除指定父 block 下 [start_index, end_index) 范围的子 block。
        通常 parent_block_id = doc_id（顶层）。
        """
        url = f"{API_BASE}/docx/v1/documents/{doc_id}/blocks/{parent_block_id}/children/batch_delete"
        body = {"start_index": start_index, "end_index": end_index}
        status, data = _http("DELETE", url, headers=self._auth_headers(), json_body=body)
        _check_api(data)

    def insert_blocks(self, doc_id: str, parent_block_id: str,
                      children: List[Dict[str, Any]], index: int = 0) -> List[Dict[str, Any]]:
        """
        在指定父 block 下插入子 block 列表。
        children: 飞书 block 结构数组
        index: 插入位置（0=开头）
        """
        url = f"{API_BASE}/docx/v1/documents/{doc_id}/blocks/{parent_block_id}/children"
        body = {"children": children, "index": index}
        status, data = _http("POST", url, headers=self._auth_headers(), json_body=body)
        _check_api(data)
        return data["data"]["children"]

    def get_doc_meta(self, doc_id: str) -> Dict[str, Any]:
        """拿文档元信息（标题/创建时间等）"""
        url = f"{API_BASE}/docx/v1/documents/{doc_id}"
        status, data = _http("GET", url, headers=self._auth_headers())
        _check_api(data)
        return data["data"]["document"]


# ---------- 便捷函数 ----------

def make_doc_url(doc_token: str, *, base: str = "https://my.feishu.cn") -> str:
    """根据 doc_token 拼飞书 docx URL"""
    return f"{base}/docx/{doc_token}"


def render_error(e: FeishuError) -> str:
    """格式化错误信息（CLI 输出用）"""
    out = f"✗ 飞书 API 错误 [{e.code}]: {e.msg}"
    if e.hint:
        out += f"\n  → {e.hint}"
    return out
