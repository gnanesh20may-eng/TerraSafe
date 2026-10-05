import json
from pathlib import Path

import numpy as np
import pytest

from backend.app.ml.susceptibility import (
    _classification_metrics,
    make_zone_geojson,
)
from backend.app.ml.synthetic_data import FEATURE_COLUMNS, generate_nilgiris_pilot


def test_synthetic_pilot_is_repeatable_and_has_required_features():
    first = generate_nilgiris_pilot(grid_size=16, seed=7)
    second = generate_nilgiris_pilot(grid_size=16, seed=7)

    assert first.cells.equals(second.cells)
    assert set(FEATURE_COLUMNS).issubset(first.cells.columns)
    assert first.cells["landslide_label"].nunique() == 2
    assert first.cells["synthetic_inventory"].all()
    assert first.source_label.startswith("SYNTHETIC")


def test_synthetic_pilot_rejects_grid_too_small_for_spatial_validation():
    with pytest.raises(ValueError, match="at least 10"):
        generate_nilgiris_pilot(grid_size=9)


def test_metrics_include_confusion_and_error_rates():
    metrics = _classification_metrics(
        np.array([0, 0, 1, 1]),
        np.array([0.1, 0.8, 0.6, 0.3]),
    )

    assert metrics["confusion_matrix"] == [[1, 1], [1, 1]]
    assert metrics["false_alarm_rate"] == 0.5
    assert metrics["miss_rate"] == 0.5
    assert metrics["roc_auc"] == 0.5


def test_geojson_zones_have_valid_polygon_shape_and_synthetic_disclaimer():
    pilot = generate_nilgiris_pilot(grid_size=12)
    class FixedProbabilityModel:
        def predict_proba(self, features):
            scores = np.linspace(0.05, 0.95, len(features))
            return np.column_stack((1 - scores, scores))

    model = FixedProbabilityModel()
    result = make_zone_geojson(pilot, model)
    serialized = json.dumps(result)

    assert result["type"] == "FeatureCollection"
    assert len(result["features"]) == 12 * 12
    assert "Synthetic demonstration output" in result["metadata"]["disclaimer"]
    assert {feature["properties"]["zone"] for feature in result["features"]} <= {
        "Low",
        "Moderate",
        "High",
        "Critical",
    }
    assert json.loads(serialized)["features"][0]["geometry"]["type"] == "Polygon"
    for feature in result["features"]:
        ring = feature["geometry"]["coordinates"][0]
        assert ring[0] == ring[-1]
