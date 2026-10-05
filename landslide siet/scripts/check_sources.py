from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import logging
from pathlib import Path
import sys
import time
from typing import Any

import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.download_all import build_request, load_registry  # noqa: E402

TIMEOUT = httpx.Timeout(10.0, connect=5.0)


def check_source(source: dict[str, Any], region_id: str, registry: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {
        "id": source["id"], "name": source["name"], "region": region_id,
        "status": "NEEDS_REVIEW", "latency_ms": None, "record_count": None,
        "newest_timestamp": None, "error": None,
    }
    if source.get("status") == "manual":
        result["status"] = "MANUAL"
        result["error"] = "Manual access or permission step required; no request attempted."
        return result
    if source.get("status") != "verified" or not source.get("adapter"):
        result["status"] = "NEEDS_REVIEW"
        result["error"] = "Access endpoint or licence has not been verified; no request attempted."
        return result

    try:
        url, params, _ = build_request(source, region_id, registry)
        started = time.perf_counter()
        response = httpx.get(url, params=params, timeout=TIMEOUT, follow_redirects=True)
        result["latency_ms"] = round((time.perf_counter() - started) * 1000, 1)
        response.raise_for_status()
        payload = response.json()
        if source["adapter"] == "open_meteo_archive":
            times = payload.get("hourly", {}).get("time", [])
            result["record_count"] = len(times)
            result["newest_timestamp"] = times[-1] if times else None
        elif source["adapter"] == "usgs_fdsn":
            features = payload.get("features", [])
            result["record_count"] = len(features)
            if features:
                result["newest_timestamp"] = features[0].get("properties", {}).get("time")
        result["status"] = "WORKING"
    except (httpx.HTTPError, ValueError, KeyError) as error:
        result["status"] = "FAILED"
        result["error"] = f"{type(error).__name__}: {error}"
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Check configured provider status and write the data health report.")
    parser.add_argument("--region", default="nilgiris")
    args = parser.parse_args()
    registry = load_registry()
    if args.region not in registry["regions"]:
        parser.error(f"unknown region {args.region!r}")

    log_dir = ROOT / "logs"
    log_dir.mkdir(exist_ok=True)
    logging.basicConfig(filename=log_dir / "check_sources.log", level=logging.INFO)
    results = [check_source(source, args.region, registry) for source in registry["sources"]]
    report = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "region": args.region,
        "sources": results,
        "summary": {
            status: sum(item["status"] == status for item in results)
            for status in ("WORKING", "MANUAL", "FAILED", "NEEDS_REVIEW")
        },
    }
    (ROOT / "data_sources" / "health.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Data Source Health", "", f"Updated: {report['updated_at']}  ",
        f"Region: `{args.region}` (query bounds are approximate search windows)", "",
        "| Source | Status | Latency (ms) | Records | Newest timestamp | Error / note |",
        "|---|---|---:|---:|---|---|",
    ]
    for item in results:
        note = (item["error"] or "").replace("|", "/")
        lines.append(
            f"| {item['name']} | {item['status']} | {item['latency_ms'] if item['latency_ms'] is not None else '-'} "
            f"| {item['record_count'] if item['record_count'] is not None else '-'} "
            f"| {item['newest_timestamp'] or '-'} | {note} |"
        )
    lines.extend([
        "", "WORKING means the small configured connectivity query succeeded; it does not validate scientific suitability. MANUAL and NEEDS_REVIEW entries were not requested. FAILED means a verified-source request failed during this run.", "",
    ])
    (ROOT / "docs" / "data_health.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(report["summary"], sort_keys=True))
    return 1 if report["summary"]["FAILED"] else 0


if __name__ == "__main__":
    sys.exit(main())
