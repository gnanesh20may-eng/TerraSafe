from __future__ import annotations

from typing import Any, Iterable

import pandas as pd


def validate_training_frame(
    frame: pd.DataFrame,
    *,
    crs: str,
    label_column: str = "landslide_label",
    group_column: str = "spatial_block",
) -> dict[str, Any]:
    issues: list[str] = []
    if crs != "EPSG:4326":
        issues.append(f"expected EPSG:4326 coordinates, got {crs}")
    required = {"longitude", "latitude", label_column, group_column}
    missing_columns = sorted(required - set(frame.columns))
    if missing_columns:
        issues.append(f"missing columns: {', '.join(missing_columns)}")
    null_counts = {
        column: int(count)
        for column, count in frame.isna().sum().items()
        if count
    }
    if null_counts:
        issues.append("null values present")
    duplicate_coordinates = 0
    if {"longitude", "latitude"}.issubset(frame.columns):
        duplicate_coordinates = int(frame.duplicated(["longitude", "latitude"]).sum())
        if duplicate_coordinates:
            issues.append("duplicate coordinates present")
    label_balance = (
        {str(label): int(count) for label, count in frame[label_column].value_counts().items()}
        if label_column in frame
        else {}
    )
    if len(label_balance) < 2:
        issues.append("both landslide label classes are required")
    coordinate_bounds_valid = True
    if {"longitude", "latitude"}.issubset(frame.columns):
        coordinate_bounds_valid = bool(
            frame["longitude"].between(-180, 180).all()
            and frame["latitude"].between(-90, 90).all()
        )
        if not coordinate_bounds_valid:
            issues.append("coordinates are outside WGS84 bounds")
    return {
        "status": "PASS" if not issues else "FAIL",
        "rows": int(len(frame)),
        "crs": crs,
        "null_counts": null_counts,
        "duplicate_coordinates": duplicate_coordinates,
        "label_balance": label_balance,
        "spatial_group_count": int(frame[group_column].nunique()) if group_column in frame else 0,
        "coordinate_bounds_valid": coordinate_bounds_valid,
        "issues": issues,
    }


def assert_spatial_groups_disjoint(
    train_groups: Iterable[Any], test_groups: Iterable[Any]
) -> None:
    overlap = set(train_groups).intersection(test_groups)
    if overlap:
        raise ValueError(f"spatial block leakage: {len(overlap)} groups overlap")