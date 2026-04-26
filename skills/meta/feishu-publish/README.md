# feishu-publish

把本地 Markdown 推送到飞书云文档的 Skill。

## 文件结构

```
feishu-publish/
├── SKILL.md                          ← Cascade 自动加载入口
└── README.md                         ← 你正在看的这个
```

## 快速开始

### 1. 一次性配置

```bash
npx @larksuite/cli@latest install
lark-cli auth login
```

浏览器确认登录后验证：

```bash
lark-cli auth status
```

### 2. 推送 Markdown

先列目标文件夹，确认不会创建重复文档或重复项目文件夹：

```powershell
$params = '{\"folder_token\":\"<TOKEN>\"}'
lark-cli drive files list --params $params --as user --format table
```

新建文档：

```powershell
lark-cli docs +create `
  --api-version v2 `
  --parent-token "<FOLDER_TOKEN>" `
  --content "@docs\showcase\showcase.md" `
  --doc-format markdown `
  --as user
```

更新已有文档：

```powershell
lark-cli docs +update `
  --api-version v2 `
  --doc "<DOCUMENT_ID_OR_URL>" `
  --markdown "@docs\showcase\showcase.md" `
  --mode replace_all `
  --as user
```

### 3. 通过 Cascade 调用

在 Windsurf 中对 Cascade 说：

```
把 docs/showcase/showcase.md 推到飞书
```

Cascade 会识别意图 → 加载 `SKILL.md` → 使用 `lark-cli` 创建或更新飞书文档。

## 依赖

- `lark-cli`
- 已登录的飞书用户身份

## 安全

- 不保存 `app_secret`。
- 不使用自建应用 tenant token。
- 发布前必须读取 `feishu.json` 并列目标文件夹，避免重复创建。

## 限制

- 只覆盖 Markdown → 飞书文档的创建/更新。
- 不处理飞书 Base、表格、日历、邮箱、会议、任务、OKR、白板、幻灯片等能力。

## 维护

- 文档生成由 `showcase-generator` 负责。
- 飞书发布由本 skill 负责。
- 公共登录与权限问题使用 `lark-shared`。
