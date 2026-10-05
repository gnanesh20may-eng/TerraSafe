#!/bin/bash
# startup.ps1 - Complete startup script for LandSense (PowerShell)

Write-Host "🚀 Starting LandSense - Explainable AI Landslide Risk System" -ForegroundColor Green
Write-Host ""

# Check Python
Write-Host "📦 Checking Python..." -ForegroundColor Yellow
if (-not (Get-Command python3 -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Python 3 not found. Install from https://www.python.org/" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Python 3 found: $(python3 --version)" -ForegroundColor Green

# Check Node.js
Write-Host "📦 Checking Node.js..." -ForegroundColor Yellow
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Node.js not found. Install from https://nodejs.org/" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Node.js found: $(node --version)" -ForegroundColor Green

# Create backend venv
Write-Host ""
Write-Host "🔧 Setting up Backend..." -ForegroundColor Yellow
if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment..."
    python3 -m venv .venv
}

.venv\Scripts\Activate.ps1

Write-Host "Installing dependencies..."
pip install -q -r requirements.txt

# Create .env if doesn't exist
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env file..."
    Copy-Item .env.example .env
    Write-Host "⚠ Remember to add real API credentials if not using DEMO_MODE" -ForegroundColor Yellow
}

Write-Host "✓ Backend ready" -ForegroundColor Green

# Setup frontend
Write-Host ""
Write-Host "🔧 Setting up Frontend..." -ForegroundColor Yellow
cd frontend

if (-not (Test-Path "node_modules")) {
    Write-Host "Installing npm dependencies..."
    npm install -q
}

Write-Host "✓ Frontend ready" -ForegroundColor Green
cd ..

# Start servers
Write-Host ""
Write-Host "═════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "✅ LandSense is ready to start!" -ForegroundColor Green
Write-Host "═════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host ""
Write-Host "📝 To start both servers, run:"
Write-Host ""
Write-Host "Terminal 1 (Backend):" -ForegroundColor Yellow
Write-Host ".venv\Scripts\Activate.ps1"
Write-Host "uvicorn backend.main:app --reload"
Write-Host ""
Write-Host "Terminal 2 (Frontend):" -ForegroundColor Yellow
Write-Host "cd frontend"
Write-Host "npm run dev"
Write-Host ""
Write-Host "Then open: http://127.0.0.1:5173" -ForegroundColor Green
Write-Host ""
Write-Host "📚 Or read QUICKSTART.md for more details."
Write-Host ""
