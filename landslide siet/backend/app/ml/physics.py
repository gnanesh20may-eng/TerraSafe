from __future__ import annotations

import math
from typing import Any


def infinite_slope_factor_of_safety(
    *,
    slope_deg: float,
    cohesion_kpa: float,
    unit_weight_kn_m3: float,
    soil_depth_m: float,
    friction_angle_deg: float,
    saturation_ratio: float,
    water_unit_weight_kn_m3: float = 9.81,
) -> float:
    values = (slope_deg, cohesion_kpa, unit_weight_kn_m3, soil_depth_m, friction_angle_deg, saturation_ratio, water_unit_weight_kn_m3)
    if not all(math.isfinite(value) for value in values):
        raise ValueError("infinite-slope inputs must be finite")
    if not 0 < slope_deg < 90 or not 0 <= friction_angle_deg < 90:
        raise ValueError("slope and friction angles are outside physical ranges")
    if cohesion_kpa < 0 or unit_weight_kn_m3 <= 0 or soil_depth_m <= 0:
        raise ValueError("soil strength, unit weight, and depth must be valid")
    if not 0 <= saturation_ratio <= 1 or water_unit_weight_kn_m3 <= 0:
        raise ValueError("saturation ratio or water unit weight is outside valid range")

    beta = math.radians(slope_deg)
    phi = math.radians(friction_angle_deg)
    driving_stress = unit_weight_kn_m3 * soil_depth_m * math.sin(beta) * math.cos(beta)
    cohesion_term = cohesion_kpa / driving_stress
    friction_term = (
        1 - saturation_ratio * water_unit_weight_kn_m3 / unit_weight_kn_m3
    ) * math.tan(phi) / math.tan(beta)
    return cohesion_term + friction_term


def rainfall_intensity_duration_indicator(
    *,
    rainfall_mm: float,
    duration_hours: float,
    threshold_a: float,
    threshold_b: float,
) -> dict[str, Any]:
    values = (rainfall_mm, duration_hours, threshold_a, threshold_b)
    if not all(math.isfinite(value) for value in values):
        raise ValueError("rainfall threshold inputs must be finite")
    if rainfall_mm < 0 or duration_hours <= 0 or threshold_a <= 0 or threshold_b < 0:
        raise ValueError("rainfall and intensity-duration parameters are invalid")
    observed_intensity = rainfall_mm / duration_hours
    threshold_intensity = threshold_a * duration_hours ** (-threshold_b)
    ratio = observed_intensity / threshold_intensity
    return {
        "observed_intensity_mm_h": observed_intensity,
        "threshold_intensity_mm_h": threshold_intensity,
        "threshold_ratio": ratio,
        "exceeds_threshold": ratio >= 1,
        "status": "SCAFFOLD — threshold coefficients require local calibration",
    }


def factor_safety_risk_component(
    factor_of_safety: float,
    *,
    failure_reference: float,
    safe_reference: float,
) -> float:
    if not all(math.isfinite(value) for value in (factor_of_safety, failure_reference, safe_reference)):
        raise ValueError("factor-of-safety references must be finite")
    if safe_reference <= failure_reference:
        raise ValueError("safe_reference must exceed failure_reference")
    return max(0.0, min(1.0, (safe_reference - factor_of_safety) / (safe_reference - failure_reference)))


def combine_hybrid_components(
    *,
    model_probability: float,
    physics_component: float,
    rainfall_component: float,
    weights: dict[str, float],
) -> dict[str, Any]:
    components = {
        "model": model_probability,
        "physics": physics_component,
        "rainfall": rainfall_component,
    }
    if set(weights) != set(components):
        raise ValueError("weights must define model, physics, and rainfall components")
    if not all(0 <= value <= 1 and math.isfinite(value) for value in components.values()):
        raise ValueError("hybrid component inputs must be finite values in [0, 1]")
    if not all(value >= 0 and math.isfinite(value) for value in weights.values()):
        raise ValueError("hybrid weights must be finite and non-negative")
    weight_total = sum(weights.values())
    if weight_total <= 0:
        raise ValueError("at least one hybrid weight must be positive")
    score = sum(components[key] * weights[key] for key in components) / weight_total
    return {
        "score": round(score * 100, 2),
        "components": components,
        "weights": weights,
        "status": "SIMULATED — weights and thresholds are not calibrated for operations",
    }
