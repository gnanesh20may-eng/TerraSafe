import asyncio
from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd
import pytest

from backend.app.ingest.base import AsyncJSONIngestor, SourceAdapterError
from backend.app.ingest.providers import (
    SOURCE_NAMES,
    OpenMeteoIngestor,
    build_ingestors,
)
from backend.app.ml.drift import (
    dataset_drift_report,
    population_stability_index,
    retraining_recommendation,
)
from backend.app.ml.dynamic_risk import (
    antecedent_rainfall,
    earthquake_trigger_score,
    hybrid_dynamic_risk,
    infinite_slope_factor_of_safety,
    intensity_duration_thresholds,
)
from backend.app.ml.explain import (
    constrained_counterfactuals,
    plain_language_risk_explanation,
)
from backend.app.ml.forecast import (
    conformal_radius,
    forecast_risk_horizons,
    open_meteo_hourly_observations,
)
from backend.app.ml.onnx_export import export_classifier_to_onnx


def test_all_sources_have_offline_fixtures_and_cache_is_defensive():
    async def run():
        adapters = build_ingestors()
        assert set(adapters) == set(SOURCE_NAMES)
        for source, adapter in adapters.items():
            first = await adapter.fetch({"region": "Nilgiris"})
            assert first.is_mock
            assert first.payload["mock"] is True
            assert first.payload["source_label"].startswith("MOCK")
            first.payload["source_label"] = "caller mutation"
            cached = await adapter.fetch({"region": "Nilgiris"})
            assert cached.cache_hit
            assert cached.payload["source_label"].startswith("MOCK")

    asyncio.run(run())


def test_live_ingestion_requires_configured_product_endpoints():
    with pytest.raises(SourceAdapterError, match="gpm_imerg"):
        build_ingestors(mock_mode=False)


def test_open_meteo_mock_normalizes_parallel_arrays():
    async def run():
        snapshot = await OpenMeteoIngestor().fetch(
            {"latitude": 11.2, "longitude": 76.5}
        )
        records = open_meteo_hourly_observations(snapshot.payload)
        assert snapshot.is_mock
        assert len(records) == 793
        assert records[0]["synthetic"] is True
        assert "soil_moisture_fraction" in records[0]

    asyncio.run(run())


def test_open_meteo_rejects_invalid_coordinates_before_request():
    async def run():
        with pytest.raises(ValueError, match="latitude"):
            await OpenMeteoIngestor().fetch({"latitude": 91})

    asyncio.run(run())


def test_antecedent_rainfall_reports_gaps_and_id_thresholds():
    as_of = datetime(2025, 1, 1, 10, 30, tzinfo=timezone.utc)
    observations = [
        {"timestamp": "2025-01-01T08:00:00Z", "precipitation_mm": 1},
        {"timestamp": "2025-01-01T09:00:00Z", "precipitation_mm": 2},
        {"timestamp": "2025-01-01T10:00:00Z", "precipitation_mm": 3},
    ]

    rainfall = antecedent_rainfall(observations, as_of=as_of)
    thresholds = intensity_duration_thresholds(
        rainfall,
        coefficient_mm_per_hour=1,
        exponent=0,
    )

    assert rainfall["1h"]["rainfall_mm"] == 3
    assert rainfall["1h"]["coverage"] == 1
    assert rainfall["24h"]["rainfall_mm"] == 6
    assert rainfall["24h"]["observed_hours"] == 3
    assert not rainfall["24h"]["complete"]
    assert thresholds["1h"]["exceeded"]
    assert thresholds["24h"]["available"]


def test_antecedent_rainfall_rejects_duplicate_hours_and_negative_values():
    duplicate_timestamp = [
        {"timestamp": "2025-01-01T10:01:00Z", "precipitation_mm": 1},
        {"timestamp": "2025-01-01T10:01:00Z", "precipitation_mm": 1},
    ]
    with pytest.raises(ValueError, match="duplicate"):
        antecedent_rainfall(
            duplicate_timestamp,
            as_of=datetime(2025, 1, 1, 11, tzinfo=timezone.utc),
        )
    with pytest.raises(ValueError, match="non-negative"):
        antecedent_rainfall(
            [{"timestamp": "2025-01-01T10:00:00Z", "precipitation_mm": -1}]
        )


def test_half_hourly_rainfall_is_aggregated_within_antecedent_hour():
    rainfall = antecedent_rainfall(
        [
            {"timestamp": "2025-01-01T10:30:00Z", "precipitation_mm": 1.5},
            {"timestamp": "2025-01-01T11:00:00Z", "precipitation_mm": 2.5},
        ],
        as_of=datetime(2025, 1, 1, 11, tzinfo=timezone.utc),
    )

    assert rainfall["1h"]["rainfall_mm"] == 4
    assert rainfall["1h"]["observation_count"] == 2


