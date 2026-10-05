"""Transparent rainfall, slope-stability, and dynamic risk calculations."""

from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone
from typing import Any, Mapping, Sequence

RAIN_WINDOWS_HOURS = (1, 24, 72, 168, 720)


def _utc_datetime(value: str | datetime) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00")) if isinstance(value, str) else value
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def antecedent_rainfall(
    observations: Sequence[Mapping[str, Any]],
    as_of: str | datetime | None = None,
) -> dict[str, dict[str, Any]]:
    """Sum hourly precipitation and expose coverage rather than treating gaps as zero."""
    current = _utc_datetime(as_of or datetime.now(timezone.utc))
    parsed: list[tuple[datetime, float]] = []
    seen_timestamps: set[datetime] = set()
    for record in observations:
        timestamp = _utc_datetime(record["timestamp"])
        amount = float(record["precipitation_mm"])
        if not math.isfinite(amount) or amount < 0:
            raise ValueError("precipitation_mm values must be finite and non-negative")
        if timestamp > current:
            continue
        if timestamp in seen_timestamps:
            raise ValueError("rainfall observations must not duplicate a timestamp")
        seen_timestamps.add(timestamp)
        parsed.append((timestamp, amount))

    result: dict[str, dict[str, Any]] = {}
    for window in RAIN_WINDOWS_HOURS:
        start = current - timedelta(hours=window)
        window_records = [(stamp, amount) for stamp, amount in parsed if start < stamp <= current]
        observed_hours = len(
            {
                stamp.replace(minute=0, second=0, microsecond=0)
                for stamp, _ in window_records
            }
        )
        result[f"{window}h"] = {
            "rainfall_mm": round(sum(amount for _, amount in window_records), 3)
            if window_records
            else None,
            "observed_hours": observed_hours,
            "observation_count": len(window_records),
            "expected_hours": window,
            "coverage": round(min(1.0, observed_hours / window), 4),
            "complete": observed_hours == window,
        }
    return result


def intensity_duration_thresholds(
    rainfall: Mapping[str, Mapping[str, Any]],
    *,
    coefficient_mm_per_hour: float = 30.0,
    exponent: float = 0.5,
) -> dict[str, dict[str, Any]]:
    """Compare observed average intensity to configurable I = a * D**(-b).

    Defaults are demonstration values only; use locally validated thresholds
    before operational interpretation.
    """
    if coefficient_mm_per_hour <= 0 or exponent < 0:
        raise ValueError("threshold coefficient must be positive and exponent non-negative")
    result = {}
    for window in (1, 24, 72):
        key = f"{window}h"
        data = rainfall.get(key)
        if not data or data.get("rainfall_mm") is None:
            result[key] = {"available": False, "exceeded": None}
            continue
        duration_days = window / 24
        threshold = coefficient_mm_per_hour * duration_days ** (-exponent)
        observed_intensity = float(data["rainfall_mm"]) / window
        ratio = observed_intensity / threshold if threshold else 0.0
        result[key] = {
            "available": True,
            "observed_intensity_mm_h": round(observed_intensity, 4),
            "threshold_intensity_mm_h": round(threshold, 4),
            "threshold_ratio": round(ratio, 4),
            "exceeded": ratio >= 1,
        }
    return result


def infinite_slope_factor_of_safety(
    *,
    slope_deg: float,
    soil_depth_m: float,
    unit_weight_kn_m3: float,
    friction_angle_deg: float,
    cohesion_kpa: float,
    saturation_ratio: float,
) -> float:
    """Estimate infinite-slope FoS; parameters are assumptions, not measured soil."""
    values = (slope_deg, soil_depth_m, unit_weight_kn_m3, friction_angle_deg, cohesion_kpa)
    if not all(math.isfinite(value) for value in values):
        raise ValueError("slope and soil parameters must be finite")
    if soil_depth_m <= 0 or unit_weight_kn_m3 <= 0 or cohesion_kpa < 0:
        raise ValueError("soil depth and unit weight must be positive; cohesion non-negative")
    if not 0 <= saturation_ratio <= 1:
        raise ValueError("saturation_ratio must be between 0 and 1")
    if not 0 <= slope_deg < 90 or not 0 < friction_angle_deg < 90:
        raise ValueError("slope must be in [0, 90) and friction angle in (0, 90)")
    beta = math.radians(slope_deg)
    friction = math.radians(friction_angle_deg)
    normal_stress = unit_weight_kn_m3 * soil_depth_m * math.cos(beta) ** 2
    pore_pressure = saturation_ratio * 9.81 * soil_depth_m * math.cos(beta) ** 2
    resisting = cohesion_kpa + (normal_stress - pore_pressure) * math.tan(friction)
    driving = unit_weight_kn_m3 * soil_depth_m * math.sin(beta) * math.cos(beta)
    if driving <= 1e-9:
        return math.inf
    return max(0.0, resisting / driving)


