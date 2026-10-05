from pathlib import Path

from typing import Any

BASE_DIR = Path(__file__).resolve().parents[3]


def ensure_backend_bootstrap() -> dict[str, Any]:
    return {
        "project": "TerraSafe",
        "phase": "1",
        "root": str(BASE_DIR),
        "status": "ready",
    }
