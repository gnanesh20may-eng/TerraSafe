from __future__ import annotations

import pandas as pd
import pytest

from backend.app.ml.data_validation import (
    check_spatial_block_leakage,
    validate_hourly_series,
    validate_point_table,
)


def test_point_validator_reports_crs_nulls_duplicates_and_label_balance():
    frame = pd.DataFrame({
        "latitude": [11.3, 11.3, None, 95.0],
        "longitude": [76.8, 76.8, 76.9, 76.0],
        "landslide_label": [0, 0, 1, 1],
    })

    report = validate_point_table(frame, label="landslide_label")

    assert report["rows"] == 4
    assert report["coordinate_null_rows"] == 1
    assert report["out_of_range_coordinates"] == 1
    assert report["duplicate_coordinates"] == 1
    assert report["label_balance"] == {"0": 2, "1": 2}
    assert report["crs"] == "EPSG:4326"
    assert report["crs_valid"]


def test_point_validator_flags_a_non_wgs84_crs():
    frame = pd.DataFrame({"latitude": [11.3], "longitude": [76.8]})

    report = validate_point_table(frame, crs="EPSG:3857")

    assert not report["crs_valid"]


def test_point_validator_requires_coordinate_columns():
    with pytest.raises(ValueError, match="latitude"):
        validate_point_table(pd.DataFrame({"name": ["sample"]}))


def test_spatial_block_leakage_check_detects_overlap():
    assert check_spatial_block_leakage({"a", "b"}, {"c"})["passed"]
    result = check_spatial_block_leakage({"a", "b"}, {"b", "c"})
    assert result == {"passed": False, "overlap_blocks": ["b"]}


def test_hourly_series_detects_misaligned_null_duplicate_and_unordered_data():
    report = validate_hourly_series(
        ["2026-01-01T01:00", "2026-01-01T00:00", "2026-01-01T00:00"],
        {"precipitation": [0.0, None]},
    )

    assert report["length_mismatches"] == ["precipitation"]
    assert report["null_counts"]["precipitation"] == 1
    assert report["duplicate_timestamps"] == 1
    assert not report["strictly_increasing_timestamps"]
    assert not report["passed"]


def test_hourly_series_accepts_valid_source_observations():
    report = validate_hourly_series(
        ["2026-01-01T00:00", "2026-01-01T01:00"],
        {"precipitation": [0.0, 1.2], "soil_moisture": [0.31, 0.32]},
    )

    assert report["passed"]
