---
name: feishu-publish
description: Publish or update a local Markdown file as a Feishu/Lark cloud document. Use this skill whenever the user wants to push a local .md file (README, showcase, project card, design doc, weekly report, knowledge base note) to Feishu, sync local docs to Feishu, update an existing Feishu document from a local file, or share a project artifact via Feishu. Supports two implementations: official lark-cli with user identity (preferred, no app secret needed) and a Python tenant-token fallback for CI or app-identity scenarios.
---

# Feishu Publish — Markdown to Feishu Cloud Doc

Publish a local Markdown file (e.g. `docs/showcase/showcase.md`) as a Feishu cloud document, or update an already-published one.

## When to use

Trigger this skill when the user expresses any of these:

- 把 X.md 推到飞书 / 发布到飞书 / 贴到飞书 / 同步到飞书
- "publish to Feishu", "feishu publish", "update Feishu doc"
- After running `showcase-generator`, the user wants the result on Feishu
- Any request to sync local Markdown to a Feishu cloud doc

## Two implementations

| Implementation | When to use | Identity | Setup cost |
| --- | --- | --- | --- |
| **A. lark-cli (preferred)** | Personal / interactive use; the user owns the target Feishu space | user | Login once with `lark-cli auth login` |
| **B. Python tenant-token (legacy)** | CI pipelines, headless server, or when an explicit Feishu self-built app is required | tenant (app) | Create self-built app + scopes + share docs with the app |

Default to **A** unless the user explicitly asks for app/tenant identity.

---

## Implementation A — lark-cli (preferred)

### A.0 Pre-flight checks (HARD RULES — never skip)

These checks exist because of a real incident on 2026-04-26 where the skill blindly created a duplicate child folder named after the project inside a parent folder that already represented the project. Always do all of the following before any create call.

1. **Read project-level metadata first.** If the project repo contains `docs/showcase/feishu.json` (or a similar `feishu.json` next to the source Markdown), load it. If it has a valid `document_id`, switch to update mode and stop here.

2. **Resolve the parent folder identity.** Ask or derive `parent_folder_token` from the user. Then list its contents:

   ```powershell
   $params = '{\"folder_token\":\"<TOKEN>\"}'
   lark-cli drive files list --params $params --as user --format table
   ```

3. **Decide whether the parent folder is already the project folder.**
   - If the parent folder's name already matches the project name (e.g. parent is `无感切号` and project is also `无感切号`), do **not** create a child folder named after the project. Publish directly into this parent.
   - Only create a sub-folder when the parent is a generic container (e.g. `个人项目`) and the project has no dedicated folder yet.

4. **Check for existing matching documents.** If a document with the intended title already exists in the target folder, prefer `docs +update` over a new `docs +create`. Update mode preserves the document URL that may already be shared.

5. **Default to dry-run on first publish.** When publishing a project for the first time and no `feishu.json` exists, append `--dry-run` to the create command and show the result to the user before actually executing.

### A.1 Setup (one-time)

```bash
npx @larksuite/cli@latest install
lark-cli auth login
```

The user completes a browser confirmation. Verify with:

```bash
lark-cli auth status
```

### A.2 Resolve target folder

The target folder is identified by `folder_token`, which appears at the end of the Feishu URL:

```text
https://my.feishu.cn/drive/folder/<folder_token>
```

Ask the user for the URL, or read it from `feishu.json` if available.

### A.3 List the folder before any write

```powershell
$params = '{\"folder_token\":\"<TOKEN>\"}'
lark-cli drive files list --params $params --as user --format table
```

Inspect the output to:

- Confirm the folder name matches the user's expectation.
- Check whether a same-titled document already exists.
- Detect whether the parent already represents the project.

### A.4 Create or update

**Create (first time, into a folder that is not yet the project folder):**

```powershell
lark-cli docs +create `
  --api-version v2 `
  --parent-token "<FOLDER_TOKEN>" `
  --content "@docs\showcase\showcase.md" `
  --doc-format markdown `
  --as user
```

The `@<relative-path>` form requires that the current working directory is the project root. Set `cwd` to the project root before calling.

**Update (an already-published doc):**

```powershell
lark-cli docs +update `
  --api-version v2 `
  --doc "<DOCUMENT_ID_OR_URL>" `
  --markdown "@docs\showcase\showcase.md" `
  --mode replace_all `
  --as user
```

If the user wants to keep the same URL after future regenerations, always update via `document_id`, not create.

### A.5 Persist publication metadata

Write `docs/showcase/feishu.json` (or the file next to the Markdown source) so the next run can update the same document instead of creating a duplicate:

