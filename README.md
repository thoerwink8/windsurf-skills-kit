# Windsurf Skills Kit

Windsurf IDE 的 Agent Skills 货架——按项目按需挑选，复制到项目中使用。

## 这是什么？

[Windsurf Skills](https://docs.windsurf.com/windsurf/cascade/skills) 是 Windsurf IDE 中 Cascade AI 的能力扩展机制。本仓库是一个**精选货架**，收录了经过验证的通用 Skills、治理规则和工作流。

**设计理念：每个项目独立控制自己的 Skills 组合**——从货架挑选需要的，复制到项目中，不强制全局安装。

## 货架内容

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
| **init-project-skills** | `/init-project-skills` | 分析新项目结构，用 skill-creator 现场生成项目专属 Skills |
| **scan-skills** | `/scan-skills` | 扫描所有已装 Skills，检查重叠/冲突，输出健康度报告 |

## 使用方式

### 1. 克隆货架

```bash
git clone https://github.com/chenxingyu0830/windsurf-skills-kit.git
```

### 2. 为项目按需链接 Skill

**推荐：Junction 链接**（非复制）——源文件只有一份，更新货架后自动生效。

```powershell
# 列出所有可用 Skills
.\add-skill.ps1 list

# 为目标项目链接指定 Skill（按需挑选，不是全装）
.\add-skill.ps1 D:\your-project systematic-debugging
.\add-skill.ps1 D:\your-project skill-creator
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

## 设计理念

```
windsurf-skills-kit（货架，源文件唯一存放地）
  └── skills/ — 精选通用 Skills

项目 A 的 .windsurf/（按需挑选，Junction 链接）
  ├── skills/skill-creator/          → Junction → windsurf-skills-kit/skills/skill-creator/
  ├── skills/systematic-debugging/   → Junction → windsurf-skills-kit/skills/systematic-debugging/
  └── skills/my-project-skill/       ← AI 现场生成（本地文件）

项目 B 的 .windsurf/（不同组合，同一源）
  ├── skills/skill-creator/          → Junction → 同一源
  ├── skills/webapp-testing/         → Junction → 同一源
  └── skills/my-api-skill/           ← AI 现场生成（本地文件）
```

- **每个项目独立挑选**：不同技术栈选不同 Skills，绝不批量推送
- **Junction 而非复制**：源文件只有一份，货架更新自动生效，无版本漂移
- **项目专属 Skills 由 AI 现场生成**：不预设模板，根据项目实际情况定制
- **治理优先**：先检查扩展，再考虑新建，控制 Skill 数量

## 致谢

- [anthropics/skills](https://github.com/anthropics/skills) — Anthropic 官方 Skills
- [obra/superpowers](https://github.com/obra/superpowers) — Jesse Vincent 的开发超能力 Skills
- [Agent Skills 规范](https://agentskills.io/) — 跨 IDE 的 Skills 开放标准
