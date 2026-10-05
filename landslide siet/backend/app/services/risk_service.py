from __future__ import annotations

from datetime import datetime, timezone

from backend.app.providers.base import LocationRef
from backend.app.services.environment_service import environment_service


class RiskService:
    def __init__(self, environment_provider=environment_service) -> None:
        self.environment_provider = environment_provider

    def evaluate_location(self, location: LocationRef) -> dict:
        environment = self.environment_provider.get_environment(location)
        weather = environment["weather"]
        terrain = environment["terrain"]

        from backend.app.gis.risk_zones import RiskSignals, calculate_risk_score

        signals = RiskSignals(
            rainfall_24h_mm=float(weather["rainfall_24h_mm"]),
            rainfall_7d_mm=float(weather.get("rainfall_7d_mm", 0.0)),
            soil_moisture_pct=(
                float(weather["soil_moisture_pct"])
                if weather.get("soil_moisture_pct") is not None
                else None
            ),
            slope_deg=float(terrain["slope_deg"]),
            ndvi=float(terrain.get("ndvi", 0.5)),
            elevation_m=float(terrain["elevation_m"]),
            historical_landslides_nearby=1.0 if location.id in {"coonor", "ooty"} else 0.0,
        )
        result = calculate_risk_score(signals)

        return {
            "location": {
                "id": location.id,
                "name": location.name,
                "latitude": location.latitude,
                "longitude": location.longitude,
                "admin_region": location.admin_region,
            },
            "risk": {
                "score": result["score"],
                "level": result["level"],
                "trend": "INCREASING" if result["score"] >= 50 else "STABLE",
                "model_status": "DEMO — weighted heuristic, not a validated model",
            },
            "confidence": {
                "available": False,
                "value": None,
                "reason": "No calibrated model confidence is available.",
            },
            "environment": environment["weather"],
            "terrain": environment["terrain"],
            "contributors": [
                {"factor": "Rainfall", "impact": "HIGH" if weather["rainfall_24h_mm"] >= 30 else "MEDIUM", "direction": "INCREASE"},
                {
                    "factor": "Soil Moisture",
                    "impact": (
                        "UNAVAILABLE"
                        if weather.get("soil_moisture_pct") is None
                        else "HIGH" if weather["soil_moisture_pct"] >= 60 else "MEDIUM"
                    ),
                    "direction": "UNKNOWN" if weather.get("soil_moisture_pct") is None else "INCREASE",
                },
                {"factor": "Slope", "impact": "HIGH" if terrain["slope_deg"] >= 25 else "MEDIUM", "direction": "INCREASE"},
            ],
            "recommendation": {
                "severity": result["level"],
                "message": "Conditions are being monitored. Follow official local guidance and avoid steep vulnerable routes unless necessary.",
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data_status": environment["data_status"],
            "model_source": result["source"],
        }


risk_service = RiskService()
