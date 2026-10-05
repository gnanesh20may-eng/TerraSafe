from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import httpx
import yaml

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data_sources" / "registry.yaml"
MAX_BYTES = 200 * 1024 * 1024
REGION_BOUNDS: dict[str, tuple[float, float, float, float]] = {
    "nilgiris": (76.2, 11.0, 77.0, 11.7),
    "kerala_western_ghats": (74.8, 8.1, 77.8, 12.9),
    "kodagu": (75.3, 12.0, 76.2, 12.8),
    "maharashtra_western_ghats": (72.5, 15.5, 75.0, 19.0),
    "uttarakhand": (77.5, 28.4, 81.0, 31.5),
    "himachal": (75.5, 30.3, 79.0, 33.3),
    "sikkim_darjeeling": (87.5, 26.8, 89.0, 28.2),
    "arunachal": (91.5, 26.5, 97.5, 29.5),
    "mizoram_meghalaya_nagaland": (89.5, 21.5, 96.5, 27.8),
    "jammu_kashmir_ladakh": (73.5, 32.0, 80.5, 37.0),
}
SUPPORTED = {"open_meteo_archive", "usgs_earthquakes"}


def configure_logging() -> None:
    log_dir = ROOT / "logs"
    log_dir.mkdir(exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[logging.FileHandler(log_dir / "download_all.log", encoding="utf-8"), logging.StreamHandler()],
    )


def build_request(source_id: str, region: str, now: datetime | None = None) -> tuple[str, dict[str, Any]]:
    if region not in REGION_BOUNDS:
        raise ValueError(f"Unknown region '{region}'. Choose from: {', '.join(REGION_BOUNDS)}")
    west, south, east, north = REGION_BOUNDS[region]
    latitude = round((south + north) / 2, 5)
    longitude = round((west + east) / 2, 5)
    now = now or datetime.now(timezone.utc)
    if source_id == "open_meteo_archive":
        end = now.date() - timedelta(days=7)
        start = end - timedelta(days=6)
        return "https://archive-api.open-meteo.com/v1/archive", {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "hourly": "precipitation,soil_moisture_0_to_7cm",
            "timezone": "UTC",
        }
    if source_id == "usgs_earthquakes":
        return "https://earthquake.usgs.gov/fdsnws/event/1/query", {
            "format": "geojson",
            "starttime": (now - timedelta(days=30)).date().isoformat(),
            "endtime": now.date().isoformat(),
            "minlatitude": south,
            "maxlatitude": north,
            "minlongitude": west,
            "maxlongitude": east,
            "limit": 2000,
            "orderby": "time-asc",
        }
    raise ValueError(f"No verified open downloader for source '{source_id}'")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def _write_mock(path: Path, source_id: str, region: str) -> None:
    payload = {
        "synthetic": True,
        "status": "MOCK ONLY - not observed source data",
        "source": source_id,
        "region": region,
        "features": [],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    path.with_suffix(path.suffix + ".sha256").write_text(f"{_sha256(path)}  {path.name}\n", encoding="ascii")


def download(
    source_id: str,
    region: str,
    output: Path,
    *,
    dry_run: bool = False,
    resume: bool = False,
    mock: bool = False,
    timeout: float = 20.0,
    retries: int = 3,
) -> dict[str, Any]:
    url, params = build_request(source_id, region)
    output = output.with_suffix(".mock.json") if mock else output.with_suffix(".json")
    if mock:
        _write_mock(output, source_id, region)
        return {"source": source_id, "path": _display_path(output), "mock": True, "bytes": output.stat().st_size, "sha256": _sha256(output)}
    if dry_run:
        return {"source": source_id, "url": url, "params": params, "output": _display_path(output), "dry_run": True}

    output.parent.mkdir(parents=True, exist_ok=True)
    partial = output.with_suffix(output.suffix + ".part")
    for attempt in range(retries):
        existing = partial.stat().st_size if resume and partial.exists() else 0
        headers = {"Range": f"bytes={existing}-"} if existing else {}
        try:
            with httpx.Client(timeout=timeout, follow_redirects=True) as client:
                with client.stream("GET", url, params=params, headers=headers) as response:
                    response.raise_for_status()
                    if response.status_code == 206 and existing:
                        mode = "ab"
                    else:
                        mode = "wb"
                        existing = 0
                    content_length = response.headers.get("content-length")
                    if content_length and existing + int(content_length) > MAX_BYTES:
                        raise ValueError(f"download exceeds {MAX_BYTES} byte safety limit")
                    downloaded = existing
                    with partial.open(mode) as target:
                        for chunk in response.iter_bytes(64 * 1024):
                            downloaded += len(chunk)
                            if downloaded > MAX_BYTES:
                                raise ValueError(f"download exceeds {MAX_BYTES} byte safety limit")
                            target.write(chunk)
            os.replace(partial, output)
            checksum = _sha256(output)
            output.with_suffix(output.suffix + ".sha256").write_text(f"{checksum}  {output.name}\n", encoding="ascii")
            return {"source": source_id, "path": _display_path(output), "mock": False, "bytes": output.stat().st_size, "sha256": checksum}
        except (httpx.HTTPError, OSError, ValueError) as exc:
            logging.warning("%s attempt %s/%s failed: %s", source_id, attempt + 1, retries, exc)
            if attempt + 1 == retries:
                raise
            time.sleep(2**attempt)
    raise RuntimeError("download retry loop exhausted")


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch bounded open data sources for a selected region.")
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument("--source", action="append", help="Verified source id; repeatable")
    selection.add_argument("--all", action="store_true", help="Download all supported sources marked ready")
    parser.add_argument("--region", choices=sorted(REGION_BOUNDS), default="nilgiris")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--mock", action="store_true")
    parser.add_argument("--timeout", type=float, default=20.0)
    args = parser.parse_args()
    configure_logging()
    registry = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
    entries = {entry["id"]: entry for entry in registry["sources"]}
    selected = sorted(SUPPORTED) if args.all else args.source
    failed = False
    for source_id in selected:
        entry = entries.get(source_id)
        if not entry:
            logging.error("unknown source id: %s", source_id)
            failed = True
            continue
        if source_id not in SUPPORTED or entry.get("status") != "ready":
            logging.error("%s is not an implemented, verified open source; status=%s", source_id, entry.get("status"))
            failed = True
            continue
        output_base = ROOT / "data" / "raw" / args.region / source_id
        try:
            result = download(source_id, args.region, output_base, dry_run=args.dry_run, resume=args.resume, mock=args.mock, timeout=args.timeout)
            logging.info("%s", json.dumps(result, sort_keys=True))
        except (httpx.HTTPError, OSError, ValueError) as exc:
            logging.error("%s failed: %s", source_id, exc)
            failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())