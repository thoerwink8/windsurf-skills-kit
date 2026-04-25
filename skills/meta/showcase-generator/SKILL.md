---
name: showcase-generator
description: Generate two paired external-facing project documents from a codebase. Always produces both a showcase (project card for resume / interview / portfolio / Feishu sharing) and a usage guide (a confidence-building user manual that explains every panel button, every shortcut, every status-bar element, and every term the user is actually likely to encounter while using the product—without diving into internal mechanism). Use this skill whenever the user wants to present a code project externally, package a project for recruiters or collaborators, write showcase.md plus usage.md, hand the product to a friend who has never used it, or explain what the visible features and surface-level terms in the product actually mean. Note: this skill does not produce install / build / quick-start instructions, nor deep technical mechanism explanations; those belong in README.md or AGENT_GUIDE / developer docs.
---

# Showcase Generator

Create two paired external-facing documents for an existing codebase:

1. **Project card (`showcase.md`)** — a 30-90 second pitch for recruiters, interviewers, or anyone who wants to know what this project is and why it matters.
2. **User guide (`usage.md`)** — a medium-depth user manual: enough to explain every visible button, shortcut, status indicator, and surface-level term the user will actually encounter, but stops short of internal mechanism. Think "a friend who already knows the product, walking a new user through the panel." Not extremely short, not a deep dictionary.

Both documents are produced by default, in the same run. Do not skip one without explicit user instruction.

## When to use

Use this skill when the user asks for any of these:

- 项目名片 / 项目展示 / 项目介绍 / 简历项目 / 面试项目包装
- 使用说明 / 产品手册 / 功能介绍 / 概念解释 / "用户文档"
- "把这个项目整理成对外文档"
- "解释一下产品里 X 是什么意思"
- "我指定一个目录，你帮我生成项目说明"

Note: do **not** trigger this skill for install / quick-start / build instructions; if the user asks for those, route them to README or a dedicated install guide. After running, the user typically wants to publish results via the `feishu-publish` skill.

## Two paired outputs (always)

| Output | Audience | Tone | Default path |
| --- | --- | --- | --- |
| `showcase.md` | Recruiters, interviewers, friends, investors | Narrative, value-first, highlight-driven | `docs/showcase/showcase.md` |
| `usage.md` | A friend handed the product, who needs to feel confident using every visible feature | Practical, surface-level, term-aware (no internal mechanism) | `docs/showcase/usage.md` |

If `docs/showcase/` already contains either file, read it first and update it instead of overwriting blindly.

## Core principle

Both documents are external-facing. Do not just copy README content. Reframe the project for outside readers.

For `showcase.md`, focus on:

1. **Problem** — what painful problem exists?
2. **Solution** — what system did the project build?
3. **Architecture** — what are the moving parts?
4. **Proof** — what concrete technical depth or measurable result exists?
5. **Visuals** — what screenshots or diagrams make it believable?
6. **Resume value** — what can the user confidently discuss in an interview?

For `usage.md`, focus on what the user **actually sees and touches**:

1. **Open it** — entry point and first impression.
2. **First action** — the smallest meaningful action to start.
3. **Daily use** — what happens once set up.
4. **Buttons / commands** — a row for every panel button and every keyboard shortcut, in plain language. "What it does" + "when to use it".
5. **Status display** — what each piece of the status bar / icon / badge means.
6. **Surface-level terms** — short entries for terms the user actually meets in UI / errors / logs (e.g. for this kind of product: tokens that surface in error messages, named feature classes the panel labels, integrations like proxy/Clash). One short paragraph per term: where you see it, what it is, why it matters. Do **not** explain internal mechanism, formulas, or scoring rules.
7. **Settings** — a small table of the settings the user is most likely to tweak.
8. **Common actions** — condensed "I want → do this" table.
9. **Troubleshooting** — condensed "I see → try this" table, 5-8 entries.

Do **not** include in `usage.md`:

- Installation / build / environment setup commands.
- Architecture diagrams or system internals.
- Internal mechanism explanations (decision algorithms, scoring formulas, scheduling internals, data layouts).
- Exhaustive concept dictionaries that go beyond what a user actually encounters.
- Long FAQ; keep troubleshooting concise.

The litmus test: if a friend just got handed the product, does this document let them use every visible feature confidently and recognise every term they will run into? If yes, ship. If it explains how the system works behind the scenes, cut.

## Workflow

### 1. Identify the target project

If the user did not specify a path, ask for the project directory.

If multiple workspaces are open, choose only when the user’s wording clearly points to one. Otherwise ask.

### 2. Read authoritative files first

Prefer these files, in order:

