---
name: feishu-publish
description: Publish or update a local Markdown file as a Feishu/Lark cloud document with lark-cli user identity. Use this skill whenever the user wants to push a local .md file (README, showcase, project card, design doc, weekly report, knowledge base note) to Feishu, sync local docs to Feishu, update an existing Feishu document from a local file, or share a project artifact via Feishu.
---

# Feishu Publish — Markdown to Feishu Cloud Doc

Publish a local Markdown file (e.g. `docs/showcase/showcase.md`) as a Feishu cloud document, or update an already-published one.

## When to use

Trigger this skill when the user expresses any of these:

- 把 X.md 推到飞书 / 发布到飞书 / 贴到飞书 / 同步到飞书
- "publish to Feishu", "feishu publish", "update Feishu doc"
- After running `showcase-generator`, the user wants the result on Feishu
- Any request to sync local Markdown to a Feishu cloud doc

## Implementation boundary

This skill intentionally keeps only the document publishing path:

- `lark-cli auth login/status` for shared user authentication.
- `lark-cli drive files list` only as a pre-flight check before creating or updating docs.
- `lark-cli docs +create` and `lark-cli docs +update` for Markdown-to-doc publishing.

Do not use calendar, sheet, base, mail, IM, task, OKR, meeting, wiki, slide, whiteboard, or raw OpenAPI skills for this workflow.

---

## lark-cli workflow

### 0. Pre-flight checks (HARD RULES — never skip)

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

### 1. Setup (one-time)

```bash
npx @larksuite/cli@latest install
lark-cli auth login
```

The user completes a browser confirmation. Verify with:

```bash
lark-cli auth status
```

### 2. Resolve target folder

The target folder is identified by `folder_token`, which appears at the end of the Feishu URL:

```text
https://my.feishu.cn/drive/folder/<folder_token>
```

Ask the user for the URL, or read it from `feishu.json` if available.

### 3. List the folder before any write

```powershell
$params = '{\"folder_token\":\"<TOKEN>\"}'
lark-cli drive files list --params $params --as user --format table
```

Inspect the output to:

- Confirm the folder name matches the user's expectation.
- Check whether a same-titled document already exists.
- Detect whether the parent already represents the project.

### 4. Create or update

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

### 5. Persist publication metadata

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

For multiple generated documents, use schema version 2:

```json
{
  "schema_version": 2,
  "project_name": "<NAME>",
  "feishu_parent": {
    "folder_token": "<TOKEN>",
    "folder_url": "https://my.feishu.cn/drive/folder/<TOKEN>"
  },
  "documents": [
    {
      "kind": "showcase",
      "source": "docs/showcase/showcase.md",
      "document_type": "docx",
      "document_id": "<DOC_ID>",
      "document_url": "https://my.feishu.cn/docx/<DOC_ID>",
      "doc_format": "markdown",
      "api_version": "v2",
      "first_published_at": "<ISO_TIME>",
      "last_published_at": "<ISO_TIME>"
    }
  ],
  "notes": [
    "Do not create a duplicate child folder named after the project inside feishu_parent.folder_token.",
    "On next publish, prefer `lark-cli docs +update --doc <document_id>` over a new create."
  ]
}
```

### 6. Validation after publish

After every publish, re-list the parent folder and confirm:

- Exactly one new entry was added (no duplicate folders, no orphan empty folders).
- The new document title is what the user expected.
- `document_url` opens correctly.
