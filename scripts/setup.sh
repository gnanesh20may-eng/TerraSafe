#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

if ! command -v python3.11 >/dev/null 2>&1; then
  echo "Python 3.11 is required (python3.11 was not found)." >&2
  exit 1
fi

if [[ ! -x .venv/bin/python ]]; then
  python3.11 -m venv .venv
fi

if [[ "${1:-}" != "--skip-install" ]]; then
  .venv/bin/python -m pip install -r requirements.txt
fi

echo "Setup complete. Activate with: source .venv/bin/activate"
