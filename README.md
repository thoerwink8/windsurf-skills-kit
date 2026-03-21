# Windsurf Skills Kit

一键安装 Windsurf IDE 的 AI 协作体系——通用 Skills、治理规则、工作流。

## 这是什么？

[Windsurf Skills](https://docs.windsurf.com/windsurf/cascade/skills) 是 Windsurf IDE 中 Cascade AI 的能力扩展机制。本仓库打包了一套经过筛选的通用 Skills + 治理机制，安装后所有项目自动可用。

## 包含内容

### Skills（5 个）

| 名称 | 来源 | 用途 |
|------|------|------|
| **skill-creator** | [anthropics/skills](https://github.com/anthropics/skills) | 元技能：创建、测试、优化新 Skills |
| **systematic-debugging** | [obra/superpowers](https://github.com/obra/superpowers) | 系统化排查 bug 根因 |
| **test-driven-development** | obra/superpowers | 测试驱动开发 |
| **verification-before-completion** | obra/superpowers | 声称完成前自动验证 |
| **webapp-testing** | anthropics/skills | Playwright 浏览器自动化测试 |

### Rules（1 个）

| 名称 | 作用 |
|------|------|
| **skill_governance** | 新建 Skill 前自动检查是否应扩展已有的，防止 Skill 碎片化 |

### Workflows（2 个）

| 名称 | 触发方式 | 作用 |
|------|---------|------|
| **init-project-skills** | `/init-project-skills` | 分析新项目，用 skill-creator 现场生成项目专属 Skills |
| **scan-skills** | `/scan-skills` | 扫描所有已装 Skills，检查重叠/冲突，输出健康度报告 |

## 安装

### 方式一：一键脚本（推荐）

```powershell
# 克隆仓库
git clone https://github.com/<你的用户名>/windsurf-skills-kit.git
cd windsurf-skills-kit

# 运行安装脚本
PowerShell -ExecutionPolicy Bypass -File setup.ps1
```

### 方式二：手动复制

将以下内容复制到 `~/.codeium/windsurf/` 目录：

```
~/.codeium/windsurf/
├── skills/         ← 复制本仓库的 skills/ 目录
├── rules/          ← 复制本仓库的 rules/ 目录
└── workflows/      ← 复制本仓库的 workflows/ 目录
```

## 使用方式

### 安装后自动生效

- 所有 Skills 在任何项目中自动可用（Global 作用域）
- `skill_governance` 规则 always_on，每次创建新 Skill 时自动触发检查

### 新项目初始化

在新项目目录中对 Cascade 说 `/init-project-skills`，AI 会：
1. 分析项目结构、语言、框架
2. 识别项目特有的重复模式
3. 用 skill-creator 现场生成 2-3 个项目专属 Skills
4. 专属 Skills 保存在项目的 `.windsurf/skills/` 目录（不污染 Global）

### 定期维护

运行 `/scan-skills` 检查 Skills 健康度：
- 是否有 description 重叠/冲突
- 数量是否过多（建议 ≤ 15 个）
- 是否有从未使用的 Skill 需要清理

## 设计理念

```
Global（装一次，所有项目通用）
  └── 通用 Skills + 治理规则 + 工作流

Workspace（每个项目按需生成）
  └── 项目专属 Skills（AI 现场分析，不用模板）
```

- **通用的全局装一次**：调试、TDD、验证等能力跨项目通用
- **专属的让 AI 现场生成**：不预设模板，根据项目实际情况定制
- **治理优先**：先检查扩展，再考虑新建，控制 Skill 数量

## 致谢

- [anthropics/skills](https://github.com/anthropics/skills) — Anthropic 官方 Skills
- [obra/superpowers](https://github.com/obra/superpowers) — Jesse Vincent 的开发超能力 Skills
- [Agent Skills 规范](https://agentskills.io/) — 跨 IDE 的 Skills 开放标准
