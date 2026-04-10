---
name: find-skills
description: 从开源 Agent Skills 生态（skills.sh）搜索、评估和安装 skills。当本地图书馆无匹配时，搜索全网开源 skills 作为参考或直接安装。
---

# Find Skills

> 来源：[claudiothebot/find-skills-skill](https://github.com/claudiothebot/find-skills-skill)，适配 Windsurf + 本地图书馆生态。

从开源 agent skills 生态发现和安装 skills：https://skills.sh/

## 搜索

```bash
npx skills find [query]
```

或直接浏览 https://skills.sh/

## 安装到本地图书馆

**推荐流程**：安装到临时目录 → 评估 → 移到图书馆对应分类。

### Step 1: 安装到临时目录

```powershell
$tmp = "$env:TEMP\skill-tmp"
if (Test-Path $tmp) { Remove-Item $tmp -Recurse -Force }
New-Item $tmp -ItemType Directory -Force | Out-Null
Push-Location $tmp
npx skills add <owner/repo@skill-name> -y
Pop-Location
```

### Step 2: 评估质量

读取下载的 SKILL.md，判断：
- 质量是否足够（有具体指导 vs 只有模糊建议）
- 是否适合直接用 vs 作为参考自建更好的

### Step 3: 入库

```powershell
# 移到图书馆对应分类（dev / business / meta）
$category = "dev"  # 按实际选择
Move-Item "$tmp\.agents\skills\<skill-name>" "D:\frank\windsurf-skills-kit\skills\$category\<skill-name>"

# 清理
Remove-Item $tmp -Recurse -Force
```

### Step 4: 验证 frontmatter

确保 SKILL.md 有 `name:` + `description:` frontmatter。不同生态的格式可能不同，需要适配。

## 研究后自建（通常更好）

开源 skills 质量参差不齐。更好的方式：

1. `npx skills find [query]` → 找到相关 skills
2. 下载 top 3，读取 SKILL.md
3. 取其精华 + 补充缺失 + 适配本地工具链
4. 自建 skill 放入图书馆

## 与本地图书馆的关系

```
dao-skill-ecosystem 决策树：
  已装 skills → 本地图书馆(add-skill.ps1 list) → 开源生态(find-skills) → 自建
```

find-skills 是供应链的第三环——本地图书馆无匹配时的外部搜索。
