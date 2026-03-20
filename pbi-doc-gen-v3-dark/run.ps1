<# 
.SYNOPSIS
    Startet den Power BI Documentation Generator.
.DESCRIPTION
    Wrapper-Skript für Windows PowerShell. Prüft Python-Installation,
    installiert ggf. Abhängigkeiten und startet das Tool.
.EXAMPLE
    .\run.ps1
#>

$ErrorActionPreference = "Stop"

# ── Activate venv if present (check current dir, parent, grandparent) ──
$venvActivate = $null
foreach ($base in @($PSScriptRoot, (Split-Path $PSScriptRoot), (Split-Path (Split-Path $PSScriptRoot)))) {
    $candidate = Join-Path $base ".venv\Scripts\Activate.ps1"
    if (Test-Path $candidate) {
        $venvActivate = $candidate
        break
    }
}
if ($venvActivate) {
    Write-Host "🐍 Aktiviere venv: $venvActivate" -ForegroundColor Cyan
    & $venvActivate
}

# Check Python
$python = $null
foreach ($cmd in @("python3", "python", "py")) {
    try {
        $ver = & $cmd --version 2>&1
        if ($ver -match "Python 3\.(\d+)") {
            $python = $cmd
            Write-Host "✅ Gefunden: $ver" -ForegroundColor Green
            break
        }
    } catch { }
}

if (-not $python) {
    Write-Host "❌ Python 3 nicht gefunden. Bitte installieren: https://www.python.org/downloads/" -ForegroundColor Red
    exit 1
}

Push-Location $PSScriptRoot
try {
    # Install deps if needed
    $reqFile = Join-Path $PSScriptRoot "requirements.txt"
    if (Test-Path $reqFile) {
        Write-Host "📦 Prüfe Abhängigkeiten ..." -ForegroundColor Cyan

        $prevNativeErrPref = $PSNativeCommandUseErrorActionPreference
        $PSNativeCommandUseErrorActionPreference = $false
        & $python -m pip install -r $reqFile --disable-pip-version-check
        $installExitCode = $LASTEXITCODE
        $PSNativeCommandUseErrorActionPreference = $prevNativeErrPref

        if ($installExitCode -ne 0) {
            Write-Host "❌ Abhängigkeiten konnten nicht installiert werden (ExitCode: $installExitCode)." -ForegroundColor Red
            exit $installExitCode
        }
    }

    # Run Web Server
    $port = 5000
    $maxRetries = 5

    # Versuche bestehenden Prozess auf dem Port zu beenden
    for ($i = 0; $i -lt $maxRetries; $i++) {
        $blocked = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue |
                   Where-Object { $_.State -eq "Listen" }
        if (-not $blocked) { break }

        $procId = $blocked.OwningProcess | Select-Object -First 1
        Write-Host "⚠️  Port $port belegt (PID $procId) – beende Prozess ..." -ForegroundColor Yellow
        Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
        Start-Sleep -Milliseconds 500
    }

    # Falls Port immer noch belegt, freien Port suchen
    $blocked = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue |
               Where-Object { $_.State -eq "Listen" }
    if ($blocked) {
        Write-Host "⚠️  Port $port konnte nicht freigegeben werden – suche freien Port ..." -ForegroundColor Yellow
        while ($true) {
            $port++
            $inUse = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue |
                     Where-Object { $_.State -eq "Listen" }
            if (-not $inUse) { break }
            if ($port -gt 5100) {
                Write-Host "❌ Kein freier Port gefunden (5000-5100)." -ForegroundColor Red
                exit 1
            }
        }
        Write-Host "✅ Verwende Port $port" -ForegroundColor Green
    }

    Write-Host ""
    Write-Host "🌐 Starte Web-Server auf Port $port ..." -ForegroundColor Cyan
    & $python run_web.py --port $port
}
finally {
    Pop-Location
}
