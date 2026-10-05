"""Model-backed, explicitly labeled experimental landslide risk inference."""

from __future__ import annotations

import hashlib
import logging
import math
from datetime import datetime
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np
import pandas as pd

from backend.app.ml.dynamic_risk import (
    antecedent_rainfall,
    hybrid_dynamic_risk,
    infinite_slope_factor_of_safety,
    intensity_duration_thresholds,
)
from backend.app.ml.explain import plain_language_risk_explanation
from backend.app.ml.forecast import conformal_radius
from backend.app.ml.susceptibility import _model_factories
from backend.app.ml.synthetic_data import FEATURE_COLUMNS, generate_nilgiris_pilot

LOGGER = logging.getLogger(__name__)
REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_MODEL_PATH = REPOSITORY_ROOT / "ml" / "data" / "models" / "terrasafe.joblib"
DISAGREEMENT_THRESHOLD = 0.2


def adaptive_zone_threshold(
    zone: str,
    historical_intensities_mm_h: Sequence[float],
    *,
    quantile: float = 0.95,
    minimum_samples: int = 20,
    fallback_threshold_mm_h: float = 30.0,
) -> dict[str, Any]:
    """Return an empirical demo threshold or an explicitly labeled fallback."""
    if not zone.strip():
        raise ValueError("zone must not be blank")
    if not 0 < quantile < 1 or minimum_samples < 1:
        raise ValueError("quantile must be in (0, 1) and minimum_samples positive")
    if not math.isfinite(fallback_threshold_mm_h) or fallback_threshold_mm_h <= 0:
        raise ValueError("fallback threshold must be positive and finite")
    values = np.asarray(historical_intensities_mm_h, dtype=float)
    if values.ndim != 1 or not np.isfinite(values).all() or (values < 0).any():
        raise ValueError("historical intensities must be a finite non-negative sequence")
    if values.size < minimum_samples:
        return {
            "zone": zone,
            "threshold_mm_h": fallback_threshold_mm_h,
            "sample_count": int(values.size),
            "quantile": quantile,
            "status": "SCAFFOLD",
            "method": "demonstration fallback; insufficient local history",
        }
    return {
        "zone": zone,
        "threshold_mm_h": float(np.quantile(values, quantile)),
        "sample_count": int(values.size),
        "quantile": quantile,
        "status": "DEMO",
        "method": "empirical quantile of supplied history; requires domain validation",
    }


def load_trusted_export(model_path: Path = DEFAULT_MODEL_PATH) -> tuple[Any, str]:
    """Load a local joblib export only when its adjacent SHA-256 is present."""
    if not model_path.exists():
        return _fit_synthetic_logistic(), "SIMULATED"
    if model_path.suffix.lower() != ".joblib":
        raise ValueError("local inference currently supports only .joblib artifacts")
    checksum_path = model_path.with_suffix(model_path.suffix + ".sha256")
    if not checksum_path.is_file():
        raise ValueError(f"model checksum file is required: {checksum_path}")
    checksum_parts = checksum_path.read_text(encoding="ascii").strip().split()
    if not checksum_parts:
        raise ValueError(f"empty SHA-256 checksum file: {checksum_path}")
    expected = checksum_parts[0].lower()
    if len(expected) != 64 or any(char not in "0123456789abcdef" for char in expected):
        raise ValueError(f"invalid SHA-256 checksum in {checksum_path}")
    digest = hashlib.sha256(model_path.read_bytes()).hexdigest()
    if digest != expected:
        raise ValueError(f"SHA-256 mismatch for model artifact {model_path}")

    import joblib

    model = joblib.load(model_path)
    if not callable(getattr(model, "predict_proba", None)):
        raise ValueError("exported classifier must implement predict_proba")
    return model, "SCAFFOLD"


