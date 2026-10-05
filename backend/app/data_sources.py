"""Source registry access and data-quality checks."""

from __future__ import annotations

import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping

import yaml

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = REPOSITORY_ROOT / "data_sources" / "registry.yaml"
HEALTH_PATH = REPOSITORY_ROOT / "ml" / "data" / "health" / "source_health.json"
REGISTRY_FIELDS = {
    "id",
    "name",
    "category",
    "url",
    "access",
    "format",
    "licence",
    "region",
    "fallback",
    "path",
    "status",
}
HEALTH_STATUSES = {"WORKING", "MANUAL", "FAILED", "NEEDS_REVIEW"}


def load_source_registry(path: Path = REGISTRY_PATH) -> list[dict[str, Any]]:
    """Load and validate the source catalogue without network access."""
    with path.open(encoding="utf-8") as source_file:
        registry = yaml.safe_load(source_file)
    if not isinstance(registry, dict) or not isinstance(registry.get("sources"), list):
        raise ValueError("source registry must contain a sources list")
    sources = registry["sources"]
    identifiers: set[str] = set()
    for index, source in enumerate(sources):
        if not isinstance(source, dict):
            raise ValueError(f"source entry {index} must be an object")
        missing = REGISTRY_FIELDS - source.keys()
        if missing:
            raise ValueError(
                f"source entry {index} is missing fields: {', '.join(sorted(missing))}"
            )
        if source["id"] in identifiers:
            raise ValueError(f"duplicate source id: {source['id']}")
        identifiers.add(source["id"])
        if source["status"] not in HEALTH_STATUSES:
            raise ValueError(f"invalid status for source {source['id']}")
    return sources


def get_source_health() -> dict[str, Any]:
    """Return latest persisted checks, or honest unverified registry statuses."""
    registry = load_source_registry()
    if HEALTH_PATH.exists():
        with HEALTH_PATH.open(encoding="utf-8") as report_file:
            report = json.load(report_file)
        by_id = {record["id"]: record for record in report.get("sources", [])}
    else:
        by_id = {}

    records = []
    for source in registry:
        checked = by_id.get(source["id"])
        status = checked.get("status") if checked else source["status"]
        if status not in HEALTH_STATUSES:
            raise ValueError(f"invalid health status for source {source['id']}")
        records.append(
            {
                "id": source["id"],
                "name": source["name"],
                "category": source["category"],
                "url": source["url"],
                "access": source["access"],
                "format": source["format"],
                "licence": source["licence"],
                "region": source["region"],
                "fallback": source["fallback"],
                "path": source["path"],
                "status": status,
                "checked_at": checked.get("checked_at") if checked else None,
                "detail": checked.get("detail")
                if checked
                else "No live source check recorded.",
            }
        )
    return {"sources": records, "count": len(records)}


def inspect_observations(
    rows: Iterable[Mapping[str, Any]],
    *,
    label_column: str = "label",
    group_column: str | None = None,
    fold_column: str | None = None,
    source_crs: str | None = None,
    longitude_column: str = "longitude",
    latitude_column: str = "latitude",
) -> dict[str, Any]:
    """Report coordinate validity, nulls, duplicates, labels, and group leakage."""
    observations = [dict(row) for row in rows]
    columns = sorted({key for row in observations for key in row})
    null_counts = {
        column: sum(_is_missing(row.get(column)) for row in observations)
        for column in columns
    }
    duplicates = len(observations) - len(
        {json.dumps(row, sort_keys=True, default=str) for row in observations}
    )
    coordinate_errors = []
    for index, row in enumerate(observations):
        longitude = _as_finite_number(row.get(longitude_column))
        latitude = _as_finite_number(row.get(latitude_column))
        if longitude is None or not -180 <= longitude <= 180:
            coordinate_errors.append({"row": index, "field": longitude_column})
        if latitude is None or not -90 <= latitude <= 90:
            coordinate_errors.append({"row": index, "field": latitude_column})

    labels = Counter(
        str(row[label_column])
        for row in observations
        if label_column in row and not _is_missing(row[label_column])
    )
    leaking_groups: list[str] = []
    if group_column and fold_column:
        folds_by_group: dict[str, set[str]] = defaultdict(set)
        for row in observations:
            group = row.get(group_column)
            fold = row.get(fold_column)
            if not _is_missing(group) and not _is_missing(fold):
                folds_by_group[str(group)].add(str(fold))
        leaking_groups = sorted(
            group for group, folds in folds_by_group.items() if len(folds) > 1
        )

    return {
        "row_count": len(observations),
        "crs": source_crs or "NOT_PROVIDED",
        "crs_status": (
            "NOT_PROVIDED"
            if source_crs is None
            else "MATCH"
            if source_crs.upper() in {"EPSG:4326", "WGS84"}
            else "MISMATCH"
        ),
        "coordinate_range_check_crs": "EPSG:4326",
        "coordinate_errors": coordinate_errors,
        "null_counts": null_counts,
        "duplicate_rows": duplicates,
        "label_balance": dict(sorted(labels.items())),
        "spatial_leakage": {
            "checked": bool(group_column and fold_column),
            "group_column": group_column,
            "fold_column": fold_column,
            "leaking_group_count": len(leaking_groups),
            "leaking_groups": leaking_groups,
        },
    }


def _is_missing(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, float) and math.isnan(value):
        return True
    return False


def _as_finite_number(value: Any) -> float | None:
    if _is_missing(value):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None