```json
{
  "schema_version": 1,
  "project_name": "<NAME>",
  "source": "docs/showcase/showcase.md",
  "feishu": {
    "parent_folder_token": "<TOKEN>",
    "parent_folder_url": "https://my.feishu.cn/drive/folder/<TOKEN>",
    "document_type": "docx",
    "document_id": "<DOC_ID>",
    "document_url": "https://my.feishu.cn/docx/<DOC_ID>",
    "doc_format": "markdown",
    "api_version": "v2",
    "first_published_at": "<ISO_TIME>",
    "last_published_at": "<ISO_TIME>"
  },
  "notes": [
    "Do not create a duplicate child folder named after the project inside parent_folder_token.",
    "On next publish, prefer `lark-cli docs +update --doc <document_id>` over a new create."
  ]
}
```

### A.6 Validation after publish

After every publish, re-list the parent folder and confirm:

- Exactly one new entry was added (no duplicate folders, no orphan empty folders).
- The new document title is what the user expected.
- `document_url` opens correctly.

---

## Implementation B — Python tenant-token (legacy)

Use when the user explicitly wants app/tenant identity, CI execution, or a self-built Feishu app workflow.

### B.0 Modes

| Mode | Command | Behavior | When to use |
| --- | --- | --- | --- |
| **publish (default)** | `python publish.py <md_file>` | Calls Feishu import API, creates a new doc, preserves Markdown formatting | First publish, URL stability not required |
| **replace** | `python publish.py <md_file> --replace <doc_id>` | Clears target doc blocks then writes new content | Preserve existing URL (already shared) |

### B.1 Credentials (one-time)

`%USERPROFILE%\.feishu-credentials.json`:

```json
{
  "app_id": "cli_xxxxxxxxxxxxxx",
  "app_secret": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "default_doc_id": "PBkudACpfomQhfxTLfGcyLylnwe",
  "default_folder_token": ""
}
```

If missing, point the user to `references/feishu-setup.md` to create a Feishu self-built app and grant scopes.

### B.2 Push commands

```bash
# Publish (new doc)
python skills/meta/feishu-publish/scripts/publish.py docs/clash-guide.md

# Replace (preserve URL)
python skills/meta/feishu-publish/scripts/publish.py docs/clash-guide.md --replace PBkudACpfomQhfxTLfGcyLylnwe

# Custom title
python skills/meta/feishu-publish/scripts/publish.py docs/clash-guide.md --name "Clash 配置指南"

# Push into specific folder
python skills/meta/feishu-publish/scripts/publish.py docs/clash-guide.md --folder <folder_token>
```

### 判断成功

成功输出：

```
✓ 已发布: https://xxx.feishu.cn/docx/yyy
  标题: clash-guide
  字数: 1842
```

失败输出（按错误类型分类）：

```
✗ 凭证缺失: 找不到 ~/.feishu-credentials.json
  → 见 references/feishu-setup.md 创建飞书自建应用
```

## 实现要点

### 凭证加载（lib_feishu.py）

按优先级查找：

1. 命令行参数 `--app-id` / `--app-secret`
2. 环境变量 `FEISHU_APP_ID` / `FEISHU_APP_SECRET`
3. `%USERPROFILE%\.feishu-credentials.json`
4. 项目根 `.feishu-credentials.json`（gitignored）

找不到 → 报错并提示创建。

### Token 缓存

`tenant_access_token` 有效期 2 小时。缓存到 `%TEMP%\feishu-token.json`，到期前 5 分钟自动刷新。

### Markdown 渲染保真度

import API 是飞书官方提供的，渲染质量最好（标题、表格、代码块、列表全保留）。

不要自己写 markdown→block 转换器（除非 replace 模式必须）。

### Replace 模式的取舍

`--replace` 模式技术上：
1. 调用 `import` API 创建临时文档（拿到完美渲染）
2. 用 docx blocks API 把临时文档的 blocks 复制到目标文档
3. 删除临时文档

这样既保 URL，又拿到 import 的完美格式。

或者更暴力：删目标文档所有 block + 用临时 doc 的 blocks 覆盖。

## 错误处理

| 错误码 | 原因 | 提示 |
| --- | --- | --- |
| 99991668 | tenant_access_token 失效 | 自动重新获取 |
| 99991663 | app_secret 错误 | 提示用户检查凭证 |
| 1061002 | 应用没权限操作此文档 | 提示用户在文档里把应用加为协作者 |
| 99991672 | 应用未发布 | 提示用户在飞书开放平台「版本管理与发布」点发布 |

## 参考

- API 速查：`references/feishu-api-cheatsheet.md`
- 飞书应用创建：`references/feishu-setup.md`
- 飞书官方文档：https://open.feishu.cn/document/server-docs/docs/docs-overview
