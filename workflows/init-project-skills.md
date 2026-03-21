---
description: 为新项目初始化 AI 协作体系：分析项目结构，用 skill-creator 生成项目专属 Skills
---

# Init Project Skills — 新项目 Skills 初始化

在一个新项目中运行此工作流，自动分析项目并生成适合的专属 Skills。

## 前置条件
- Global Skills 已安装（skill-creator、systematic-debugging 等）
- 当前目录是目标项目的根目录

## 步骤

1. 检查 Global Skills 是否就绪
// turbo
```bash
Get-ChildItem -Path "$env:USERPROFILE\.codeium\windsurf\skills" -Directory | ForEach-Object { $_.Name }
```

如果 skill-creator 不存在，提示用户先运行 `/setup-global-skills`。

2. 扫描项目结构，识别核心特征
// turbo
```bash
Get-ChildItem -Recurse -File -Exclude *.pyc,*.pyo | Where-Object { $_.DirectoryName -notmatch '(node_modules|\.git|__pycache__|\.venv|venv|dist|build)' } | Group-Object Extension | Sort-Object Count -Descending | Select-Object Count, Name -First 15
```

3. 识别项目类型和关键模式：
   - **语言/框架**：Python/JS/TS？Django/Flask/React/Streamlit？
   - **数据层**：SQLite/Postgres/MongoDB？ORM？
   - **前端**：有 Dashboard/Web UI 吗？用什么框架？
   - **开发流程**：有 feature_backlog.json？有 TODO 管理？有 CI/CD？
   - **测试**：有测试文件吗？用什么测试框架？

4. 读取 README.md（如果存在），理解项目定位

5. 基于分析结果，判断需要哪些项目专属 Skills（通常 2-3 个）。常见模式：
   - 有 feature_backlog.json → 需要"需求开发"Skill
   - 有 Dashboard/Web UI → 需要"UI 开发"Skill
   - 有数据管道（采集→存储→分析） → 需要"管道开发"Skill
   - 有 API 服务 → 需要"API 开发"Skill

6. 向用户展示推荐的 Skills 列表，确认后用 `@skill-creator` 逐个创建

7. 创建 `.windsurf/skills/<name>/SKILL.md`，每个 Skill 的 description 必须：
   - 包含项目的具体模块名和文件路径
   - 与已有 Skills 的 description 互斥
   - 足够"pushy"以确保自动触发

8. 运行 `/scan-skills` 验证无冲突

## 注意事项
- 每个项目的专属 Skills 控制在 2-5 个
- 通用能力（调试、TDD、验证）由 Global Skills 覆盖，不要重复创建
- 遵循 skill_governance 规则：新建前检查是否可以扩展已有的