1. `AGENT_GUIDE.md`, `AGENT.md`, `.windsurf/rules/*`
2. `README.md`, `docs/architecture.md`, `docs/*design*.md`
3. `package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `pom.xml`, etc.
4. `TODO.md`, changelog, evolution logs, design docs
5. Main entry files (`src/`, `server/src/`, `mobile/app/`, etc.) only as needed

Build a mental model before writing:

- product purpose
- users and scenarios
- system boundaries
- technical stack
- core data/control flow
- standout decisions
- operational/deployment story

### 3. Extract resume-grade highlights

Prioritize highlights with one or more of these qualities:

- measurable improvement: latency, cost, reliability, automation, scale
- hard engineering: reverse engineering, concurrency, caching, distributed state, migrations, CI/CD
- product judgment: permissions, privacy, workflow, UX tradeoffs
- full-stack integration: client + server + mobile + deployment
- long-term maintainability: tests, logs, knowledge base, version discipline

Avoid weak highlights:

- “used React”
- “implemented CRUD”
- “has login page”
- “wrote documentation”

### 4. Write output to project docs

Default output paths:

```text
docs/showcase/showcase.md
docs/showcase/usage.md
```

If either file already exists, read it first and update it instead of overwriting blindly. Preserve any user edits that did not come from the skill.

### 5. Document structures

**`showcase.md`** — the project card:

```markdown
# [Project Name] · 项目名片

> [One-sentence positioning]

**项目类型**：...
**核心关键词**：...
**技术栈**：...

---

## 1. 解决的问题

[Problem context and why it matters]

## 2. 系统架构

[Mermaid diagram or ASCII architecture]

## 3. 核心亮点

### 3.1 [Highlight with outcome]

[Problem → solution → concrete effect]

### 3.2 ...

## 4. 面试/简历可讲点

- **[Capability]**：[specific proof]

## 5. 截图补齐清单

| 序号 | 截图 | 用途 |
|---|---|---|
| 1 | ... | ... |

## 6. 对外一句话版本

[One paragraph suitable for Feishu / README / resume]
```

**`usage.md`** — the user guide. Aim for 130-200 lines. Shorter than this means you missed real surface area; much longer means you drifted into developer docs.

```markdown
# [Project Name] · 怎么用

> [One sentence: what does this product do for me?]

---

## 1. 打开
[1-3 lines: where the entry point is and what the user sees first.]

## 2. 加号 / 第一步
[1-4 lines: the smallest meaningful action.]

## 3. 正常用
[A few bullets: what happens once it is set up.]

---

## 4. 面板上的按钮

| 按钮 | 干什么 | 什么时候用 |
|---|---|---|
| ... | ... | ... |

### 快捷键
| 快捷键 | 等价命令 |
|---|---|
| ... | ... |

## 5. 状态栏看什么
[Plain-language list mapping each visible bit (text/color/icon/badge) to its meaning.]

## 6. 你可能会看到的名词
[Only terms the user actually encounters in UI / errors / logs / panel labels. Each gets 1-3 lines: where you see it, what it is, why it matters. Do NOT explain internal mechanism.]

### <Term name>
[Short paragraph: where the user sees it, what it is, why it matters.]

## 7. 设置里能改什么

| 设置 | 默认 | 说明 |
|---|---|---|
| ... | ... | ... |

## 8. 出问题了

| 现象 | 怎么办 |
|---|---|
| ... | ... |

---

