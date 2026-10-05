"""Bounded, provenance-recording downloader for selected open Nilgiris sources."""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import sys
import time
from datetime import date, timedelta
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT))

from backend.app.data_sources import load_source_registry  # noqa: E402

REGION_BOUNDS = {
    "Nilgiris": (76.0, 11.0, 77.0, 11.75),
    "Kerala Ghats": (74.8, 8.0, 77.5, 13.0),
    "Kodagu": (75.2, 12.0, 76.2, 13.2),
    "Maharashtra Ghats": (72.5, 15.5, 74.5, 20.0),
    "Uttarakhand": (77.5, 28.5, 81.2, 31.5),
    "Himachal": (75.5, 30.2, 79.0, 33.3),
    "Sikkim+Darjeeling": (87.8, 26.5, 89.0, 28.2),
    "Arunachal": (91.5, 26.5, 97.5, 29.5),
    "Mizoram/Meghalaya/Nagaland": (89.5, 21.8, 95.3, 27.5),
    "J&K+Ladakh": (73.5, 32.0, 80.5, 36.0),
}
IMPLEMENTED_SOURCES = {"open_meteo_archive", "usgs_earthquakes"}
MAX_DOWNLOAD_BYTES = 200 * 1024 * 1024
REQUEST_TIMEOUT_SECONDS = 5
MAX_ATTEMPTS = 3
LOGGER = logging.getLogger("terrasafe.download")


def build_request(source_id: str, region: str, start: date, end: date) -> tuple[str, str]:
    """Return the safe endpoint and output extension for an implemented source."""
    if region != "Nilgiris":
        raise ValueError("live downloads are currently enabled only for Nilgiris")
    if start > end:
        raise ValueError("start date must not be after end date")
    west, south, east, north = REGION_BOUNDS[region]
    if source_id == "open_meteo_archive":
        params = {
            "latitude": 11.35,
            "longitude": 76.7,
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "hourly": "precipitation,soil_moisture_0_to_7cm",
            "timezone": "UTC",
        }
        return (
            "https://archive-api.open-meteo.com/v1/archive?"
            + urlencode(params),
            ".json",
        )
    if source_id == "usgs_earthquakes":
        params = {
            "format": "geojson",
            "starttime": start.isoformat(),
            "endtime": end.isoformat(),
            "minlatitude": south,
            "maxlatitude": north,
            "minlongitude": west,
            "maxlongitude": east,
        }
        return (
            "https://earthquake.usgs.gov/fdsnws/event/1/query?"
            + urlencode(params),
            ".geojson",
        )
    raise ValueError(f"{source_id} is not an implemented open source")


def fetch_bounded(url: str, destination: Path, *, resume: bool) -> str:
    """Download at most 200 MiB, retry transient errors, and return SHA-256."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    partial = destination.with_suffix(destination.suffix + ".part")
    existing_size = partial.stat().st_size if resume and partial.exists() else 0
    if not resume and partial.exists():
        partial.unlink()
        existing_size = 0
    for attempt in range(MAX_ATTEMPTS):
        headers = {"User-Agent": "TerraSafe-data-check/0.1 (public-data prototype)"}
        if existing_size:
            headers["Range"] = f"bytes={existing_size}-"
        try:
            request = Request(url, headers=headers)
            with urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
                if existing_size and response.status != 206:
                    existing_size = 0
                    partial.unlink(missing_ok=True)
                declared_length = response.headers.get("Content-Length")
                if declared_length and int(declared_length) + existing_size > MAX_DOWNLOAD_BYTES:
                    raise ValueError("response exceeds the 200 MiB download limit")
                mode = "ab" if existing_size else "wb"
                size = existing_size
                with partial.open(mode) as output:
                    while True:
                        chunk = response.read(64 * 1024)
                        if not chunk:
                            break
                        size += len(chunk)
                        if size > MAX_DOWNLOAD_BYTES:
                            raise ValueError("response exceeds the 200 MiB download limit")
                        output.write(chunk)
            digest = hashlib.sha256()
            with partial.open("rb") as downloaded:
                for chunk in iter(lambda: downloaded.read(64 * 1024), b""):
                    digest.update(chunk)
            os.replace(partial, destination)
            return digest.hexdigest()
        except (HTTPError, URLError, TimeoutError, ConnectionError) as exc:
            if attempt + 1 == MAX_ATTEMPTS:
                raise RuntimeError(f"download failed after {MAX_ATTEMPTS} attempts: {exc}") from exc
            LOGGER.warning("attempt %s failed: %s", attempt + 1, exc)
            time.sleep(0.5 * (2**attempt))
        except ValueError:
            partial.unlink(missing_ok=True)
            raise
    raise RuntimeError("download exited without a result")


def _write_mock(source_id: str, destination: Path) -> str:
    from backend.app.ingest.providers import build_ingestors

    import asyncio

    snapshot = asyncio.run(build_ingestors()[source_id].fetch({"region": "Nilgiris"}))
    payload = {
        "status": "SIMULATED",
        "source_label": snapshot.payload.get("source_label", "MOCK"),
        "mock": True,
        "payload": snapshot.payload,
    }
    destination.parent.mkdir(parents=True, exist_ok=True)
    encoded = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
    destination.write_bytes(encoded)
    return hashlib.sha256(encoded).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument("--source", help="source ID from the registry")
    selection.add_argument("--all", action="store_true", help="select implemented sources only")
    parser.add_argument("--region", default="Nilgiris", choices=sorted(REGION_BOUNDS))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--mock", action="store_true", help="write labeled local fixtures")
    parser.add_argument("--start-date", type=date.fromisoformat)
    parser.add_argument("--end-date", type=date.fromisoformat)
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    source_registry = {source["id"]: source for source in load_source_registry()}
    selected = sorted(IMPLEMENTED_SOURCES) if args.all else [args.source]
    unknown = [source_id for source_id in selected if source_id not in source_registry]
    if unknown:
        parser.error("unknown source ID(s): " + ", ".join(unknown))
    unsupported = [source_id for source_id in selected if source_id not in IMPLEMENTED_SOURCES]
    if unsupported:
        parser.error(
            "no live downloader for: "
            + ", ".join(unsupported)
            + "; see registry status and use a MANUAL step where required"
        )
    if args.region != "Nilgiris" and not args.mock:
        parser.error("live downloads are restricted to Nilgiris in this phase")

    end = args.end_date or (date.today() - timedelta(days=1))
    start = args.start_date or (end - timedelta(days=6))
    if start > end:
        parser.error("--start-date must not be after --end-date")

    for source_id in selected:
        source = source_registry[source_id]
        _, extension = build_request(source_id, args.region, start, end)
        output = REPOSITORY_ROOT / "ml" / "data" / "raw" / args.region / (
            source_id + extension
        )
        if args.dry_run:
            print(
                f"DRY_RUN source={source_id} region={args.region} "
                f"output={output.relative_to(REPOSITORY_ROOT)} "
                f"access={source['access']}"
            )
            continue
        if args.mock:
            checksum = _write_mock(source_id, output)
            print(f"SIMULATED source={source_id} sha256={checksum} output={output}")
            continue
        url, _ = build_request(source_id, args.region, start, end)
        checksum = fetch_bounded(url, output, resume=args.resume)
        manifest: dict[str, Any] = {
            "source_id": source_id,
            "url": url,
            "region": args.region,
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "sha256": checksum,
            "status": "LIVE",
        }
        manifest_path = output.with_suffix(output.suffix + ".manifest.json")
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        print(f"LIVE source={source_id} sha256={checksum} output={output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
