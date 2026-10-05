from __future__ import annotations
from typing import Any, Dict, List


def generate_alerts(risk_score: int, zone_name: str) -> Dict[str, Any]:
    level = "LOW" if risk_score <= 30 else "MODERATE" if risk_score <= 60 else "HIGH" if risk_score <= 80 else "CRITICAL"
    if level == "CRITICAL":
        message = (
            "CRITICAL LANDSLIDE WARNING\nZone: " + zone_name + "\nRisk: " + str(risk_score) + "/100\nMain reasons: "
            "Heavy rainfall, high soil moisture, steep terrain.\nRecommended action: Inspect vulnerable locations and prepare evacuation measures."
        )
        confidence = 91
    elif level == "HIGH":
        message = "HIGH RISK ALERT. Heavy rainfall and steep terrain are increasing landslide risk."
        confidence = 79
    elif level == "MODERATE":
        message = "MODERATE RISK. Continue monitoring and maintain increased inspection frequency."
        confidence = 68
    else:
        message = "LOW RISK. Conditions remain stable. Continue routine monitoring."
        confidence = 58

    return {
        "level": level,
        "risk_score": risk_score,
        "confidence": confidence,
        "message": message,
        "timestamp": "2026-10-05T12:00:00Z",
        "status": "active" if level in {"HIGH", "CRITICAL"} else "monitoring",
    }