def earthquake_trigger_score(
    events: Sequence[Mapping[str, Any]],
    *,
    latitude: float,
    longitude: float,
    influence_radius_km: float = 150,
) -> float:
    """Map USGS GeoJSON event magnitude/distance to an uncalibrated 0–1 trigger."""
    if not -90 <= latitude <= 90 or not -180 <= longitude <= 180:
        raise ValueError("latitude or longitude is outside WGS84 bounds")
    if influence_radius_km <= 0:
        raise ValueError("influence_radius_km must be positive")
    scores = []
    for event in events:
        properties = event.get("properties", {})
        coordinates = event.get("geometry", {}).get("coordinates", [])
        if len(coordinates) < 2 or properties.get("mag") is None:
            continue
        event_lon, event_lat = float(coordinates[0]), float(coordinates[1])
        magnitude = float(properties["mag"])
        if not math.isfinite(magnitude):
            continue
        delta_lat = math.radians(event_lat - latitude)
        delta_lon = math.radians(event_lon - longitude)
        lat1, lat2 = math.radians(latitude), math.radians(event_lat)
        haversine = (
            math.sin(delta_lat / 2) ** 2
            + math.cos(lat1) * math.cos(lat2) * math.sin(delta_lon / 2) ** 2
        )
        distance_km = 6371.0 * 2 * math.asin(min(1.0, math.sqrt(haversine)))
        magnitude_score = min(1.0, max(0.0, (magnitude - 1.0) / 6.0))
        distance_score = min(1.0, max(0.0, 1 - distance_km / influence_radius_km))
        scores.append(magnitude_score * distance_score)
    return max(scores, default=0.0)


def hybrid_dynamic_risk(
    *,
    susceptibility_score: float,
    rainfall_thresholds: Mapping[str, Mapping[str, Any]] | None = None,
    factor_of_safety: float | None = None,
    soil_moisture_fraction: float | None = None,
    earthquake_trigger_score: float | None = None,
    synthetic_data: bool = False,
) -> dict[str, Any]:
    """Combine static susceptibility and live triggers as a transparent risk index."""
    if not 0 <= susceptibility_score <= 1:
        raise ValueError("susceptibility_score must be between 0 and 1")
    components: dict[str, float | None] = {
        "susceptibility": float(susceptibility_score),
        "rainfall": None,
        "slope_instability": None,
        "soil_moisture": None,
        "earthquake": None,
    }
    weights = {
        "susceptibility": 0.45,
        "rainfall": 0.30,
        "slope_instability": 0.15,
        "soil_moisture": 0.05,
        "earthquake": 0.05,
    }
    available_thresholds = [
        float(item["threshold_ratio"])
        for item in (rainfall_thresholds or {}).values()
        if item.get("available") and item.get("threshold_ratio") is not None
    ]
    if available_thresholds:
        components["rainfall"] = min(1.0, max(0.0, max(available_thresholds) / 2))
    if factor_of_safety is not None:
        if factor_of_safety < 0 or math.isnan(factor_of_safety):
            raise ValueError("factor_of_safety must be non-negative")
        components["slope_instability"] = (
            0.0
            if math.isinf(factor_of_safety)
            else min(1.0, max(0.0, (1.5 - factor_of_safety) / 1.5))
        )
    if soil_moisture_fraction is not None:
        if not 0 <= soil_moisture_fraction <= 1:
            raise ValueError("soil_moisture_fraction must be between 0 and 1")
        components["soil_moisture"] = min(
            1.0, max(0.0, (soil_moisture_fraction - 0.2) / 0.4)
        )
    if earthquake_trigger_score is not None:
        if not 0 <= earthquake_trigger_score <= 1:
            raise ValueError("earthquake_trigger_score must be between 0 and 1")
        components["earthquake"] = earthquake_trigger_score

    active_weight = sum(weights[name] for name, value in components.items() if value is not None)
    score = sum(
        weights[name] * value
        for name, value in components.items()
        if value is not None
    ) / active_weight
    level = (
        "Green"
        if score < 0.25
        else "Yellow"
        if score < 0.5
        else "Orange"
        if score < 0.75
        else "Red"
    )
    reasons = [
        f"{name.replace('_', ' ').title()} contributes {value:.2f} on the 0–1 index."
        for name, value in components.items()
        if value is not None and value >= 0.5
    ]
    if not reasons:
        reasons.append("No supplied dynamic trigger is currently elevated.")
    return {
        "risk_score": round(score, 4),
        "risk_level": level,
        "components": components,
        "reasons": reasons,
        "calibrated_probability": False,
        "synthetic": synthetic_data,
        "disclaimer": (
            "Synthetic demonstration output. Not for operational decisions. "
            "Follow official IMD, NDMA, and GSI warnings."
            if synthetic_data
            else "Decision support only; follow official IMD, NDMA, and GSI warnings."
        ),
    }
