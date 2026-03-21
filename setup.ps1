# Windsurf Global Skills 安装脚本
# 用法: PowerShell -ExecutionPolicy Bypass -File setup-global-skills.ps1
# 功能: 安装通用 Skills + 治理规则 + 扫描工作流到 Global 目录

$ErrorActionPreference = "Stop"
$GlobalDir = "$env:USERPROFILE\.codeium\windsurf"
$TempDir = "$env:TEMP\windsurf-skills-setup"

Write-Host "=== Windsurf Global Skills 安装 ===" -ForegroundColor Cyan

# 1. 创建目录结构
Write-Host "`n[1/4] 创建目录结构..." -ForegroundColor Yellow
@("$GlobalDir\skills", "$GlobalDir\rules", "$GlobalDir\workflows") | ForEach-Object {
    if (!(Test-Path $_)) { New-Item -ItemType Directory -Path $_ -Force | Out-Null }
}

# 2. 下载 anthropics/skills (skill-creator + webapp-testing)
Write-Host "[2/4] 下载 Anthropic 官方 Skills..." -ForegroundColor Yellow
if (Test-Path $TempDir) { Remove-Item $TempDir -Recurse -Force }
git clone --depth 1 --filter=blob:none --sparse "https://github.com/anthropics/skills.git" $TempDir 2>&1 | Out-Null
Push-Location $TempDir
git sparse-checkout set skills/skill-creator skills/webapp-testing 2>&1 | Out-Null
Pop-Location
Copy-Item "$TempDir\skills\skill-creator" "$GlobalDir\skills\skill-creator" -Recurse -Force
Copy-Item "$TempDir\skills\webapp-testing" "$GlobalDir\skills\webapp-testing" -Recurse -Force
Remove-Item $TempDir -Recurse -Force

# 3. 下载 obra/superpowers (debugging + TDD + verification)
Write-Host "[3/4] 下载社区 Skills..." -ForegroundColor Yellow
$TempDir2 = "$env:TEMP\windsurf-skills-setup-2"
if (Test-Path $TempDir2) { Remove-Item $TempDir2 -Recurse -Force }
git clone --depth 1 --filter=blob:none --sparse "https://github.com/obra/superpowers.git" $TempDir2 2>&1 | Out-Null
Push-Location $TempDir2
git sparse-checkout set skills/systematic-debugging skills/test-driven-development skills/verification-before-completion 2>&1 | Out-Null
Pop-Location
Copy-Item "$TempDir2\skills\systematic-debugging" "$GlobalDir\skills\systematic-debugging" -Recurse -Force
Copy-Item "$TempDir2\skills\test-driven-development" "$GlobalDir\skills\test-driven-development" -Recurse -Force
Copy-Item "$TempDir2\skills\verification-before-completion" "$GlobalDir\skills\verification-before-completion" -Recurse -Force
Remove-Item $TempDir2 -Recurse -Force

# 4. 写入治理规则和扫描工作流
Write-Host "[4/4] 安装治理规则和工作流..." -ForegroundColor Yellow

# skill_governance.md
@"
---
trigger: always_on
---

## Skill 治理规则：新建 vs 扩展

当需要创建新的 Skill 时，必须先执行以下检查流程，禁止直接新建。

### 检查流程
1. 列出现有 Skills
2. 匹配判断：
   - 70%+ 重叠 → 必须扩展已有 Skill
   - 30-70% 重叠 → 向用户说明，让用户选择
   - < 30% 重叠 → 可新建，需向用户确认
3. 如果 Workspace Skills >= 10 个，强制提醒合并或清理

### 禁止事项
- 禁止创建只有 1-2 句话的超小 Skill（应该是 Rule）
- 禁止创建与已有 Skill description 高度相似的新 Skill
- 禁止在不告知用户的情况下新建 Skill
"@ | Set-Content "$GlobalDir\rules\skill_governance.md" -Encoding UTF8

# scan-skills.md (workflow)
@"
---
description: 扫描系统中所有已安装的 Skills，检查重叠/冲突，输出健康度报告
---

# Scan Skills

## 步骤
1. 扫描 Workspace Skills: Get-ChildItem .windsurf\skills -Directory
2. 扫描 Global Skills: Get-ChildItem ~\.codeium\windsurf\skills -Directory
3. 读取每个 SKILL.md 的 name + description
4. 检查 description 重叠、数量是否过多
5. 输出健康度报告
"@ | Set-Content "$GlobalDir\workflows\scan-skills.md" -Encoding UTF8

# init-project-skills.md (workflow) - 如果还没安装
if (!(Test-Path "$GlobalDir\workflows\init-project-skills.md")) {
    Write-Host "  init-project-skills.md 已存在，跳过" -ForegroundColor Gray
}

# 完成
Write-Host "`n=== 安装完成 ===" -ForegroundColor Green
Write-Host "Global Skills:" -ForegroundColor Cyan
Get-ChildItem "$GlobalDir\skills" -Directory | ForEach-Object { Write-Host "  - $($_.Name)" }
Write-Host "Global Rules:" -ForegroundColor Cyan
Get-ChildItem "$GlobalDir\rules" -File | ForEach-Object { Write-Host "  - $($_.Name)" }
Write-Host "Global Workflows:" -ForegroundColor Cyan
Get-ChildItem "$GlobalDir\workflows" -File | ForEach-Object { Write-Host "  - $($_.Name)" }
Write-Host "`n下一步: 在新项目中运行 /init-project-skills 生成项目专属 Skills" -ForegroundColor Yellow
