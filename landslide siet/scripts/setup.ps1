$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

if (Test-Path '.venv/Scripts/python.exe') {
    $python = '.venv/Scripts/python.exe'
} else {
    $launcher = Get-Command py -ErrorAction SilentlyContinue
    if ($launcher) {
        & $launcher.Source -3.12 -m venv .venv
        if ($LASTEXITCODE -ne 0) { throw 'Python launcher failed to create .venv.' }
    } else {
        $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
        if (-not $pythonCommand) {
            throw 'Install Python 3.12, then rerun scripts/setup.ps1.'
        }
        & $pythonCommand.Source -m venv .venv
        if ($LASTEXITCODE -ne 0) { throw 'Python failed to create .venv.' }
    }
    $python = '.venv/Scripts/python.exe'
}

& $python -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { throw 'pip upgrade failed.' }
& $python -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw 'Python dependency installation failed.' }

if (-not (Test-Path '.env') -and (Test-Path '.env.example')) {
    Copy-Item '.env.example' '.env'
    Write-Output 'Created .env from .env.example; review placeholders before use.'
}

Push-Location frontend
try {
    npm ci
    if ($LASTEXITCODE -ne 0) { throw 'npm ci failed; stop frontend servers and retry setup.' }
} finally {
    Pop-Location
}

Write-Output 'Setup complete. Next: .\.venv\Scripts\python -m pytest backend/tests -q'
Write-Output 'Start API: .\.venv\Scripts\python -m uvicorn backend.main:app --reload'
Write-Output 'Start UI: cd frontend; npm run dev'