> 更深的机制 / 部署 / 架构 看 README 与 AGENT_GUIDE。
```

Writing rules:

- Cover **every** panel button, command, and shortcut the user can reach in the UI. Missing surface area is a defect.
- For surface-level terms: explain only those the user actually meets (in UI labels, error toasts, logs, status indicators). Skip internal-only concepts.
- For each term: "where you see it / what it is / why it matters." That is the depth ceiling. Do not write formulas, decision rules, or scheduling details.
- Use everyday Chinese. Tables for actions and lookups; short paragraphs for term explanations.
- If a paragraph starts explaining the system from the inside out, stop and move it to AGENT_GUIDE.

### 6. Screenshot Capture Phase

After drafting `showcase.md` and `usage.md`, run a four-step capture phase. Capture what is automatable; leave the rest as a precise checklist for the user to fill in.

#### 6.1 Convention

- All screenshots live under `docs/showcase/img/`.
- File names are stable, descriptive, lowercase-kebab-case: `webview-main.png`, `mobile-dashboard.png`, `gh-actions-pipeline.png`.
- The same file name appears in the markdown reference and the todo list, so dropping a file in place fills the slot without further edits.

#### 6.2 Auto-discover existing images

Scan these locations and reuse anything that matches a needed slot:

```text
docs/image/**
docs/showcase/img/**
docs/screenshots/**
mobile/screenshots/**
mobile/dist/**/*.png
src/image/**
.github/assets/**
README assets referenced inline
```

For each match, write or rewrite the image reference in `showcase.md` / `usage.md` to point at it. Mark the slot as resolved in the todo list.

#### 6.3 Try to capture what is automatable

These are the only categories the skill should try to capture without the user's hands. Do not exceed this list.

| Capture target | Tool | When |
| --- | --- | --- |
| Mermaid diagrams in the documents | `mmdc` (mermaid-cli, optional) | Only if `mmdc` is on PATH; otherwise rely on Feishu / GitHub native rendering |
| Public, no-login web pages (project's public GitHub page, public docs site, public dashboards) | `chrome-devtools` MCP | Only if a clearly public URL is in scope |
| CSV / data table preview as a cropped HTML render | rendering script writing to `_tmp/` | Only when the project has a notable data-driven artifact (e.g. a public `evolution-entries.csv`) |

Hard rules:

- Never attempt to log into the user's accounts (GitHub, Feishu, vendor consoles).
- Never start the user's dev server without explicit confirmation.
- Never take operating-system screenshots; the skill cannot capture VSCode UIs, IDE panels, or desktop windows.
- If `chrome-devtools` MCP is not available or required, skip silently.

#### 6.4 Generate `docs/showcase/screenshot-todo.md`

Always produce this file. It is the single source of truth for what is still missing.

```markdown
# 截图补齐清单

每条记录的目标文件名都已在 showcase.md / usage.md 中预留。补图时把文件放到对应路径即可，无需改 markdown。

## 已自动获取

- [x] `docs/showcase/img/<filename>.png` — <来源说明>

## 待你手动补齐

### 1. <截图主题，例如 "Windsurf 侧边栏账号管理面板">

- 用途：showcase §5 / usage §5.X
- 操作：<具体步骤，例如 "在 Windsurf 中点左侧 无感切号 图标，把面板拉宽到 360px">
- 期望内容：<画面里至少要看到什么>
- 目标路径：`docs/showcase/img/webview-main.png`
- 推荐分辨率：1280x800 左右

### 2. ...
```

`screenshot-todo.md` 是用户视角的产物，不要塞进 AI 注释或元信息。每条只写：用途、操作、期望内容、目标路径、分辨率。

#### 6.5 Ensure `docs/showcase/img/` exists

If the directory does not exist, create it with a tiny `README.md` inside:

```markdown
# img/

这个目录只放 showcase / usage 用到的对外截图。
文件名由 `screenshot-todo.md` 指定，对应 markdown 中已写好的引用。
```

This guarantees the user has an obvious place to drop screenshots, with no decision overhead.

### 7. Tone

Use clear, professional Chinese by default.

Write for recruiters/interviewers, not only engineers:

- Start with product value.
- Then explain technical depth.
- Avoid private jokes and excessive internal jargon.
- Keep sensitive credentials, private URLs, account details, and secrets out.

### 8. Feishu/Notion readiness

Make the Markdown portable:

- Use plain headings and tables.
- Use Mermaid for diagrams when helpful.
- Avoid local-only links unless they are clearly marked as repository paths.
- Put screenshots under `docs/showcase/img/`.
- Keep the first screen scannable.

## Validation checklist

Before delivery, verify both documents exist and pass these checks.

`showcase.md`:

- [ ] File exists at `docs/showcase/showcase.md` (or user-specified path).
- [ ] First paragraph explains what the project does without assuming internal context.
- [ ] At least 3 strong technical or product highlights.
- [ ] Architecture section matches actual project structure.
- [ ] Screenshot checklist is concrete.

`usage.md`:

- [ ] File exists at `docs/showcase/usage.md` (or user-specified path).
- [ ] Total length is roughly 130-200 lines (medium depth, not a leaflet, not a textbook).
- [ ] **Every** panel button and keyboard shortcut surfaced in the product is documented at least once.
- [ ] Status bar / icon / badge meanings are listed.
- [ ] At least 4-8 surface-level terms the user will actually encounter (errors, logs, badges, integrations) get a short explanation.
- [ ] Term explanations stay at "where you see it / what it is / why it matters" depth; no formulas, no decision rules.
- [ ] No installation, build, or environment-setup steps.
- [ ] No architecture diagrams or internal mechanism explanations.
- [ ] Settings table covers the settings users most often tweak.
- [ ] Troubleshooting table has 5-8 short entries.

Cross-cutting:

- [ ] No secrets, passwords, tokens, or private account details in either file.
- [ ] No internal-only jokes or jargon that an external reader cannot understand.
- [ ] User has a clear next step: review both files, add screenshots, then run `feishu-publish`.
