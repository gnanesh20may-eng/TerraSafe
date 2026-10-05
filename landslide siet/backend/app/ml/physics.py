from __future__ import annotations

import math


def infinite_slope_factor(
    slope_deg: float,
    cohesion_kpa: float,
    unit_weight_kn_m3: float,
    soil_depth_m: float,
    friction_angle_deg: float,
    pore_pressure_ratio: float = 0.0,
) -> float:
    """Return an illustrative infinite-slope factor of safety, not a forecast."""
    if not 0 < slope_deg < 90 or not 0 < friction_angle_deg < 90:
        raise ValueError("slope and friction angles must be between 0 and 90 degrees")
    if unit_weight_kn_m3 <= 0 or soil_depth_m <= 0:
        raise ValueError("unit weight and soil depth must be positive")
    if cohesion_kpa < 0 or not 0 <= pore_pressure_ratio <= 1:
        raise ValueError("cohesion must be nonnegative and pore pressure ratio in [0, 1]")
    slope = math.radians(slope_deg)
    friction = math.radians(friction_angle_deg)
    cohesion_term = cohesion_kpa / (unit_weight_kn_m3 * soil_depth_m * math.sin(slope) * math.cos(slope))
    friction_term = (1 - pore_pressure_ratio) * math.tan(friction) / math.tan(slope)
    return cohesion_term + friction_term


def rainfall_id_trigger(rainfall_mm: float, duration_hours: float, threshold_mm_per_hour: float = 1.0) -> dict[str, float | bool]:
    if rainfall_mm < 0 or duration_hours <= 0 or threshold_mm_per_hour <= 0:
        raise ValueError("rainfall must be nonnegative and duration/threshold positive")
    intensity = rainfall_mm / duration_hours
    return {
        "intensity_mm_per_hour": intensity,
        "threshold_mm_per_hour": threshold_mm_per_hour,
        "exceeded": intensity >= threshold_mm_per_hour,
        "normalized_trigger": min(1.0, intensity / threshold_mm_per_hour),
    }