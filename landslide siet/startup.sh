#!/bin/bash
# startup.sh - Complete startup script for LandSense

set -e  # Exit on error

echo "🚀 Starting LandSense - Explainable AI Landslide Risk System"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python
echo "📦 Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found. Install from https://www.python.org/${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python 3 found$(python3 --version)${NC}"

# Check Node.js
echo "📦 Checking Node.js..."
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js not found. Install from https://nodejs.org/${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Node.js found: $(node --version)${NC}"

# Create backend venv
echo ""
echo "🔧 Setting up Backend..."
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

source .venv/bin/activate 2>/dev/null || . .venv/Scripts/activate 2>/dev/null || true

echo "Installing dependencies..."
pip install -q -r requirements.txt

# Create .env if doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo -e "${YELLOW}⚠ Remember to add real API credentials if not using DEMO_MODE${NC}"
fi

echo -e "${GREEN}✓ Backend ready${NC}"

# Setup frontend
echo ""
echo "🔧 Setting up Frontend..."
cd frontend

if [ ! -d "node_modules" ]; then
    echo "Installing npm dependencies..."
    npm install -q
fi

echo -e "${GREEN}✓ Frontend ready${NC}"
cd ..

# Start servers
echo ""
echo -e "${GREEN}═════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ LandSense is ready to start!${NC}"
echo -e "${GREEN}═════════════════════════════════════════════════════════${NC}"
echo ""
echo "📝 To start both servers, run:"
echo ""
echo -e "${YELLOW}  Terminal 1 (Backend):${NC}"
echo "  source .venv/bin/activate  # Linux/Mac"
echo "  uvicorn backend.main:app --reload"
echo ""
echo -e "${YELLOW}  Terminal 2 (Frontend):${NC}"
echo "  cd frontend"
echo "  npm run dev"
echo ""
echo "Then open: ${GREEN}http://127.0.0.1:5173${NC}"
echo ""
echo "📚 Or read QUICKSTART.md for more details."
echo ""
