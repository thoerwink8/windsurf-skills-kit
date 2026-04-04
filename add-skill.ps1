# add-skill.ps1 — 按需将单个 Skill 链接到目标项目
#
# Usage:
#   .\add-skill.ps1 <project-path> <skill-name>
#   .\add-skill.ps1 list                          列出所有可用 Skills
#
# Skills 按域分类存放在 skills/<category>/<skill-name>/ 下，
# 但用户只需提供 skill-name，脚本自动在所有分类中查找。
#
# 示例:
#   .\add-skill.ps1 D:\frank\myproject systematic-debugging
#   .\add-skill.ps1 D:\frank\myproject dbs-diagnosis

param(
    [Parameter(Position=0)] [string]$Arg1,
    [Parameter(Position=1)] [string]$SkillName
)

$KitRoot   = $PSScriptRoot
$KitSkills = Join-Path $KitRoot "skills"

# --- Helper: find a skill directory by name across all categories ---
function Find-Skill {
    param([string]$Name)
    foreach ($category in (Get-ChildItem $KitSkills -Directory)) {
        $candidate = Join-Path $category.FullName $Name
        if (Test-Path $candidate) { return $candidate }
    }
    return $null
}

# --- List mode ---
if ($Arg1 -eq "list" -or !$Arg1) {
    Write-Host "`n  Available skills in windsurf-skills-kit:" -ForegroundColor Cyan
    foreach ($category in (Get-ChildItem $KitSkills -Directory | Sort-Object Name)) {
        Write-Host "`n  [$($category.Name)]" -ForegroundColor Yellow
        Get-ChildItem $category.FullName -Directory | ForEach-Object {
            $desc = ""
            $skill = Join-Path $_.FullName "SKILL.md"
            if (Test-Path $skill) {
                $line = Get-Content $skill | Where-Object { $_ -match "^description:" } | Select-Object -First 1
                if ($line) { $desc = $line -replace "^description:\s*", "" }
            }
            Write-Host "    $($_.Name)" -ForegroundColor Green -NoNewline
            if ($desc) { Write-Host " — $desc" -ForegroundColor Gray } else { Write-Host "" }
        }
    }
    Write-Host "`n  Usage: .\add-skill.ps1 <project-path> <skill-name>`n"
    exit 0
}

# --- Link mode ---
$ProjectPath = $Arg1

if (!$SkillName) {
    Write-Host "  [error] Usage: .\add-skill.ps1 <project-path> <skill-name>" -ForegroundColor Red
    Write-Host "          Run '.\add-skill.ps1 list' to see available skills."
    exit 1
}

$srcSkill = Find-Skill $SkillName
if (!$srcSkill) {
    Write-Host "  [error] Skill '$SkillName' not found. Run '.\add-skill.ps1 list' to see available skills." -ForegroundColor Red
    exit 1
}

if (!(Test-Path $ProjectPath)) {
    Write-Host "  [error] Project path not found: $ProjectPath" -ForegroundColor Red
    exit 1
}
$ProjectPath = (Resolve-Path $ProjectPath).Path

$destDir   = Join-Path $ProjectPath ".windsurf\skills"
$destSkill = Join-Path $destDir $SkillName

if (!(Test-Path $destDir)) {
    New-Item -ItemType Directory -Path $destDir -Force | Out-Null
}

if (Test-Path $destSkill) {
    $item = Get-Item $destSkill
    if ($item.LinkType -eq "Junction") {
        Write-Host "  [skip] '$SkillName' already linked in $ProjectPath" -ForegroundColor DarkGray
    } else {
        Write-Host "  [warn] '$SkillName' exists as a real directory. Remove it manually first if you want to link." -ForegroundColor Yellow
    }
    exit 0
}

New-Item -ItemType Junction -Path $destSkill -Target $srcSkill | Out-Null
Write-Host "  [link] $SkillName -> $srcSkill" -ForegroundColor Green
Write-Host "         in: $destDir"
