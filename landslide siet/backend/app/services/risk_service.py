from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class RiskSignals:
    rainfall_24h_mm: float
    rainfall_7d_mm: float
    soil_moisture_pct: float
    slope_deg: float
    ndvi: float
    elevation_m: float
    historical_landslides_nearby: float = 0.0


def classify_level(score: float) -> str:
    if score < 25:
        return "LOW"
    if score < 50:
        return "WATCH"
    if score < 75:
        return "HIGH"
    return "CRITICAL"


def normalize_score(value: float, lower: float, upper: float) -> float:
    if upper == lower:
        return 0.0
    return max(0.0, min(1.0, (value - lower) / (upper - lower)))


def calculate_risk_score(signals: RiskSignals) -> dict[str, Any]:
    rainfall_score = 0.0
    if signals.rainfall_24h_mm >= 60:
        rainfall_score += 25
    elif signals.rainfall_24h_mm >= 30:
        rainfall_score += 12

    if signals.rainfall_7d_mm >= 150:
        rainfall_score += 20
    elif signals.rainfall_7d_mm >= 80:
        rainfall_score += 10

    moisture_score = 0.0
    if signals.soil_moisture_pct >= 70:
        moisture_score += 18
    elif signals.soil_moisture_pct >= 55:
        moisture_score += 10

    slope_score = 0.0
    if signals.slope_deg >= 30:
        slope_score += 18
    elif signals.slope_deg >= 20:
        slope_score += 10

    vegetation_score = 0.0
    if signals.ndvi < 0.4:
        vegetation_score += 12
    elif signals.ndvi < 0.6:
        vegetation_score += 6

    elevation_score = 0.0
    if signals.elevation_m >= 1500:
        elevation_score += 8

    history_score = 0.0
    if signals.historical_landslides_nearby >= 4:
        history_score += 15
    elif signals.historical_landslides_nearby >= 1:
        history_score += 8

    score = rainfall_score + moisture_score + slope_score + vegetation_score + elevation_score + history_score
    score = max(0.0, min(100.0, score))

    reasons: list[str] = []
    if signals.rainfall_24h_mm >= 60:
        reasons.append("Heavy 24-hour rainfall")
    if signals.soil_moisture_pct >= 70:
        reasons.append("Saturated soil")
    if signals.slope_deg >= 30:
        reasons.append("Steep terrain")
    if signals.ndvi < 0.4:
        reasons.append("Reduced vegetation stability")
    if signals.historical_landslides_nearby >= 1:
        reasons.append("Research indicates landslide history nearby")

    return {
        "score": round(score),
        "level": classify_level(score),
        "confidence": "Moderate",
        "reasons": reasons or ["Baseline terrain and weather conditions are stable"],
        "source": "DEMO RISK MODEL",
        "disclaimer": "This is a decision-support prototype and not an official warning.",
    }


def build_risk_zone_feature(location_name: str, latitude: float, longitude: float, score: float) -> dict[str, Any]:
    zone = classify_level(score)
    radius = 0.015 + (score / 100) * 0.04
    polygon = [
        [longitude - radius, latitude - radius],
        [longitude + radius, latitude - radius],
        [longitude + radius, latitude + radius],
        [longitude - radius, latitude + radius],
        [longitude - radius, latitude - radius],
    ]
    return {
        "type": "Feature",
        "geometry": {"type": "Polygon", "coordinates": [polygon]},
        "properties": {
            "location": location_name,
            "score": round(score),
            "zone": zone,
            "risk_level": zone,
            "source": "DEMO GIS ZONE",
        },
    }


def build_risk_zone_geojson(locations: list[dict[str, Any]], risk_scores: dict[str, float]) -> dict[str, Any]:
    features = []
    for entry in locations:
        loc_id = entry["id"]
        if loc_id in risk_scores:
            score = risk_scores[loc_id]
            features.append(build_risk_zone_feature(entry["name"], entry["latitude"], entry["longitude"], score))
    return {
        "type": "FeatureCollection",
        "features": features,
        "metadata": {
            "source": "DEMO GIS ZONE",
            "disclaimer": "Synthetic demonstration output only. This is not official hazard mapping.",
        },
    }
