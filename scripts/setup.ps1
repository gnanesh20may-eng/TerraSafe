param(
    [switch]$SkipInstall
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

if (-not (Get-Command py -ErrorAction SilentlyContinue)) {
    throw "Python launcher 'py' was not found. Install Python 3.11 or newer."
}

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    py -3.11 -m venv .venv
    if ($LASTEXITCODE -ne 0) {
        throw "Could not create .venv with Python 3.11. Install Python 3.11 or create .venv manually."
    }
}

if (-not $SkipInstall) {
    & ".venv\Scripts\python.exe" -m pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        throw "Dependency installation failed. Review the pip error above."
    }
}

Write-Output "Setup complete. Activate with .\.venv\Scripts\Activate.ps1"
