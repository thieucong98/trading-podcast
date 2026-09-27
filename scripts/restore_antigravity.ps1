<#
.SYNOPSIS
    Antigravity Cross-Machine Session Restorer (PowerShell Native)
.DESCRIPTION
    Restores Antigravity chat sessions, SQLite databases, and brain artifacts
    directly into Windows Antigravity IDE and Antigravity profiles with zero Python prerequisites.
#>

[CmdletBinding()]
param ()

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$SourceAntigravity = Join-Path $ProjectRoot ".antigravity"
$SourceConvs = Join-Path $SourceAntigravity "conversations"
$SourceBrain = Join-Path $SourceAntigravity "brain"
$SourceSummaries = Join-Path $SourceAntigravity "summaries.json"

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "ANTIGRAVITY NATIVE WINDOWS SESSION RESTORER" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "Project Root : $ProjectRoot" -ForegroundColor Gray

if (-not (Test-Path $SourceConvs)) {
    Write-Error "Source conversations directory not found: $SourceConvs"
    exit 1
}

# Identify target Antigravity directories on Windows
$GeminiBase = Join-Path $env:USERPROFILE ".gemini"
$TargetSubDirs = @("antigravity-ide", "antigravity")
$TargetDirs = @()

foreach ($sub in $TargetSubDirs) {
    $targetPath = Join-Path $GeminiBase $sub
    if (Test-Path $targetPath) {
        $TargetDirs += $targetPath
    }
}

# Fallback: if neither exists, create antigravity-ide by default
if ($TargetDirs.Count -eq 0) {
    $TargetDirs += (Join-Path $GeminiBase "antigravity-ide")
}

Write-Host "Found $($TargetDirs.Count) Antigravity target environment(s):" -ForegroundColor Yellow
foreach ($t in $TargetDirs) {
    Write-Host "  -> $t" -ForegroundColor Gray
}

$RestoredSessions = @()

foreach ($target in $TargetDirs) {
    Write-Host "`n[+] Restoring into: $target" -ForegroundColor Green
    $destConv = Join-Path $target "conversations"
    $destBrain = Join-Path $target "brain"

    if (-not (Test-Path $destConv)) { New-Item -ItemType Directory -Path $destConv -Force | Out-Null }
    if (-not (Test-Path $destBrain)) { New-Item -ItemType Directory -Path $destBrain -Force | Out-Null }

    # 1. Copy SQLite Databases
    $dbFiles = Get-ChildItem -Path $SourceConvs -Filter "*.db"
    foreach ($db in $dbFiles) {
        $destFile = Join-Path $destConv $db.Name
        Copy-Item -Path $db.FullName -Destination $destFile -Force
        Write-Host "  [+] Restored session DB: $($db.Name)" -ForegroundColor White
        if ($RestoredSessions -notcontains $db.BaseName) {
            $RestoredSessions += $db.BaseName
        }
    }

    # 2. Copy Brain Artifacts & Transcripts
    if (Test-Path $SourceBrain) {
        $brainDirs = Get-ChildItem -Path $SourceBrain -Directory
        foreach ($bDir in $brainDirs) {
            $destB = Join-Path $destBrain $bDir.Name
            Copy-Item -Path $bDir.FullName -Destination $destB -Recurse -Force
            Write-Host "  [+] Restored brain artifacts: $($bDir.Name)" -ForegroundColor White
        }
    }
}

# Check if Python is available via WSL or native to update SQLite summary DB
$pythonRun = $false
try {
    $wslCheck = Get-Command wsl.exe -ErrorAction SilentlyContinue
    if ($wslCheck) {
        Write-Host "`n[+] Running metadata synchronization via WSL Python..." -ForegroundColor Yellow
        $wslScript = "/mnt/" + ($PSScriptRoot.Replace(":", "").Replace("\", "/")) + "/restore_antigravity.py"
        wsl.exe -d Ubuntu python3 $wslScript 2>$null
        $pythonRun = $true
    }
} catch {
    # Non-fatal if WSL call fails; files are already safely restored
}

Write-Host "`n======================================================================" -ForegroundColor Green
Write-Host "SUCCESS: Antigravity sessions have been restored on this machine!" -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Green
Write-Host "Restored Session IDs:" -ForegroundColor Yellow
foreach ($sid in $RestoredSessions) {
    Write-Host "  - $sid" -ForegroundColor Cyan
    Write-Host "    CLI Resume : agy --resume $sid" -ForegroundColor Gray
}
Write-Host "`nAntigravity IDE:" -ForegroundColor Yellow
Write-Host "  You can now access your restored conversations directly from" -ForegroundColor White
Write-Host "  the Antigravity IDE Chat History / Session Switcher." -ForegroundColor White
Write-Host "======================================================================`n" -ForegroundColor Green
