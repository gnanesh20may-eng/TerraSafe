import builtins
import hashlib
import io

import joblib
import numpy as np
import pytest
from sklearn.dummy import DummyClassifier

from backend.app.ml.logistic import NumpyLogisticRegression
from backend.app.ml.inference import (
    adaptive_zone_threshold,
    infer_risk,
    load_trusted_export,
)
from backend.app.ml.susceptibility import _model_factories
from backend.app.ml.synthetic_data import FEATURE_COLUMNS, generate_nilgiris_pilot
from scripts import fetch_models


def test_model_factories_fall_back_to_logistic_when_tree_import_is_blocked(
    monkeypatch,
):
    real_import = builtins.__import__

    def blocked_tree_import(name, *args, **kwargs):
        if name in {"xgboost", "sklearn.linear_model"}:
            raise OSError("simulated Windows Application Control DLL denial")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", blocked_tree_import)

    factories = _model_factories(seed=7)

    assert list(factories) == ["LogisticRegression"]
    model = factories["LogisticRegression"]()
    assert isinstance(model, NumpyLogisticRegression)
    pilot = generate_nilgiris_pilot(grid_size=10, seed=7)
    model.fit(pilot.cells.loc[:, FEATURE_COLUMNS], pilot.cells["landslide_label"])
    assert model.predict_proba(pilot.cells.loc[:, FEATURE_COLUMNS]).shape == (100, 2)


def test_numpy_logistic_returns_finite_binary_probabilities():
    model = NumpyLogisticRegression(max_iter=500)
    model.fit([[0, 1], [1, 0], [2, 0], [3, 1]], [0, 0, 1, 1])

    probabilities = model.predict_proba([[0, 1], [3, 1]])

    assert probabilities.shape == (2, 2)
    assert np.isfinite(probabilities).all()
    assert np.allclose(probabilities.sum(axis=1), 1)
    assert probabilities[1, 1] > probabilities[0, 1]


def test_adaptive_zone_threshold_labels_empirical_and_fallback_status():
    fallback = adaptive_zone_threshold("north", [1.0, 2.0], minimum_samples=3)
    empirical = adaptive_zone_threshold(
        "south", list(np.arange(20, dtype=float)), minimum_samples=20
    )

    assert fallback["threshold_mm_h"] == 30.0
    assert fallback["status"] == "SCAFFOLD"
    assert empirical["sample_count"] == 20
    assert empirical["status"] == "DEMO"
    assert empirical["threshold_mm_h"] == pytest.approx(18.05)


def test_inference_returns_labeled_probability_triggers_uncertainty_and_why(tmp_path):
    pilot = generate_nilgiris_pilot(grid_size=10, seed=5)
    row = pilot.cells.iloc[0]
    observation = {feature: float(row[feature]) for feature in FEATURE_COLUMNS}
    result = infer_risk(
        observation,
        model_path=tmp_path / "not-exported.joblib",
        rainfall_observations=[
            {"timestamp": "2025-01-01T09:00:00Z", "precipitation_mm": 4.0},
            {"timestamp": "2025-01-01T10:00:00Z", "precipitation_mm": 6.0},
        ],
        as_of="2025-01-01T10:00:00Z",
        soil_moisture_fraction=0.5,
        slope_parameters={
            "slope_deg": 30,
            "soil_depth_m": 1.0,
            "unit_weight_kn_m3": 18.0,
            "friction_angle_deg": 30.0,
            "cohesion_kpa": 5.0,
            "saturation_ratio": 0.4,
        },
        zone="north",
        zone_rainfall_history_mm_h=list(np.arange(20, dtype=float)),
        model_scores={"RandomForest": 0.0, "XGBoost": 1.0},
        conformal_errors=[0.1] * 19,
    )

    assert result["status"] == "SIMULATED"
    assert 0 <= result["model"]["susceptibility_probability"] <= 1
    assert result["risk"]["calibrated_probability"] is False
    assert result["uncertainty"]["method"] == "split_conformal_absolute_error"
    assert result["uncertainty"]["status"] == "SCAFFOLD"
    assert result["rainfall"]["zone_threshold"]["status"] == "DEMO"
    assert result["slope_stability"]["status"] == "DEMO"
    assert result["slope_memory"]["7d_rainfall_mm"] is not None
    assert result["model_disagreement"]["flag"] is True
    assert result["top_factors"]
    assert result["why"]
    assert "official disaster-management warnings" in result["disclaimer"]


