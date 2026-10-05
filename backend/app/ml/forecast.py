"""Horizon-based dynamic-risk outlooks with optional MAPIE intervals."""

from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone
from typing import Any, Mapping, Sequence

import numpy as np

from backend.app.ml.dynamic_risk import hybrid_dynamic_risk, _utc_datetime


def open_meteo_hourly_observations(payload: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Convert Open-Meteo parallel hourly arrays into canonical records."""
    hourly = payload.get("hourly")
    if not isinstance(hourly, Mapping):
        raise ValueError("weather payload is missing hourly data")
    times = hourly.get("time")
    rainfall = hourly.get("precipitation")
    soil_moisture = hourly.get("soil_moisture_0_to_7cm")
    if not isinstance(times, list) or not isinstance(rainfall, list) or len(times) != len(rainfall):
        raise ValueError("hourly time and precipitation arrays must have equal lengths")
    if soil_moisture is not None and len(soil_moisture) != len(times):
        raise ValueError("soil moisture and hourly time arrays must have equal lengths")
    records = []
    for index, (timestamp, amount) in enumerate(zip(times, rainfall)):
        record: dict[str, Any] = {
            "timestamp": timestamp,
            "precipitation_mm": float(amount),
        }
        if soil_moisture is not None and soil_moisture[index] is not None:
            record["soil_moisture_fraction"] = float(soil_moisture[index])
        if payload.get("mock"):
            record["synthetic"] = True
        records.append(record)
    return records


def conformal_radius(
    calibration_errors: Sequence[float],
    coverage_level: float = 0.9,
) -> float | None:
    """Finite-sample split-conformal absolute-error radius.

    Returns None when there are too few calibration points to support the
    requested finite-sample coverage rather than silently clipping the rank.
    """
    if not 0 < coverage_level < 1:
        raise ValueError("coverage_level must be strictly between 0 and 1")
    errors = np.asarray(calibration_errors, dtype=float)
    if errors.ndim != 1 or not np.isfinite(errors).all() or (errors < 0).any():
        raise ValueError("calibration_errors must be a finite 1D sequence of absolute errors")
    if errors.size == 0:
        return None
    rank = math.ceil((errors.size + 1) * coverage_level)
    if rank > errors.size:
        return None
    return float(np.sort(errors)[rank - 1])


def forecast_risk_horizons(
    *,
    susceptibility_score: float,
    hourly_forecast: Sequence[Mapping[str, Any]],
    as_of: str | datetime | None = None,
    factor_of_safety: float | None = None,
    soil_moisture_fraction: float | None = None,
    calibration_errors: Sequence[float] | None = None,
    coverage_level: float = 0.9,
    threshold_coefficient_mm_h: float = 30,
    threshold_exponent: float = 0.5,
    synthetic_data: bool = False,
) -> dict[str, Any]:
    """Project transparent 24/48/72h risk indices from forecast precipitation.

    This is a deterministic trigger-based forecast baseline, not a trained TFT
    or LSTM. Intervals are emitted only when supplied with adequate held-out
    calibration residuals.
    """
    current = _utc_datetime(as_of or datetime.now(timezone.utc))
    forecast_rows: list[tuple[datetime, float]] = []
    for item in hourly_forecast:
        timestamp = _utc_datetime(item["timestamp"])
        amount = float(item["precipitation_mm"])
        if not math.isfinite(amount) or amount < 0:
            raise ValueError("forecast precipitation must be finite and non-negative")
        if timestamp > current:
            forecast_rows.append((timestamp, amount))
    forecast_rows.sort(key=lambda item: item[0])
    hours = [stamp.replace(minute=0, second=0, microsecond=0) for stamp, _ in forecast_rows]
    if len(hours) != len(set(hours)):
        raise ValueError("forecast observations must not duplicate an hour")
    errors = calibration_errors if calibration_errors is not None else ()
    radius = conformal_radius(errors, coverage_level)
    outputs = []
    for horizon in (24, 48, 72):
        end = current + timedelta(hours=horizon)
        selected = [(stamp, amount) for stamp, amount in forecast_rows if current < stamp <= end]
        expected_hours = horizon
        observed_hours = len(selected)
        rainfall_mm = sum(amount for _, amount in selected) if selected else None
        risk = None
        if rainfall_mm is not None:
            duration_days = horizon / 24
            threshold = threshold_coefficient_mm_h * duration_days ** (-threshold_exponent)
            intensity = rainfall_mm / horizon
            ratio = intensity / threshold if threshold > 0 else 0
            trigger = {
                f"{horizon}h": {
                    "available": True,
                    "threshold_ratio": ratio,
                }
            }
            risk = hybrid_dynamic_risk(
                susceptibility_score=susceptibility_score,
                rainfall_thresholds=trigger,
                factor_of_safety=factor_of_safety,
                soil_moisture_fraction=soil_moisture_fraction,
                synthetic_data=synthetic_data,
            )
        score = risk["risk_score"] if risk else None
        outputs.append(
            {
                "horizon_hours": horizon,
                "valid_until": end.isoformat(),
                "rainfall_mm": round(rainfall_mm, 3) if rainfall_mm is not None else None,
                "observed_hours": observed_hours,
                "expected_hours": expected_hours,
                "coverage": round(observed_hours / expected_hours, 4),
                "risk_score": score,
                "risk_level": risk["risk_level"] if risk else None,
                "lower": max(0.0, score - radius) if score is not None and radius is not None else None,
                "upper": min(1.0, score + radius) if score is not None and radius is not None else None,
                "uncertainty_method": (
                    "split_conformal_absolute_error"
                    if radius is not None
                    else "unavailable_without_sufficient_calibration"
                ),
            }
        )
    return {
        "as_of": current.isoformat(),
        "forecast_method": "deterministic trigger baseline",
        "coverage_level": coverage_level,
        "calibration_sample_count": len(errors),
        "horizons": outputs,
        "synthetic": synthetic_data,
        "disclaimer": (
            "Synthetic forecast inputs; not for operational decisions. "
            "Follow official IMD, NDMA, and GSI warnings."
            if synthetic_data
            else
            "Forecast risk indices are decision support only. Follow official "
            "IMD, NDMA, and GSI warnings."
        ),
    }


def mapie_regression_intervals(
    estimator: Any,
    calibration_features: Any,
    calibration_targets: Any,
    prediction_features: Any,
    confidence_level: float = 0.9,
) -> list[dict[str, float]]:
    """Conformalize a fitted regressor using MAPIE's split-conformal API."""
    if not 0 < confidence_level < 1:
        raise ValueError("confidence_level must be strictly between 0 and 1")
    try:
        from mapie.regression import SplitConformalRegressor
    except ModuleNotFoundError as exc:
        raise RuntimeError("Install MAPIE with `python -m pip install mapie`.") from exc
    except ImportError as exc:
        raise RuntimeError(f"Unable to load MAPIE or its native dependencies: {exc}") from exc
    conformal = SplitConformalRegressor(
        estimator=estimator,
        confidence_level=confidence_level,
        prefit=True,
    )
    conformal.conformalize(calibration_features, calibration_targets)
    predictions, intervals = conformal.predict_interval(prediction_features)
    bounds = np.asarray(intervals)
    if bounds.ndim == 3:
        lower = bounds[:, 0, 0]
        upper = bounds[:, 1, 0]
    elif bounds.ndim == 2 and bounds.shape[1] == 2:
        lower, upper = bounds[:, 0], bounds[:, 1]
    else:
        raise RuntimeError(f"Unexpected MAPIE interval shape: {bounds.shape}")
    return [
        {"prediction": float(point), "lower": float(lo), "upper": float(hi)}
        for point, lo, hi in zip(np.asarray(predictions).ravel(), lower, upper)
    ]
