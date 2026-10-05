from __future__ import annotations

import joblib
import pytest

from backend.app.ml.adaptive_thresholds import estimate_zone_threshold
from backend.app.ml.inference import InferenceEngine
from backend.app.ml.model_disagreement import assess_model_disagreement
from backend.app.ml.physics import (
    combine_hybrid_components,
    factor_safety_risk_component,
    infinite_slope_factor_of_safety,
    rainfall_intensity_duration_indicator,
)
from backend.app.ml.slope_memory import cumulative_slope_memory
from backend.app.ml.synthetic_data import generate_nilgiris_pilot
from scripts.fetch_models import validate_entry


def test_infinite_slope_factor_of_safety_is_finite_and_saturation_sensitive():
    dry = infinite_slope_factor_of_safety(
        slope_deg=25, cohesion_kpa=8, unit_weight_kn_m3=18, soil_depth_m=1.2,
        friction_angle_deg=32, saturation_ratio=0.1,
    )
    wet = infinite_slope_factor_of_safety(
        slope_deg=25, cohesion_kpa=8, unit_weight_kn_m3=18, soil_depth_m=1.2,
        friction_angle_deg=32, saturation_ratio=0.8,
    )

    assert dry > wet > 0


def test_intensity_duration_and_hybrid_output_are_explicitly_simulated():
    threshold = rainfall_intensity_duration_indicator(
        rainfall_mm=60, duration_hours=6, threshold_a=12, threshold_b=0.2,
    )
    hybrid = combine_hybrid_components(
        model_probability=0.4,
        physics_component=factor_safety_risk_component(0.9, failure_reference=1, safe_reference=1.5),
        rainfall_component=min(threshold["threshold_ratio"], 1) if threshold["exceeds_threshold"] else 0,
        weights={"model": 0.5, "physics": 0.25, "rainfall": 0.25},
    )

    assert threshold["exceeds_threshold"]
    assert 0 <= hybrid["score"] <= 100
    assert hybrid["status"].startswith("SIMULATED")


def test_slope_memory_decays_older_stress():
    assert cumulative_slope_memory([10, 0], decay_periods=2) > cumulative_slope_memory([0, 10], decay_periods=2)


def test_adaptive_threshold_uses_demo_default_until_enough_observations():
    fallback = estimate_zone_threshold([20, 30], minimum_samples=5, fallback_threshold=45)
    experimental = estimate_zone_threshold(list(range(40)), minimum_samples=30)

    assert fallback == {"threshold": 45, "source": "DEMO DEFAULT", "calibrated": False, "sample_count": 2}
    assert experimental["source"] == "EXPERIMENTAL EMPIRICAL QUANTILE"
    assert not experimental["calibrated"]


def test_model_disagreement_is_unavailable_for_single_model():
    assert assess_model_disagreement({"LogisticRegression": 0.6})["available"] is False
    result = assess_model_disagreement({"A": 0.2, "B": 0.8}, threshold=0.3)
    assert result["disagreement"] is True
    assert result["spread"] == pytest.approx(0.6)


def test_inference_fallback_is_labeled_synthetic_and_has_placeholder_uncertainty(tmp_path):
    engine = InferenceEngine(model_path=tmp_path / "missing.joblib")
    features = generate_nilgiris_pilot(grid_size=10).cells.iloc[0].to_dict()

    result = engine.predict(features)

    assert 0 <= result["probability"] <= 1
    assert result["status"].startswith("DEMO")
    assert result["synthetic"] is True
    assert result["uncertainty"]["available"] is False
    assert "PLACEHOLDER" in result["uncertainty"]["label"]
    assert result["contributors"]
    assert "not a causal" in result["why"]
    assert result["hybrid_score"]["available"] is False


def test_inference_loads_a_reviewed_export_bundle(tmp_path):
    fallback = InferenceEngine(model_path=tmp_path / "not-present.joblib")
    model_path = tmp_path / "susceptibility.joblib"
    joblib.dump(fallback.model_bundle, model_path)
    loaded = InferenceEngine(model_path=model_path)
    features = generate_nilgiris_pilot(grid_size=10).cells.iloc[0].to_dict()

    assert loaded.predict(features)["synthetic"] is True
    assert loaded.status == "DEMO MODEL ARTIFACT"


def test_model_fetch_manifest_requires_https_name_and_sha256():
    valid = {"name": "model.joblib", "url": "https://models.example.test/model.joblib", "sha256": "a" * 64}
    assert validate_entry(valid) == ("model.joblib", valid["url"])
    with pytest.raises(ValueError, match="HTTPS"):
        validate_entry({**valid, "url": "http://models.example.test/model.joblib"})
    with pytest.raises(ValueError, match="filename"):
        validate_entry({**valid, "name": "../model.joblib"})
