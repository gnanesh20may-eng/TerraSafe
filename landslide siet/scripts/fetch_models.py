from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlparse

import httpx

ROOT = Path(__file__).resolve().parents[1]
MODELS_DIR = ROOT / "backend" / "models"
MAX_MODEL_BYTES = 200 * 1024 * 1024
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")


def validate_entry(entry: dict) -> tuple[str, str]:
    name = entry.get("name")
    url = entry.get("url")
    digest = entry.get("sha256", "")
    if not isinstance(name, str) or Path(name).name != name or name in {"", ".", ".."}:
        raise ValueError("model name must be a plain filename")
    if not isinstance(url, str) or urlparse(url).scheme != "https":
        raise ValueError("model URL must use HTTPS")
    if not isinstance(digest, str) or not SHA256_PATTERN.fullmatch(digest):
        raise ValueError("model entry must include a lowercase SHA-256 checksum")
    return name, url


def fetch_model(url: str, destination: Path, expected_sha256: str) -> int:
    destination.parent.mkdir(parents=True, exist_ok=True)
    partial = destination.with_suffix(destination.suffix + ".part")
    digest = hashlib.sha256()
    written = 0
    timeout = httpx.Timeout(30.0, connect=10.0)
    try:
        with httpx.Client(timeout=timeout, follow_redirects=True) as client:
            with client.stream("GET", url) as response:
                response.raise_for_status()
                size = int(response.headers.get("content-length", "0"))
                if size > MAX_MODEL_BYTES:
                    raise ValueError("Refusing model larger than 200 MiB")
                with partial.open("wb") as output:
                    for chunk in response.iter_bytes(64 * 1024):
                        written += len(chunk)
                        if written > MAX_MODEL_BYTES:
                            raise ValueError("Refusing model larger than 200 MiB")
                        output.write(chunk)
                        digest.update(chunk)
        if digest.hexdigest() != expected_sha256:
            raise ValueError("downloaded model SHA-256 does not match the manifest")
        partial.replace(destination)
        return written
    except Exception:
        partial.unlink(missing_ok=True)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch model artifacts only after HTTPS and SHA-256 validation.")
    parser.add_argument("--manifest", required=True, type=Path, help="JSON file with a models list (name, url, sha256)")
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    models = manifest.get("models")
    if not isinstance(models, list):
        parser.error("manifest must contain a models array")
    for entry in models:
        try:
            name, url = validate_entry(entry)
            size = fetch_model(url, MODELS_DIR / name, entry["sha256"])
            print(f"VERIFIED {name} bytes={size} sha256={entry['sha256']}")
        except (KeyError, TypeError, ValueError, OSError, httpx.HTTPError) as error:
            print(f"FAILED {entry.get('name', '<unnamed>')}: {error}", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
