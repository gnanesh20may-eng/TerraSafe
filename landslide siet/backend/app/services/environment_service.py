from __future__ import annotations

from datetime import datetime, timezone

from backend.app.config import DEMO_MODE
from backend.app.providers.base import LocationRef
from backend.app.providers.satellite import DemoSatelliteProvider
from backend.app.providers.terrain import DemoTerrainProvider
from backend.app.providers.weather import OpenMeteoWeatherProvider


class EnvironmentService:
    def __init__(
        self,
        weather_provider=None,
        terrain_provider=None,
        satellite_provider=None,
    ) -> None:
        self.weather_provider = weather_provider or OpenMeteoWeatherProvider()
        self.terrain_provider = terrain_provider or DemoTerrainProvider()
        self.satellite_provider = satellite_provider or DemoSatelliteProvider()

    def get_environment(self, location: LocationRef) -> dict:
        weather = self.weather_provider.get_current_weather(location)
        terrain = self.terrain_provider.get_terrain_features(location)
        satellite = self.satellite_provider.get_satellite_observation(location)

        source_names = [weather.source, terrain.source, satellite.source]
        demo_sources = [source for source in source_names if source.upper().startswith("DEMO")]
        if len(demo_sources) == len(source_names):
            data_status = "DEMO DATA"
        elif demo_sources:
            data_status = "MIXED LIVE/DEMO DATA"
        else:
            data_status = "LIVE DATA"

        return {
            "location": {
                "id": location.id,
                "name": location.name,
                "latitude": location.latitude,
                "longitude": location.longitude,
                "admin_region": location.admin_region,
            },
            "weather": {
                "rainfall_24h_mm": weather.rainfall_24h_mm,
                "rainfall_7d_mm": weather.rainfall_7d_mm,
                "soil_moisture_pct": weather.soil_moisture_pct,
                "wind_speed_kmh": weather.wind_speed_kmh,
                "temperature_c": weather.temperature_c,
                "source": weather.source,
                "observed_at": weather.observed_at,
            },
            "terrain": {
                "elevation_m": terrain.elevation_m,
                "slope_deg": terrain.slope_deg,
                "curvature": terrain.curvature,
                "ndvi": terrain.ndvi,
                "land_cover": terrain.land_cover,
                "source": terrain.source,
            },
            "satellite": {
                "cloud_cover_pct": satellite.cloud_cover_pct,
                "ndvi": satellite.ndvi,
                "ndwi": satellite.ndwi,
                "land_cover": satellite.land_cover,
                "source": satellite.source,
            },
            "last_updated": "2026-10-05T12:00:00Z",
            "data_status": (
                "LIVE WEATHER + DEMO TERRAIN/SATELLITE"
                if weather.source == "open-meteo"
                else "DEMO DATA"
            ),
        }


environment_service = EnvironmentService()
