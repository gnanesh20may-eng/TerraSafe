#!/usr/bin/env sh
set -eu
repo_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$repo_root"

if [ ! -x .venv/bin/python ]; then
  python3 -m venv .venv
fi
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt

if [ ! -f .env ] && [ -f .env.example ]; then
  cp .env.example .env
  printf '%s\n' 'Created .env from .env.example; review placeholders before use.'
fi

cd frontend
npm ci
printf '%s\n' 'Setup complete. Next: ../.venv/bin/python -m pytest ../backend/tests -q'
printf '%s\n' 'Start API from repository root: .venv/bin/python -m uvicorn backend.main:app --reload'
printf '%s\n' 'Start UI: cd frontend && npm run dev'