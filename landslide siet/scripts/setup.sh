#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

if [[ ! -x .venv/bin/python ]]; then
  python3 -m venv .venv
fi
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt

if [[ ! -f .env ]]; then
  cp .env.example .env
  printf '%s\n' 'Created .env from .env.example. Review values; do not add secrets to Git.'
fi

npm --prefix frontend ci

cat <<'NEXT'
Setup complete. Next commands:
  .venv/bin/python -m uvicorn backend.main:app --reload --port 8000
  cd frontend && npm run dev
  .venv/bin/python -m pytest backend/tests -q
NEXT
