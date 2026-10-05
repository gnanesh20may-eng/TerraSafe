from __future__ import annotations

from backend.app.providers.base import LocationRef
from backend.app.services.risk_service import RiskService


class PartialEnvironmentProvider:
    def get_environment(self, _location):
        return {
            "location": {"id": "test", "name": "Test", "latitude": 11.0, "longitude": 76.0, "admin_region": "Test region"},
            "weather": {
                "rainfall_24h_mm": 12.0,
                "rainfall_7d_mm": 38.0,
                "soil_moisture_pct": None,
                "wind_speed_kmh": 9.0,
                "temperature_c": 24.0,
                "source": "OPEN-METEO API",
            },
            "terrain": {
                "elevation_m": 400.0,
                "slope_deg": 14.0,
                "curvature": 0.0,
                "ndvi": 0.7,
                "land_cover": "DEMO",
                "source": "DEMO TERRAIN PROVIDER",
            },
            "satellite": {"source": "DEMO SATELLITE PROVIDER"},
            "data_status": "MIXED LIVE/DEMO DATA",
        }


def test_risk_service_handles_missing_moisture_without_fabricating_confidence():
    service = RiskService(environment_provider=PartialEnvironmentProvider())
    result = service.evaluate_location(LocationRef("test", "Test", 11.0, 76.0))

    assert result["confidence"]["available"] is False
    assert result["confidence"]["value"] is None
    assert result["data_status"] == "MIXED LIVE/DEMO DATA"
    assert result["risk"]["model_status"].startswith("DEMO")
    moisture = next(item for item in result["contributors"] if item["factor"] == "Soil Moisture")
    assert moisture["impact"] == "UNAVAILABLE"
    assert moisture["direction"] == "UNKNOWN"
