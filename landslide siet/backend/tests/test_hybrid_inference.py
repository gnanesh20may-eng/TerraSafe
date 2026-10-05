import pytest

from backend.app.ml.inference import SusceptibilityInference
from backend.app.ml.physics import infinite_slope_factor, rainfall_id_trigger
from backend.app.ml.slope_memory import update_slope_memory
from backend.app.ml.synthetic_data import FEATURE_COLUMNS, generate_nilgiris_pilot
from backend.app.ml.thresholds import AdaptiveZoneThresholds


def test_inference_uses_labelled_synthetic_fallback_and_returns_hybrid_explanation(tmp_path):
    cells = generate_nilgiris_pilot(grid_size=12, seed=11).cells
    values = cells.loc[0, FEATURE_COLUMNS].to_dict()
    values["rainfall_24h_mm"] = 36.0

    result = SusceptibilityInference(tmp_path / "missing.joblib").predict(values)

    assert 0 <= result["probability"] <= 1
    assert 0 <= result["hybrid_probability"] <= 1
    assert result["model_status"] == "DEMO_SYNTHETIC_LOGISTIC"
    assert result["uncertainty_band"]["status"].startswith("PLACEHOLDER")
    assert result["physics"]["status"].startswith("ILLUSTRATIVE")
    assert result["top_factors"]
    assert result["synthetic_training_data"] is True


def test_infinite_slope_and_rainfall_intensity_duration_checks():
    factor = infinite_slope_factor(30, 5, 18, 1.5, 30, pore_pressure_ratio=0.2)
    trigger = rainfall_id_trigger(48, 24, threshold_mm_per_hour=1.5)

    assert factor > 0
    assert trigger["intensity_mm_per_hour"] == 2
    assert trigger["exceeded"] is True
    with pytest.raises(ValueError):
        infinite_slope_factor(90, 5, 18, 1.5, 30)


def test_slope_memory_accumulates_and_decays_stress():
    assert update_slope_memory(10, 2, decay=0.5) == 7
    with pytest.raises(ValueError):
        update_slope_memory(1, 2, decay=1.5)


def test_zone_thresholds_adapt_to_history_and_clamp():
    thresholds = AdaptiveZoneThresholds()

    assert thresholds.for_zone("critical") == 0.4
    assert thresholds.for_zone("watch", [0.2, 0.6, 0.9]) == pytest.approx(0.66)
    assert thresholds.for_zone("watch", [0.95, 0.98]) == 0.8