def test_inference_rejects_missing_and_non_finite_features(tmp_path):
    with pytest.raises(ValueError, match="missing feature"):
        infer_risk({}, model_path=tmp_path / "missing.joblib")
    pilot = generate_nilgiris_pilot(grid_size=10)
    observation = {feature: 1.0 for feature in FEATURE_COLUMNS}
    observation["slope_deg"] = float("nan")
    with pytest.raises(ValueError, match="must be finite"):
        infer_risk(observation, model_path=tmp_path / "missing.joblib")


def test_trusted_export_requires_matching_checksum(tmp_path):
    model_path = tmp_path / "model.joblib"
    model = DummyClassifier(strategy="prior")
    model.fit([[0.0], [1.0]], [0, 1])
    joblib.dump(model, model_path)
    checksum_path = model_path.with_suffix(".joblib.sha256")
    checksum_path.write_text(
        hashlib.sha256(model_path.read_bytes()).hexdigest(), encoding="ascii"
    )

    loaded, status = load_trusted_export(model_path)

    assert status == "SCAFFOLD"
    assert loaded.predict_proba([[0.5]]).shape == (1, 2)
    model_path.write_bytes(model_path.read_bytes() + b"tamper")
    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        load_trusted_export(model_path)


def test_model_fetch_verifies_hash_before_publishing(tmp_path, monkeypatch):
    payload = b"verified model bytes"

    class FakeResponse(io.BytesIO):
        headers = {"Content-Length": str(len(payload))}

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            self.close()

    monkeypatch.setattr(
        fetch_models, "urlopen", lambda *_args, **_kwargs: FakeResponse(payload)
    )
    digest = hashlib.sha256(payload).hexdigest()
    artifact = fetch_models.fetch_verified(
        "https://models.example.test/model.joblib",
        "model.joblib",
        digest,
        tmp_path,
    )

    assert artifact.read_bytes() == payload
    assert artifact.with_suffix(".joblib.sha256").read_text().strip() == digest


def test_model_fetch_rejects_non_https_and_bad_hash(tmp_path):
    with pytest.raises(ValueError, match="HTTPS"):
        fetch_models.fetch_verified("http://example.test/m", "m.onnx", "0" * 64, tmp_path)
    with pytest.raises(ValueError, match="64 hexadecimal"):
        fetch_models.fetch_verified("https://example.test/m", "m.joblib", "bad", tmp_path)


def test_inference_rejects_onnx_artifact_until_runtime_support_exists(tmp_path):
    model_path = tmp_path / "model.onnx"
    model_path.write_bytes(b"not loaded")

    with pytest.raises(ValueError, match="only .joblib"):
        load_trusted_export(model_path)


def test_model_fetch_does_not_publish_checksum_mismatch(tmp_path, monkeypatch):
    class FakeResponse(io.BytesIO):
        headers = {"Content-Length": "4"}

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            self.close()

    monkeypatch.setattr(
        fetch_models, "urlopen", lambda *_args, **_kwargs: FakeResponse(b"bad!")
    )

    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        fetch_models.fetch_verified(
            "https://models.example.test/model.joblib",
            "model.joblib",
            hashlib.sha256(b"other").hexdigest(),
            tmp_path,
        )

    assert not (tmp_path / "model.joblib").exists()
    assert not (tmp_path / "model.joblib.part").exists()
