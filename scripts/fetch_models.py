"""Fetch a model artifact only after its operator-supplied SHA-256 matches."""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
MODEL_DIRECTORY = REPOSITORY_ROOT / "ml" / "data" / "models"
MAX_MODEL_BYTES = 200 * 1024 * 1024


def fetch_verified(url: str, name: str, expected_sha256: str, destination: Path) -> Path:
    """Download HTTPS bytes to a temporary file and publish after hash validation."""
    if urlparse(url).scheme != "https":
        raise ValueError("model URL must use HTTPS")
    if Path(name).name != name or name in {"", ".", ".."}:
        raise ValueError("model name must be a plain filename")
    if Path(name).suffix.lower() != ".joblib":
        raise ValueError("model artifact must use .joblib")
    if not re.fullmatch(r"[0-9a-fA-F]{64}", expected_sha256):
        raise ValueError("expected_sha256 must be exactly 64 hexadecimal characters")

    destination.mkdir(parents=True, exist_ok=True)
    output = destination / name
    partial = output.with_suffix(output.suffix + ".part")
    request = Request(url, headers={"User-Agent": "TerraSafe-model-fetch/0.1"})
    try:
        with urlopen(request, timeout=5) as response:
            declared_size = response.headers.get("Content-Length")
            if declared_size and int(declared_size) > MAX_MODEL_BYTES:
                raise ValueError("model exceeds the 200 MiB download limit")
            digest = hashlib.sha256()
            size = 0
            with partial.open("wb") as artifact:
                while chunk := response.read(64 * 1024):
                    size += len(chunk)
                    if size > MAX_MODEL_BYTES:
                        raise ValueError("model exceeds the 200 MiB download limit")
                    digest.update(chunk)
                    artifact.write(chunk)
        actual = digest.hexdigest()
        if actual.lower() != expected_sha256.lower():
            raise ValueError(
                f"SHA-256 mismatch: expected {expected_sha256.lower()}, received {actual}"
            )
        os.replace(partial, output)
        output.with_suffix(output.suffix + ".sha256").write_text(
            actual + "\n", encoding="ascii"
        )
        return output
    except (HTTPError, URLError, TimeoutError, ConnectionError) as exc:
        partial.unlink(missing_ok=True)
        raise RuntimeError(f"model download failed: {exc}") from exc
    except ValueError:
        partial.unlink(missing_ok=True)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--sha256", required=True)
    args = parser.parse_args()
    try:
        artifact = fetch_verified(args.url, args.name, args.sha256, MODEL_DIRECTORY)
    except (ValueError, RuntimeError) as exc:
        parser.error(str(exc))
    print(f"VERIFIED sha256={args.sha256.lower()} artifact={artifact}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
