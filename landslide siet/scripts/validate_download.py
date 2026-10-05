from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backend.app.ml.data_validation import validate_hourly_series, validate_point_table  # noqa: E402


def validate_file(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if "hourly" in payload:
        hourly = payload["hourly"]
        times = hourly.get("time", [])
        fields = {key: values for key, values in hourly.items() if key != "time"}
        report = validate_hourly_series(times, fields)
        point = validate_point_table(pd.DataFrame({
            "latitude": [payload.get("latitude")],
            "longitude": [payload.get("longitude")],
        }))
        return {"format": "Open-Meteo hourly JSON", "time_series": report, "point": point}

    if payload.get("type") == "FeatureCollection":
        records = []
        for feature in payload.get("features", []):
            geometry = feature.get("geometry") or {}
            if geometry.get("type") == "Point":
                longitude, latitude = geometry["coordinates"][:2]
                records.append({"latitude": latitude, "longitude": longitude})
        frame = pd.DataFrame(records, columns=["latitude", "longitude"])
        return {
            "format": "GeoJSON FeatureCollection",
            "record_count": len(records),
            "point_table": validate_point_table(frame),
        }
    raise ValueError("Unsupported data shape: expected hourly weather JSON or GeoJSON FeatureCollection")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate downloaded environmental observations without changing them.")
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    report = validate_file(args.path)
    print(json.dumps(report, indent=2))
    checks = [report.get("point", {}).get("crs_valid", True)]
    checks.extend(report.get("point", {}).get(key, 0) == 0 for key in ("coordinate_null_rows", "out_of_range_coordinates"))
    checks.append(report.get("time_series", {}).get("passed", True))
    checks.append(report.get("point_table", {}).get("crs_valid", True))
    return 0 if all(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
