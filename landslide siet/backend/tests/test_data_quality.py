import pandas as pd
import pytest

from backend.app.ml.data_quality import (
    assert_spatial_groups_disjoint,
    validate_training_frame,
)
from backend.app.ml.synthetic_data import generate_nilgiris_pilot


def test_synthetic_pilot_passes_wgs84_data_checks():
    pilot = generate_nilgiris_pilot(grid_size=12, seed=9)

    result = validate_training_frame(pilot.cells, crs="EPSG:4326")

    assert result["status"] == "PASS"
    assert result["rows"] == 144
    assert result["duplicate_coordinates"] == 0
    assert set(result["label_balance"]) == {"0", "1"}


def test_data_checks_report_nulls_duplicate_coordinates_and_invalid_crs():
    frame = pd.DataFrame(
        {
            "longitude": [76.8, 76.8],
            "latitude": [11.3, 11.3],
            "landslide_label": [0, 1],
            "spatial_block": [1, 2],
            "feature": [None, 1],
        }
    )

    result = validate_training_frame(frame, crs="EPSG:3857")

    assert result["status"] == "FAIL"
    assert result["duplicate_coordinates"] == 1
    assert result["null_counts"] == {"feature": 1}
    assert len(result["issues"]) == 3


def test_spatial_fold_groups_must_not_overlap():
    assert_spatial_groups_disjoint([1, 2], [3, 4])
    with pytest.raises(ValueError, match="spatial block leakage"):
        assert_spatial_groups_disjoint([1, 2], [2, 3])