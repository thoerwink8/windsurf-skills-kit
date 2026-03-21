---
trigger: always_on
---

## Skill 治理规则：新建 vs 扩展

当需要创建新的 Skill 时（无论是用户主动要求还是 AI 判断需要），**必须先执行以下检查流程**，禁止直接新建。

### 检查流程

1. **列出现有 Skills**：扫描 `.windsurf/skills/` 和 `~/.codeium/windsurf/skills/` 中所有 Skill 的 name + description
2. **匹配判断**：新需求是否属于某个已有 Skill 的领域范围？
   - 如果 **70%+ 内容重叠** → **必须扩展已有 Skill**（在其 SKILL.md 中新增章节）
   - 如果 **30-70% 重叠** → 向用户说明两个选项，让用户选择：扩展 vs 新建
   - 如果 **< 30% 重叠**（确实是全新领域） → 可以新建，但需向用户确认
3. **数量检查**：如果 Workspace Skills 已 ≥ 10 个，强制提醒用户考虑合并或清理

### 扩展已有 Skill 时
- 在 SKILL.md 末尾或相关章节下新增内容
- 不修改现有内容的语义
- 如果需要新的资源文件，放在同一个 Skill 文件夹内

### 新建 Skill 时
- 必须说明为什么不能归入已有 Skill
- Description 必须与所有已有 Skill 的 description 互斥
- 优先放 Workspace 级别，除非确认是跨项目通用的

### 禁止事项
- 禁止创建只有 1-2 句话的超小 Skill（应该是 Rule 而非 Skill）
- 禁止创建与已有 Skill description 高度相似的新 Skill
- 禁止在不告知用户的情况下新建 Skill
