from __future__ import annotations

from backend.app.providers.base import LocationRef
from backend.app.services.environment_service import environment_service


class RiskService:
    def evaluate_location(self, location: LocationRef) -> dict:
        environment = environment_service.get_environment(location)
        weather = environment["weather"]
        terrain = environment["terrain"]

        from backend.app.gis.risk_zones import RiskSignals, calculate_risk_score

        signals = RiskSignals(
            rainfall_24h_mm=float(weather["rainfall_24h_mm"]),
            rainfall_7d_mm=float(weather.get("rainfall_7d_mm", 0.0)),
            soil_moisture_pct=float(weather["soil_moisture_pct"]),
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
            },
            "confidence": {"available": True, "value": 0.8},
            "environment": environment["weather"],
            "terrain": environment["terrain"],
            "contributors": [
                {"factor": "Rainfall", "impact": "HIGH" if weather["rainfall_24h_mm"] >= 30 else "MEDIUM", "direction": "INCREASE"},
                {"factor": "Soil Moisture", "impact": "HIGH" if weather["soil_moisture_pct"] >= 60 else "MEDIUM", "direction": "INCREASE"},
                {"factor": "Slope", "impact": "HIGH" if terrain["slope_deg"] >= 25 else "MEDIUM", "direction": "INCREASE"},
            ],
            "recommendation": {
                "severity": result["level"],
                "message": "Conditions are being monitored. Follow official local guidance and avoid steep vulnerable routes unless necessary.",
            },
            "timestamp": "2026-10-05T12:00:00Z",
        }


risk_service = RiskService()
