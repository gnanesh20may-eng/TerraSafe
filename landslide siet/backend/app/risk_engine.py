from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple

from backend.app.models import classify_risk


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except Exception:
        return default


def calc_weighted_risk(
    weather: Dict[str, Any],
    terrain: Dict[str, Any],
    satellite: Dict[str, Any],
    historical: Dict[str, Any],
) -> Tuple[int, List[str], Dict[str, Any]]:
    rainfall_24 = safe_float(weather.get("rain_24h_mm"), 0.0)
    rainfall_72 = safe_float(weather.get("rain_72h_mm"), 0.0)
    soil_moisture = safe_float(weather.get("soil_moisture"), 0.0)
    slope = safe_float(terrain.get("slope_deg"), 0.0)
    ndvi = safe_float(satellite.get("ndvi"), 0.5)
    hist = safe_float(historical.get("historical_landslides_nearby"), 0.0)
    roads = safe_float(terrain.get("roads_proximity_km"), 10.0)
    settlements = safe_float(terrain.get("settlements_proximity_km"), 10.0)

    score = 0.0
    reasons: List[str] = []

    if rainfall_24 >= 60:
        score += 22
        reasons.append("Heavy rainfall")
    elif rainfall_24 >= 25:
        score += 10

    if rainfall_72 >= 100:
        score += 18
        reasons.append("Extended heavy rainfall")
    elif rainfall_72 >= 50:
        score += 10

    if soil_moisture >= 65:
        score += 15
        reasons.append("High soil moisture")

    if slope >= 25:
        score += 16
        reasons.append("High slope")
    elif slope >= 15:
        score += 8

    if ndvi < 0.45:
        score += 10
        reasons.append("Low vegetation stability")
    elif ndvi < 0.6:
        score += 5

    if hist >= 4:
        score += 18
        reasons.append("Historical landslides nearby")
    elif hist >= 1:
        score += 8

    if roads < 1.0:
        score += 6
    if settlements < 1.0:
        score += 5

    score = max(0.0, min(100.0, score))
    unique_reasons: List[str] = []
    for reason in reasons:
        if reason not in unique_reasons:
            unique_reasons.append(reason)

    return int(round(score)), unique_reasons, {
        "riskScore": int(round(score)),
        "riskLevel": classify_risk(score),
        "updatedAt": datetime.now(timezone.utc).isoformat(),
    }
