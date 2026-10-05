from __future__ import annotations

from datetime import datetime
import math
from typing import Any

import pandas as pd


def validate_point_table(
    frame: pd.DataFrame,
    *,
    latitude: str = "latitude",
    longitude: str = "longitude",
    label: str | None = None,
    spatial_block: str | None = None,
    crs: str = "EPSG:4326",
) -> dict[str, Any]:
    required = {latitude, longitude}
    if label:
        required.add(label)
    if spatial_block:
        required.add(spatial_block)
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"missing required columns: {', '.join(sorted(missing))}")

    coordinate_rows = frame[[latitude, longitude]]
    coordinate_nulls = int(coordinate_rows.isna().any(axis=1).sum())
    valid = coordinate_rows.dropna()
    out_of_range = int(
        ((valid[latitude] < -90) | (valid[latitude] > 90) |
         (valid[longitude] < -180) | (valid[longitude] > 180)).sum()
    )
    duplicate_coordinates = int(frame.duplicated([latitude, longitude]).sum())
    label_balance = None
    if label:
        label_balance = {
            str(key): int(value)
            for key, value in frame[label].value_counts(dropna=False).sort_index().items()
        }
    return {
        "rows": int(len(frame)),
        "coordinate_null_rows": coordinate_nulls,
        "out_of_range_coordinates": out_of_range,
        "duplicate_coordinates": duplicate_coordinates,
        "label_balance": label_balance,
        "crs": crs,
        "crs_valid": crs.upper().replace(" ", "") in {"EPSG:4326", "OGC:CRS84"},
    }


def validate_hourly_series(times: list[str], fields: dict[str, list[Any]]) -> dict[str, Any]:
    parsed_times = []
    invalid_times = 0
    for value in times:
        try:
            parsed_times.append(datetime.fromisoformat(value.replace("Z", "+00:00")))
        except (AttributeError, TypeError, ValueError):
            invalid_times += 1

    null_counts: dict[str, int] = {}
    invalid_numeric_counts: dict[str, int] = {}
    length_mismatches: list[str] = []
    for name, values in fields.items():
        if len(values) != len(times):
            length_mismatches.append(name)
        null_counts[name] = sum(value is None for value in values)
        invalid_numeric_counts[name] = 0
        for value in values:
            if value is None:
                continue
            try:
                if not math.isfinite(float(value)):
                    invalid_numeric_counts[name] += 1
            except (TypeError, ValueError):
                invalid_numeric_counts[name] += 1

    duplicate_timestamps = len(parsed_times) - len(set(parsed_times))
    ordered = all(left < right for left, right in zip(parsed_times, parsed_times[1:]))
    passed = (
        not invalid_times
        and not length_mismatches
        and duplicate_timestamps == 0
        and ordered
        and not any(null_counts.values())
        and not any(invalid_numeric_counts.values())
    )
    return {
        "rows": len(times),
        "invalid_timestamps": invalid_times,
        "duplicate_timestamps": duplicate_timestamps,
        "strictly_increasing_timestamps": ordered,
        "length_mismatches": length_mismatches,
        "null_counts": null_counts,
        "invalid_numeric_counts": invalid_numeric_counts,
        "passed": passed,
    }


def check_spatial_block_leakage(train_blocks: set[str], test_blocks: set[str]) -> dict[str, Any]:
    overlap = sorted(train_blocks & test_blocks)
    return {"passed": not overlap, "overlap_blocks": overlap}
