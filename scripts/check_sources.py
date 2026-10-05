"""Check only supported open Nilgiris endpoints and write observed health."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, timedelta, timezone, datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT))

from backend.app.data_sources import (  # noqa: E402
    HEALTH_PATH,
    HEALTH_STATUSES,
    load_source_registry,
)
from scripts.download_all import REGION_BOUNDS  # noqa: E402

PROBES = {
    "open_meteo_archive",
    "usgs_earthquakes",
}


def probe_url(source_id: str, region: str) -> str:
    """Build a low-volume public endpoint probe using the shared region bounds."""
    if source_id == "open_meteo_archive":
        params = {
            "latitude": 11.35,
            "longitude": 76.7,
            "start_date": (date.today() - timedelta(days=7)).isoformat(),
            "end_date": (date.today() - timedelta(days=1)).isoformat(),
            "hourly": "precipitation",
        }
        return "https://archive-api.open-meteo.com/v1/archive?" + urlencode(params)
    if source_id == "usgs_earthquakes":
        west, south, east, north = REGION_BOUNDS[region]
        params = {
            "format": "geojson",
            "starttime": (datetime.now(timezone.utc) - timedelta(days=1)).date().isoformat(),
            "endtime": datetime.now(timezone.utc).date().isoformat(),
            "minlatitude": south,
            "maxlatitude": north,
            "minlongitude": west,
            "maxlongitude": east,
        }
        return "https://earthquake.usgs.gov/fdsnws/event/1/query?" + urlencode(params)
    raise ValueError(f"no probe is configured for {source_id}")


def check_source(source: dict, region: str) -> dict:
    checked_at = datetime.now(timezone.utc).isoformat()
    source_id = source["id"]
    if source_id not in PROBES:
        status = "MANUAL" if source["access"] in {
            "request_or_portal",
            "institutional",
            "registration",
            "account_and_api",
            "earthdata_account",
            "MAP_KEY",
            "account_required",
        } else "NEEDS_REVIEW"
        return {
            "id": source_id,
            "status": status,
            "checked_at": checked_at,
            "detail": "Not probed: no approved no-login normalizer is implemented.",
        }

    request = Request(
        probe_url(source_id, region),
        headers={"User-Agent": "TerraSafe-source-health/0.1"},
    )
    try:
        with urlopen(request, timeout=5) as response:
            sample = response.read(1024 * 1024 + 1)
            if len(sample) > 1024 * 1024:
                return {
                    "id": source_id,
                    "status": "FAILED",
                    "checked_at": checked_at,
                    "detail": "Probe response exceeded the 1 MiB validation limit.",
                }
            if response.status < 200 or response.status >= 300:
                status = "FAILED"
                detail = f"HTTP {response.status}"
            else:
                try:
                    parsed = json.loads(sample.decode("utf-8"))
                except (UnicodeDecodeError, json.JSONDecodeError):
                    status = "FAILED"
                    detail = "Successful HTTP response was not valid JSON in sampled bytes."
                else:
                    status = "WORKING" if isinstance(parsed, dict) else "FAILED"
                    detail = f"HTTP {response.status}; JSON object response received."
    except HTTPError as exc:
        status = "FAILED"
        detail = f"HTTP {exc.code}"
    except (URLError, TimeoutError, ConnectionError) as exc:
        status = "FAILED"
        detail = f"Network probe failed: {exc}"
    if status not in HEALTH_STATUSES:
        raise RuntimeError(f"unexpected status generated for {source_id}: {status}")
    return {"id": source_id, "status": status, "checked_at": checked_at, "detail": detail}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--region", default="Nilgiris", choices=sorted(REGION_BOUNDS))
    args = parser.parse_args()

    results = [
        check_source(source, args.region) for source in load_source_registry()
    ]
    report = {
        "region": args.region,
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "sources": results,
    }
    HEALTH_PATH.parent.mkdir(parents=True, exist_ok=True)
    HEALTH_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    markdown = [
        "# Data source health",
        "",
        f"Check timestamp (UTC): {report['checked_at']}",
        f"Region: {args.region}",
        "",
        "Status indicates endpoint reachability and sampled response format only; it does not validate scientific fitness, licensing, completeness, or safety.",
        "",
        "| Source | Status | Checked at (UTC) | Detail |",
        "| --- | --- | --- | --- |",
    ]
    for source, result in zip(load_source_registry(), results):
        detail = result["detail"].replace("|", "\\|")
        markdown.append(
            f"| {source['name']} | {result['status']} | {result['checked_at']} | {detail} |"
        )
    markdown.extend(
        [
            "",
            "NASA Earthdata, Copernicus, GSI Bhukosh, and other access-controlled products are MANUAL. Do not use credentials or bypass logins in this checker.",
            "",
            "Only Open-Meteo Archive and USGS earthquake endpoints are probed. No downloaded datasets are committed.",
        ]
    )
    (REPOSITORY_ROOT / "docs" / "data_health.md").write_text(
        "\n".join(markdown) + "\n", encoding="utf-8"
    )
    for result in results:
        print(f"{result['status']} {result['id']}: {result['detail']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
