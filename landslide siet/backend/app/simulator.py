from __future__ import annotations
from typing import Any, Dict


def simulate_risk(zone: str, rainfall: float, soil_moisture: float, slope: float) -> Dict[str, Any]:
    base_score = 30
    rainfall_component = min(35, rainfall / 2.5)
    moisture_component = min(25, soil_moisture / 2.8)
    slope_component = min(20, slope / 1.8)
    score = int(min(100, base_score + rainfall_component + moisture_component + slope_component))
    if zone.lower() in {"ooty", "wayanad", "darjeeling", "sikkim"}:
        score = min(100, score + 8)
    return {
        "zone": zone,
        "current": score,
        "risk_level": "LOW" if score <= 30 else "MODERATE" if score <= 60 else "HIGH" if score <= 80 else "CRITICAL",
        "rainfall": rainfall,
        "soil_moisture": soil_moisture,
        "slope": slope,
        "summary": "Simulated scenario updated. Risk recalculated immediately.",
        "demo": True,
    }
