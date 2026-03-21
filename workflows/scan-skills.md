---
description: 扫描系统中所有已安装的 Skills，检查重叠/冲突，输出健康度报告
---

# Scan Skills — Skills 健康度扫描

## 步骤

1. 扫描 Workspace Skills
// turbo
```bash
Get-ChildItem -Path ".windsurf\skills" -Directory | ForEach-Object { $_.Name }
```

2. 扫描 Global Skills（如果存在）
// turbo
```bash
if (Test-Path "$env:USERPROFILE\.codeium\windsurf\skills") { Get-ChildItem -Path "$env:USERPROFILE\.codeium\windsurf\skills" -Directory | ForEach-Object { "[Global] $($_.Name)" } } else { "Global Skills 目录不存在" }
```

3. 读取每个 Skill 的 SKILL.md，提取 `name` 和 `description` 字段

4. 生成健康度报告，格式如下：

```
## Skills 健康度报告

### 📦 已安装 Skills（共 X 个）

| # | 名称 | 范围 | Description 摘要 |
|---|------|------|-----------------|
| 1 | xxx  | Workspace/Global | xxx |

### ⚠️ 潜在问题

#### Description 重叠
- skill-A 和 skill-B 的触发场景有重叠：...
  → 建议：合并为一个 / 细化 description

#### 从未使用（建议清理）
- skill-X：description 与项目当前阶段不匹配
  → 建议：删除 / 移到 Global

#### 可合并
- skill-A 和 skill-B 经常一起被需要
  → 建议：合并为一个更完整的 Skill

### 📊 总评
- 数量：X 个（健康/偏多/需精简）
- Description 互斥度：高/中/低
- 建议操作：...
```

5. 如果发现问题，调用 `ask_user_question` 询问用户是否要处理

## 注意事项
- 只读扫描，不自动修改任何 Skill
- 重点关注 description 的重叠程度
- 数量 > 15 时主动提醒需要精简