def test_infinite_slope_and_hybrid_risk_move_in_expected_direction():
    low_slope = infinite_slope_factor_of_safety(
        slope_deg=15,
        soil_depth_m=1,
        unit_weight_kn_m3=18,
        friction_angle_deg=30,
        cohesion_kpa=5,
        saturation_ratio=0.3,
    )
    steep_slope = infinite_slope_factor_of_safety(
        slope_deg=40,
        soil_depth_m=1,
        unit_weight_kn_m3=18,
        friction_angle_deg=30,
        cohesion_kpa=5,
        saturation_ratio=0.8,
    )
    dry = hybrid_dynamic_risk(susceptibility_score=0.4)
    wet = hybrid_dynamic_risk(
        susceptibility_score=0.4,
        factor_of_safety=steep_slope,
        soil_moisture_fraction=0.6,
        earthquake_trigger_score=0.8,
        rainfall_thresholds={
            "24h": {"available": True, "threshold_ratio": 1.8}
        },
    )

    assert low_slope > steep_slope
    no_slope_failure = hybrid_dynamic_risk(
        susceptibility_score=0.4,
        factor_of_safety=float("inf"),
    )
    assert wet["risk_score"] > dry["risk_score"]
    assert no_slope_failure["components"]["slope_instability"] == 0
    assert wet["risk_level"] in {"Yellow", "Orange", "Red"}
    assert not wet["calibrated_probability"]


def test_earthquake_trigger_decreases_with_distance_and_magnitude():
    nearby = [
        {
            "properties": {"mag": 5},
            "geometry": {"coordinates": [76.7, 11.35, 5]},
        }
    ]
    distant = [
        {
            "properties": {"mag": 2},
            "geometry": {"coordinates": [78.7, 13.35, 5]},
        }
    ]

    nearby_score = earthquake_trigger_score(
        nearby, latitude=11.35, longitude=76.7
    )
    distant_score = earthquake_trigger_score(
        distant, latitude=11.35, longitude=76.7
    )
    assert nearby_score > distant_score


def test_forecast_horizons_and_finite_sample_conformal_intervals():
    as_of = datetime(2025, 1, 1, tzinfo=timezone.utc)
    hourly = [
        {
            "timestamp": (as_of + timedelta(hours=hour)).isoformat(),
            "precipitation_mm": 1.0,
        }
        for hour in range(1, 73)
    ]
    errors = [index / 100 for index in range(1, 10)]

    result = forecast_risk_horizons(
        susceptibility_score=0.5,
        hourly_forecast=hourly,
        as_of=as_of,
        calibration_errors=errors,
        synthetic_data=True,
    )

    assert [item["horizon_hours"] for item in result["horizons"]] == [24, 48, 72]
    assert all(item["coverage"] == 1 for item in result["horizons"])
    assert all(item["lower"] is not None and item["upper"] is not None for item in result["horizons"])
    assert result["synthetic"]
    assert result["horizons"][0]["rainfall_mm"] == 24
    assert conformal_radius(errors, 0.9) == 0.09
    assert conformal_radius(errors[:8], 0.9) is None
    assert forecast_risk_horizons(
        susceptibility_score=0.5,
        hourly_forecast=hourly,
        as_of=as_of,
    )["horizons"][0]["lower"] is None


def test_drift_detection_and_operator_gated_retraining_policy():
    reference = np.linspace(0, 1, 200)
    shifted = np.linspace(2, 3, 200)
    assert population_stability_index(reference, reference) < 0.01
    assert population_stability_index(reference, shifted) > 0.2

    report = dataset_drift_report(
        pd.DataFrame({"feature": reference}),
        pd.DataFrame({"feature": shifted}),
    )
    recommendation = retraining_recommendation(
        "2025-01-01T00:00:00Z",
        report,
        now="2025-01-02T00:00:00Z",
    )
    assert report["drift_detected"]
    assert recommendation["retraining_recommended"]
    assert recommendation["action"] == "enqueue_with_operator_review"


def test_counterfactual_and_plain_language_explanation_are_explicit():
    class MonotoneModel:
        def predict_proba(self, features):
            score = 1 / (1 + np.exp(-features["rain"].to_numpy()))
            return np.column_stack((1 - score, score))

    result = constrained_counterfactuals(
        MonotoneModel(),
        pd.DataFrame({"rain": [4.0]}),
        {"rain": (0.0, 5.0)},
        target_probability=0.25,
    )
    explanation = plain_language_risk_explanation(
        {
            "risk_level": "Orange",
            "reasons": ["Rainfall contributes 0.80 on the index."],
        }
    )
    assert result["suggestions"]
    assert "not causal effects" in result["message"]
    assert "Current modeled risk is Orange" in explanation


def test_onnx_export_rejects_wrong_extension_before_optional_import(tmp_path):
    with pytest.raises(ValueError, match=".onnx"):
        export_classifier_to_onnx(
            object(),
            ["feature"],
            tmp_path / "model.bin",
        )
