# feishu-publish

把本地 markdown 推送到飞书云文档的 Skill。

## 文件结构

```
feishu-publish/
├── SKILL.md                          ← Cascade 自动加载入口
├── README.md                         ← 你正在看的这个
├── .env.example                      ← 凭证模板
├── scripts/
│   ├── publish.py                    ← 命令行入口
│   └── lib_feishu.py                 ← 飞书 OpenAPI 客户端
└── references/
    ├── feishu-setup.md               ← 飞书自建应用创建教程
    └── feishu-api-cheatsheet.md      ← API 速查
```

## 快速开始

### 1. 一次性配置

按 `references/feishu-setup.md` 创建飞书自建应用，拿到凭证后写入：

```
~/.feishu-credentials.json
```

格式见 `.env.example`。

### 2. 验证连通

```bash
python scripts/publish.py --check
```

### 3. 推送 markdown

```bash
# 新建文档（默认）
python scripts/publish.py docs/clash-guide.md

# 自定义标题
python scripts/publish.py docs/clash-guide.md --name "Clash 配置指南"

# 推到指定文件夹
python scripts/publish.py docs/clash-guide.md --folder <folder_token>
```

### 4. 通过 Cascade 调用

在 Windsurf 中对 Cascade 说：

```
把 docs/clash-guide.md 推到飞书
```

Cascade 会识别意图 → 加载 `SKILL.md` → 执行脚本 → 返回飞书 URL。

## 依赖

只用 Python stdlib，**不需要 pip install**。

测试过：Python 3.10+

## 安全

- 凭证文件**绝对不要进 Git**（路径在用户目录而非项目内）
- `app_secret` 等同密码，泄露后立刻去飞书开放平台重置
- 应用权限严格限定在你授权的文档/文件夹

## 限制

- markdown 单文件 ≤ 20MB（飞书 import API 上限）
- `--replace` 覆盖模式当前是 stub，会回退到 publish 模式（待 v2 完整实现）
- 飞书 API 调用频率 100 QPS（脚本调用频率远低于此，无需关心）

## 维护

- 飞书 API 变更：参考 https://open.feishu.cn/document/server-docs/docs/docs-overview
- 错误码补充：在 `lib_feishu.py` 的 `ERROR_HINTS` 字典追加