def infer_risk(
    observation: Mapping[str, Any],
    *,
    model_path: Path = DEFAULT_MODEL_PATH,
    rainfall_observations: Sequence[Mapping[str, Any]] = (),
    as_of: str | datetime | None = None,
    soil_moisture_fraction: float | None = None,
    slope_parameters: Mapping[str, float] | None = None,
    zone: str = "unspecified",
    zone_rainfall_history_mm_h: Sequence[float] = (),
    model_scores: Mapping[str, float] | None = None,
    conformal_errors: Sequence[float] = (),
    confidence_level: float = 0.9,
) -> dict[str, Any]:
    """Estimate a non-calibrated hybrid risk index and explain its inputs."""
    feature_values = {}
    for feature in FEATURE_COLUMNS:
        if feature not in observation:
            raise ValueError(f"observation is missing feature {feature!r}")
        value = float(observation[feature])
        if not math.isfinite(value):
            raise ValueError(f"feature {feature!r} must be finite")
        feature_values[feature] = value
    frame = pd.DataFrame([feature_values], columns=FEATURE_COLUMNS)

    model, model_status = load_trusted_export(model_path)
    probability = float(model.predict_proba(frame)[0, 1])
    if not math.isfinite(probability) or not 0 <= probability <= 1:
        raise ValueError("model returned a probability outside [0, 1]")

    rainfall = antecedent_rainfall(rainfall_observations, as_of=as_of)
    zone_threshold = adaptive_zone_threshold(zone, zone_rainfall_history_mm_h)
    if zone_threshold["status"] == "DEMO":
        coefficient = float(zone_threshold["threshold_mm_h"])
    else:
        coefficient = 30.0
    duration_thresholds = intensity_duration_thresholds(
        rainfall,
        coefficient_mm_per_hour=coefficient,
        exponent=0.5,
    )

    factor_of_safety = None
    if slope_parameters is not None:
        required = {
            "slope_deg",
            "soil_depth_m",
            "unit_weight_kn_m3",
            "friction_angle_deg",
            "cohesion_kpa",
            "saturation_ratio",
        }
        missing = required - slope_parameters.keys()
        if missing:
            raise ValueError("slope_parameters missing: " + ", ".join(sorted(missing)))
        factor_of_safety = infinite_slope_factor_of_safety(**slope_parameters)

    risk = hybrid_dynamic_risk(
        susceptibility_score=probability,
        rainfall_thresholds=duration_thresholds,
        factor_of_safety=factor_of_safety,
        soil_moisture_fraction=soil_moisture_fraction,
        synthetic_data=model_status == "SIMULATED",
    )
    scores = {"LogisticRegression": probability, **dict(model_scores or {})}
    if any(not math.isfinite(value) or not 0 <= value <= 1 for value in scores.values()):
        raise ValueError("all model scores must be finite probabilities in [0, 1]")
    spread = max(scores.values()) - min(scores.values())
    disagreement = {
        "available": len(scores) > 1,
        "score_spread": round(spread, 4) if len(scores) > 1 else None,
        "threshold": DISAGREEMENT_THRESHOLD,
        "flag": spread >= DISAGREEMENT_THRESHOLD if len(scores) > 1 else None,
        "status": "DEMO" if len(scores) > 1 else "SCAFFOLD",
    }

    radius = conformal_radius(conformal_errors, confidence_level)
    uncertainty = {
        "lower": max(0.0, probability - radius) if radius is not None else None,
        "upper": min(1.0, probability + radius) if radius is not None else None,
        "confidence_level": confidence_level,
        "calibration_sample_count": len(conformal_errors),
        "method": (
            "split_conformal_absolute_error"
            if radius is not None
            else "unavailable_without_sufficient_calibration"
        ),
        "status": "SCAFFOLD",
    }
    memory = {
        "7d_rainfall_mm": rainfall["168h"]["rainfall_mm"],
        "30d_rainfall_mm": rainfall["720h"]["rainfall_mm"],
        "status": "DEMO" if rainfall_observations else "MISSING",
        "description": "Antecedent rainfall memory; not a calibrated soil-memory model.",
    }
    factors = _top_logistic_factors(model, frame)
    result = {
        "status": model_status,
        "model": {
            "type": type(model).__name__,
            "artifact": "trusted_export" if model_status == "SCAFFOLD" else "synthetic_fallback",
            "susceptibility_probability": round(probability, 4),
        },
        "risk": risk,
        "uncertainty": uncertainty,
        "top_factors": factors,
        "rainfall": {
            "antecedent": rainfall,
            "intensity_duration": duration_thresholds,
            "zone_threshold": zone_threshold,
        },
        "slope_stability": {
            "factor_of_safety": factor_of_safety,
            "status": "DEMO" if factor_of_safety is not None else "MISSING",
        },
        "slope_memory": memory,
        "model_disagreement": disagreement,
        "why": plain_language_risk_explanation(risk),
        "disclaimer": risk["disclaimer"],
    }
    return result


def _fit_synthetic_logistic():
    pilot = generate_nilgiris_pilot(grid_size=20, seed=42)
    model = _model_factories(42)["LogisticRegression"]()
    model.fit(pilot.cells.loc[:, FEATURE_COLUMNS], pilot.cells["landslide_label"])
    return model


def _top_logistic_factors(
    model: Any, frame: pd.DataFrame, limit: int = 3
) -> list[dict[str, Any]]:
    steps = getattr(model, "named_steps", {})
    classifier = next(
        (
            candidate
            for candidate in reversed(list(steps.values()))
            if hasattr(candidate, "coef_") or hasattr(candidate, "feature_importances_")
        ),
        model
        if hasattr(model, "coef_") or hasattr(model, "feature_importances_")
        else None,
    )
    scaler = next((step for step in steps.values() if hasattr(step, "scale_")), None)
    if classifier is None:
        return []
    if not hasattr(classifier, "coef_"):
        importances = np.asarray(classifier.feature_importances_, dtype=float)
        indexes = np.argsort(importances)[::-1][:limit]
        return [
            {
                "feature": str(frame.columns[index]),
                "value": float(frame.iloc[0, index]),
                "contribution": float(importances[index]),
                "method": "model feature importance; not causal",
            }
            for index in indexes
        ]
    coefficients = np.asarray(classifier.coef_)[0]
    values = frame.iloc[0].to_numpy(dtype=float)
    if scaler is not None:
        values = (values - np.asarray(scaler.mean_)) / np.asarray(scaler.scale_)
    contributions = coefficients * values
    indexes = np.argsort(np.abs(contributions))[::-1][:limit]
    return [
        {
            "feature": str(frame.columns[index]),
            "value": float(frame.iloc[0, index]),
            "contribution": float(contributions[index]),
            "method": "linear model coefficient contribution; not causal",
        }
        for index in indexes
    ]
