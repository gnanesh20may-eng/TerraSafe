from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from time import perf_counter
from typing import Any

import httpx
import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
REGISTRY_PATH = REPO_ROOT / "data_sources" / "registry.yaml"
NILGIRIS_CENTER = (11.35, 76.8)


def _history_dates() -> tuple[str, str]:
    end = datetime.now(timezone.utc).date() - timedelta(days=7)
    start = end - timedelta(days=6)
    return start.isoformat(), end.isoformat()


def _check_open_meteo(source_id: str, timeout: float) -> dict[str, Any]:
    latitude, longitude = NILGIRIS_CENTER
    if source_id == "open_meteo_archive":
        start_date, end_date = _history_dates()
        url = "https://archive-api.open-meteo.com/v1/archive"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": start_date,
            "end_date": end_date,
            "hourly": "precipitation,soil_moisture_0_to_7cm",
            "timezone": "UTC",
        }
    else:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": "precipitation,soil_moisture_0_to_7cm",
            "past_days": 1,
            "forecast_days": 1,
            "timezone": "UTC",
        }
    response = httpx.get(url, params=params, timeout=timeout)
    response.raise_for_status()
    hourly = response.json()["hourly"]
    precipitation = hourly["precipitation"]
    soil_moisture = hourly["soil_moisture_0_to_7cm"]
    times = hourly["time"]
    count = min(len(precipitation), len(soil_moisture), len(times))
    if not count:
        raise ValueError("Open-Meteo returned no hourly records")
    return {"record_count": count, "newest_timestamp": times[count - 1]}


def _check_usgs(timeout: float) -> dict[str, Any]:
    now = datetime.now(timezone.utc)
    response = httpx.get(
        "https://earthquake.usgs.gov/fdsnws/event/1/query",
        params={
            "format": "geojson",
            "starttime": (now - timedelta(days=30)).date().isoformat(),
            "endtime": now.date().isoformat(),
            "minlatitude": 10.8,
            "maxlatitude": 12.0,
            "minlongitude": 76.0,
            "maxlongitude": 77.5,
            "limit": 200,
            "orderby": "time-asc",
        },
        timeout=timeout,
    )
    response.raise_for_status()
    features = response.json().get("features", [])
    newest = max(
        (feature.get("properties", {}).get("time") for feature in features if feature.get("properties", {}).get("time")),
        default=None,
    )
    newest_timestamp = datetime.fromtimestamp(newest / 1000, timezone.utc).isoformat() if newest else None
    return {"record_count": len(features), "newest_timestamp": newest_timestamp}


def check_source(source: dict[str, Any], timeout: float = 5.0) -> dict[str, Any]:
    source_id = source["id"]
    started = perf_counter()
    result: dict[str, Any] = {
        "id": source_id,
        "name": source["name"],
        "category": source["category"],
        "access_type": source["access_type"],
        "status": "NEEDS_REVIEW",
        "latency_ms": None,
        "record_count": None,
        "newest_timestamp": None,
        "error": None,
    }
    try:
        if source_id in {"open_meteo_archive", "open_meteo_forecast"}:
            result.update(_check_open_meteo(source_id, timeout))
            result["status"] = "WORKING"
        elif source_id == "usgs_earthquakes":
            result.update(_check_usgs(timeout))
            result["status"] = "WORKING"
        elif source.get("status") == "needs_review" or source.get("status") in {"missing", "scaffold"}:
            result["status"] = "NEEDS_REVIEW"
        elif source.get("status") == "manual" or source.get("access_type") in {"manual", "login", "api_key"}:
            result["status"] = "MANUAL"
    except (httpx.HTTPError, KeyError, TypeError, ValueError) as exc:
        result["status"] = "FAILED"
        result["error"] = f"{type(exc).__name__}: {exc}"
    finally:
        if result["status"] in {"WORKING", "FAILED"}:
            result["latency_ms"] = round((perf_counter() - started) * 1000, 1)
    return result


def check_all_sources(timeout: float = 5.0, registry_path: Path = REGISTRY_PATH) -> dict[str, Any]:
    registry = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "region": registry.get("region_default", "nilgiris"),
        "sources": [check_source(source, timeout=timeout) for source in registry["sources"]],
    }


def render_markdown_report(report: dict[str, Any]) -> str:
    lines = [
        "# Data Source Health",
        "",
        f"Generated: {report['generated_at']}",
        f"Region: {report['region']}",
        "",
        "Statuses describe endpoint accessibility, not data suitability or operational validation.",
        "",
        "| Source | Category | Status | Latency ms | Records | Newest timestamp | Error |",
        "| --- | --- | --- | ---: | ---: | --- | --- |",
    ]
    for source in report["sources"]:
        error = (source["error"] or "").replace("|", "\\|")
        fields = (
            source["name"], source["category"], source["status"],
            source["latency_ms"] if source["latency_ms"] is not None else "",
            source["record_count"] if source["record_count"] is not None else "",
            source["newest_timestamp"] or "", error,
        )
        lines.append("| " + " | ".join(str(value) for value in fields) + " |")
    return "\n".join(lines) + "\n"