# Windsurf Skills Kit

Windsurf IDE 的 Agent Skills 货架——按项目按需挑选，复制到项目中使用。

## 这是什么？

[Windsurf Skills](https://docs.windsurf.com/windsurf/cascade/skills) 是 Windsurf IDE 中 Cascade AI 的能力扩展机制。本仓库是一个**精选货架**，收录了经过验证的通用 Skills、治理规则和工作流。

**设计理念：每个项目独立控制自己的 Skills 组合**——从货架挑选需要的，复制到项目中，不强制全局安装。

## 图书馆架构

### 分类原则

本仓库按**域（domain）**分类——这是用户来到货架时脑子里的第一个问题："我要找什么方向的能力？"

从第一性原理推导：

| 候选维度 | 结论 |
|---------|------|
| **按域（domain）** | ✅ 直觉最强，用户想"我要开发/商业相关的" |
| 按功能（function） | ❌ 类别太碎（诊断/分析/生成/路由/测试...） |
| 按来源（source） | ❌ 新来源就要加类别，脆弱 |
| 按受众（audience） | ❌ 与域高度重合，不够精确 |

好的分类必须：**互斥**（无歧义）、**穷尽**（有归属）、**直觉**（能猜到）、**可扩展**（加新内容不破坏结构）。

### 目录结构

```
windsurf-skills-kit/
├── skills/                         ← 按域分类
│   ├── dev/                        ← 开发质量（10 个）
│   ├── business/                   ← 商业诊断（9 个）
│   └── meta/                       ← 元工具（2 个）
├── rules/                          ← 治理规则（暂不分类）
├── workflows/                      ← 工作流（暂不分类）
├── add-skill.ps1                   ← 链接工具
└── README.md
```

**扩展约定**：当 rules 或 workflows 增长到 5+ 时，同样按域分类：

```
rules/
  dev/          ← 开发相关规则
  business/     ← 商业相关规则
  meta/         ← 元治理规则

workflows/
  dev/          ← 开发相关工作流
  business/     ← 商业相关工作流
  meta/         ← 元管理工作流
```

当前仅 1 条规则 + 2 个工作流（全部是 meta 级别），不做过早分类。

---

## 货架内容

### Skills — dev（开发质量，10 个）

| 名称 | 来源 | 用途 |
|------|------|------|
| **brainstorming** | [obra/superpowers](https://github.com/obra/superpowers) | 苏格拉底式设计精炼：通过对话将想法变成完整设计 |
| **database-patterns** | 原创 | 数据库设计与优化：Schema 设计、查询优化、Migration、ORM 模式 |
| **express-typescript-api** | 原创 | Express.js + TypeScript REST API 开发规范 |
| **react-native-expo** | 原创 | Expo React Native TypeScript 开发规范 |
| **security-audit** | 原创 | 安全审计：OWASP Top 10、输入验证、认证授权、密钥管理 |
| **systematic-debugging** | [obra/superpowers](https://github.com/obra/superpowers) | 系统化排查 bug 根因 |
| **test-driven-development** | obra/superpowers | 测试驱动开发 |
| **ui-ux-pro-max** | 原创 | UI/UX 设计系统：67 风格 + 96 配色 + 57 字体 + 99 UX 指南，Python 搜索引擎 |
| **verification-before-completion** | obra/superpowers | 声称完成前自动验证 |
| **webapp-testing** | [anthropics/skills](https://github.com/anthropics/skills) | Playwright 浏览器自动化测试 |

### Skills — business（商业诊断，9 个）

dontbesilent 商业工具箱（[dontbesilent/dbskill](https://github.com/dontbesilent2025/dbskill)）+ 奥派经济聊天室。

| 名称 | 用途 |
|------|------|
| **dbs** | 工具箱主入口，自动路由到最合适的诊断工具 |
| **dbs-diagnosis** | 商业模式诊断（问诊 + 体检两种模式） |
| **dbs-benchmark** | 五重过滤法对标分析 |
| **dbs-content** | 内容创作五维诊断 |
| **dbs-hook** | 短视频开头诊断 + 优化方案生成 |
| **dbs-action** | 阿德勒框架执行力诊断 |
| **dbs-deconstruct** | 维特根斯坦式概念拆解 |
| **chatroom-austrian** | 哈耶克 × 米塞斯 × Claude 奥派经济学多角色讨论 |
| **dbskill-upgrade** | dbs 系列 Skill 升级工具 |

### Skills — meta（元工具，2 个）

| 名称 | 来源 | 用途 |
|------|------|------|
| **find-skills** | [claudiothebot/find-skills-skill](https://github.com/claudiothebot/find-skills-skill) | 从 skills.sh 开源生态搜索、评估和安装 skills |
| **skill-creator** | [anthropics/skills](https://github.com/anthropics/skills) | 元技能：创建、测试、优化新 Skills |

### Rules（1 个）

| 名称 | 作用 |
|------|------|
| **skill_governance** | 新建 Skill 前自动检查是否应扩展已有的，防止 Skill 碎片化 |

### Workflows（2 个）

| 名称 | 触发方式 | 作用 |
|------|---------|------|
| **init-project-skills** | `/init-project-skills` | 分析新项目结构，用 skill-creator 现场生成项目专属 Skills |
| **scan-skills** | `/scan-skills` | 扫描所有已装 Skills，检查重叠/冲突，输出健康度报告 |

---

## 使用方式

### 1. 克隆货架

```bash
git clone https://github.com/chenxingyu0830/windsurf-skills-kit.git
```

### 2. 为项目按需链接 Skill

**推荐：Junction 链接**（非复制）——源文件只有一份，更新货架后自动生效。

```powershell
# 列出所有可用 Skills（按分类显示）
.\add-skill.ps1 list

# 为目标项目链接指定 Skill（只需 skill 名，无需知道分类）
.\add-skill.ps1 D:\your-project systematic-debugging
.\add-skill.ps1 D:\your-project dbs-diagnosis
# ... 只挑项目实际需要的
```

每次只链接一个，避免把不相关的 Skill 带进项目。

### 3. 用 /init-project-skills 生成项目专属 Skills

复制完通用 Skills 后，在 Windsurf 中对 Cascade 说 `/init-project-skills`，AI 会：
1. 分析项目结构、语言、框架
2. 识别项目特有的重复模式
3. 用 skill-creator 现场生成 2-3 个项目专属 Skills

### 4. 定期维护

运行 `/scan-skills` 检查 Skills 健康度：
- 是否有 description 重叠/冲突
- 数量是否过多（建议每项目 ≤ 10 个）
- 是否有从未使用的 Skill 需要清理

---

## 设计理念

### 为什么不做 Sidecar？

Windsurf 支持多 workspace 跨项目聚合 skills（打开 workspace 即自动可见）。但图书馆不适合这个模式：

- **同域多变体**：库中的 skills 可能有 80%+ 功能重叠（如 systematic-debugging vs dao-debug）
- **全播 = 赌博**：AI 靠 description 选 skill，描述相似时选择不可控
- **策展 = 精准**：人挑最合适的 skill 放进项目，消除歧义

对比 windsurf-dao（行为规则 sidecar）：dao 的 skills 各管一个域、无重叠，全播无歧义。图书馆是多品牌同域货架，必须策展。

```
windsurf-skills-kit（货架，源文件唯一存放地）
  └── skills/
      ├── dev/           — 开发质量 Skills
      ├── business/      — 商业诊断 Skills
      └── meta/          — 元工具 Skills

项目 A 的 .windsurf/（按需挑选，Junction 链接）
  ├── skills/skill-creator/          → Junction → windsurf-skills-kit/skills/meta/skill-creator/
  ├── skills/systematic-debugging/   → Junction → windsurf-skills-kit/skills/dev/systematic-debugging/
  └── skills/my-project-skill/       ← AI 现场生成（本地文件）

项目 B 的 .windsurf/（不同组合，同一源）
  ├── skills/dbs/                    → Junction → windsurf-skills-kit/skills/business/dbs/
  ├── skills/dbs-diagnosis/          → Junction → windsurf-skills-kit/skills/business/dbs-diagnosis/
  └── skills/my-api-skill/           ← AI 现场生成（本地文件）
```

- **每个项目独立挑选**：不同技术栈选不同 Skills，绝不批量推送
- **Junction 而非复制**：源文件只有一份，货架更新自动生效，无版本漂移
- **项目专属 Skills 由 AI 现场生成**：不预设模板，根据项目实际情况定制
- **治理优先**：先检查扩展，再考虑新建，控制 Skill 数量

## 致谢

- [anthropics/skills](https://github.com/anthropics/skills) — Anthropic 官方 Skills
- [obra/superpowers](https://github.com/obra/superpowers) — Jesse Vincent 的开发超能力 Skills
- [dontbesilent/dbskill](https://github.com/dontbesilent2025/dbskill) — dontbesilent 商业诊断工具箱
- [Agent Skills 规范](https://agentskills.io/) — 跨 IDE 的 Skills 开放标准
