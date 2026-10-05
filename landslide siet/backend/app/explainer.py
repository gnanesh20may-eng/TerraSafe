from __future__ import annotations
from typing import Any, Dict, List


def explain_risk(data: Dict[str, Any], score: int) -> Dict[str, Any]:
    rainfall = float(data.get("rainfall_24h", 0))
    soil = float(data.get("soil_moisture", 0))
    slope = float(data.get("slope_deg", 0))
    ndvi = float(data.get("ndvi", 0.5))
    hist = float(data.get("historical_landslides_nearby", 0))

    contribution = {
        "Rainfall": min(35, max(8, rainfall / 3.2)),
        "Soil Moisture": min(30, max(5, soil / 3)),
        "Slope": min(22, max(6, slope / 2.1)),
        "History": min(18, max(4, hist * 3.4)),
        "Vegetation": min(15, max(4, (0.6 - ndvi) * 30)),
    }

    reasons = []
    if rainfall >= 60:
        reasons.append("Heavy rainfall")
    if soil >= 65:
        reasons.append("High soil moisture")
    if slope >= 25:
        reasons.append("Steep terrain")
    if hist >= 3:
        reasons.append("Historical landslides nearby")
    if ndvi < 0.45:
        reasons.append("Low vegetation stability")

    reduction = []
    if rainfall > 0:
        reduction.append("Rainfall intensity decreases")
    if soil > 0:
        reduction.append("Soil moisture falls to moderate levels")
    if slope > 0:
        reduction.append("Slope remains under a critical threshold")

    return {
        "score": score,
        "risk_level": "CRITICAL" if score >= 81 else "HIGH" if score >= 61 else "MODERATE" if score >= 31 else "LOW",
        "contributing_factors": contribution,
        "reasons": reasons or ["Stable conditions observed"],
        "counterfactual": "Risk could fall below the critical threshold if rainfall intensity decreases and soil moisture returns to moderate levels.",
        "reduction_actions": reduction or ["Continue monitoring and maintain normal drainage management"],
    }
