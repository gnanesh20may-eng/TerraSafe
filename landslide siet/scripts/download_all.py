from __future__ import annotations

import argparse
from datetime import date, datetime, timedelta, timezone
import hashlib
import json
import logging
from pathlib import Path
import sys
import time
from typing import Any

import httpx
import yaml

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "data_sources" / "registry.yaml"
MAX_DOWNLOAD_BYTES = 200 * 1024 * 1024
TIMEOUT = httpx.Timeout(20.0, connect=8.0)


def load_registry() -> dict[str, Any]:
    with REGISTRY_PATH.open(encoding="utf-8") as registry_file:
        return yaml.safe_load(registry_file)


def build_request(source: dict[str, Any], region_id: str, registry: dict[str, Any]) -> tuple[str, dict[str, Any], str]:
    region = registry["regions"][region_id]
    west, south, east, north = region["bbox"]
    today = datetime.now(timezone.utc).date()
    if source["adapter"] == "open_meteo_archive":
        # Leave a short reanalysis settling period; these are modeled historical estimates, not gauges.
        end_date = today - timedelta(days=6)
        start_date = end_date - timedelta(days=6)
        longitude, latitude = region["point"]
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "hourly": "precipitation,soil_moisture_0_to_7cm",
            "timezone": "UTC",
        }
        label = f"{start_date}_{end_date}"
    elif source["adapter"] == "usgs_fdsn":
        params = {
            "format": "geojson",
            "starttime": (today - timedelta(days=30)).isoformat(),
            "endtime": today.isoformat(),
            "minlatitude": south,
            "maxlatitude": north,
            "minlongitude": west,
            "maxlongitude": east,
            "minmagnitude": 2.5,
            "limit": 2000,
            "orderby": "time",
        }
        label = today.isoformat()
    else:
        raise ValueError(f"No downloader adapter for source {source['id']}")
    return source["url"], params, label


def _log() -> logging.Logger:
    logs_dir = ROOT / "logs"
    logs_dir.mkdir(exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[logging.FileHandler(logs_dir / "download_all.log", encoding="utf-8"), logging.StreamHandler()],
    )
    return logging.getLogger("download_all")


def download(url: str, params: dict[str, Any], destination: Path, resume: bool, logger: logging.Logger) -> str:
    destination.parent.mkdir(parents=True, exist_ok=True)
    partial = destination.with_suffix(destination.suffix + ".part")
    for attempt in range(4):
        offset = partial.stat().st_size if resume and partial.exists() else 0
        headers = {"Range": f"bytes={offset}-"} if offset else {}
        try:
            with httpx.Client(timeout=TIMEOUT, follow_redirects=True) as client:
                with client.stream("GET", url, params=params, headers=headers) as response:
                    if response.status_code in {429, 500, 502, 503, 504}:
                        response.raise_for_status()
                    response.raise_for_status()
                    append = offset > 0 and response.status_code == 206
                    if not append:
                        offset = 0
                    content_length = int(response.headers.get("content-length", "0"))
                    if content_length + offset > MAX_DOWNLOAD_BYTES:
                        raise ValueError("Refusing response larger than 200 MiB")
                    mode = "ab" if append else "wb"
                    written = offset
                    digest_state = hashlib.sha256()
                    if append:
                        with partial.open("rb") as existing:
                            for existing_chunk in iter(lambda: existing.read(64 * 1024), b""):
                                digest_state.update(existing_chunk)
                    with partial.open(mode) as output:
                        for chunk in response.iter_bytes(64 * 1024):
                            written += len(chunk)
                            if written > MAX_DOWNLOAD_BYTES:
                                raise ValueError("Refusing response larger than 200 MiB")
                            output.write(chunk)
                            digest_state.update(chunk)
            digest = digest_state.hexdigest()
            partial.replace(destination)
            destination.with_suffix(destination.suffix + ".sha256").write_text(
                f"{digest}  {destination.name}\n", encoding="ascii"
            )
            logger.info("downloaded %s bytes=%s sha256=%s", destination, written, digest)
            return digest
        except (httpx.HTTPError, OSError) as error:
            if attempt == 3:
                raise
            delay = min(2 ** attempt, 8)
            logger.warning("attempt %s failed: %s; retry in %ss", attempt + 1, error, delay)
            time.sleep(delay)
    raise RuntimeError("unreachable retry state")


def write_mock(source: dict[str, Any], region_id: str, logger: logging.Logger) -> Path:
    destination = ROOT / "data_sources" / "mock" / region_id / f"{source['id']}.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "status": "SIMULATED",
        "synthetic": True,
        "source_id": source["id"],
        "region": region_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "records": [],
    }
    destination.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    logger.info("wrote SIMULATED fixture %s", destination)
    return destination


def main() -> int:
    parser = argparse.ArgumentParser(description="Download bounded, registry-approved environmental data.")
    parser.add_argument("--source", action="append", help="Registry source id; repeat to select several")
    parser.add_argument("--region", default="nilgiris", help="Configured region id (default: nilgiris)")
    parser.add_argument("--all", action="store_true", help="Select all registry sources (unsupported sources are skipped)")
    parser.add_argument("--dry-run", action="store_true", help="Print intended requests without network or file writes")
    parser.add_argument("--resume", action="store_true", help="Resume supported interrupted downloads")
    parser.add_argument("--mock", action="store_true", help="Write SIMULATED fixtures; never call external sources")
    args = parser.parse_args()

    registry = load_registry()
    if args.region not in registry["regions"]:
        parser.error(f"unknown region {args.region!r}; choose from {', '.join(registry['regions'])}")
    sources = registry["sources"]
    if args.all:
        selected = sources
    elif args.source:
        wanted = set(args.source)
        selected = [source for source in sources if source["id"] in wanted]
        found = {source["id"] for source in selected}
        missing = wanted - found
        if missing:
            parser.error(f"unknown source id(s): {', '.join(sorted(missing))}")
    else:
        parser.error("specify --source or --all")

    logger = _log()
    failures = 0
    for source in selected:
        if args.mock:
            write_mock(source, args.region, logger)
            continue
        if source.get("status") != "verified" or source.get("access") != "open" or not source.get("adapter"):
            logger.info("skip %s status=%s access=%s", source["id"], source.get("status"), source.get("access"))
            continue
        try:
            url, params, label = build_request(source, args.region, registry)
            target = source["target_path"].format(region=args.region)
            destination = ROOT / target
            if args.dry_run:
                logger.info("DRY-RUN %s %s params=%s -> %s", source["id"], url, params, destination)
                continue
            digest = download(url, params, destination, args.resume, logger)
            metadata = {
                "status": "WORKING",
                "source_id": source["id"],
                "region": args.region,
                "query_window": label,
                "retrieved_at": datetime.now(timezone.utc).isoformat(),
                "sha256": digest,
                "bytes": destination.stat().st_size,
            }
            destination.with_suffix(destination.suffix + ".metadata.json").write_text(
                json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
            )
        except (httpx.HTTPError, OSError, ValueError) as error:
            failures += 1
            logger.error("failed %s: %s", source["id"], error)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
