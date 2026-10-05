$ErrorActionPreference = 'Stop'
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

if (-not (Test-Path '.venv\Scripts\python.exe')) {
    python -m venv .venv
}
$Python = Join-Path $ProjectRoot '.venv\Scripts\python.exe'
& $Python -m pip install --upgrade pip
& $Python -m pip install -r requirements.txt

if (-not (Test-Path '.env')) {
    Copy-Item '.env.example' '.env'
    Write-Host 'Created .env from .env.example. Review values; do not add secrets to Git.'
}

Push-Location frontend
npm ci
Pop-Location

Write-Host ''
Write-Host 'Setup complete. Next commands:'
Write-Host '  .\.venv\Scripts\python.exe -m uvicorn backend.main:app --reload --port 8000'
Write-Host '  cd frontend; npm run dev'
Write-Host '  .\.venv\Scripts\python.exe -m pytest backend/tests -q'
