from __future__ import annotations

from backend.app.providers.base import LocationRef, SatelliteObservation, TerrainFeatures, WeatherConditions
from backend.app.providers.weather import DemoWeatherProvider
from backend.app.providers.terrain import DemoTerrainProvider
from backend.app.providers.satellite import DemoSatelliteProvider


class EnvironmentalSnapshot:
    def __init__(
        self,
        location: LocationRef,
        weather: WeatherConditions,
        terrain: TerrainFeatures,
        satellite: SatelliteObservation,
    ) -> None:
        self.location = location
        self.weather = weather
        self.terrain = terrain
        self.satellite = satellite


class EnvironmentService:
    def __init__(
        self,
        weather_provider=None,
        terrain_provider=None,
        satellite_provider=None,
    ) -> None:
        self.weather_provider = weather_provider or DemoWeatherProvider()
        self.terrain_provider = terrain_provider or DemoTerrainProvider()
        self.satellite_provider = satellite_provider or DemoSatelliteProvider()

    def build_environment_snapshot(self, location: LocationRef) -> EnvironmentalSnapshot:
        weather = self.weather_provider.get_current_weather(location)
        terrain = self.terrain_provider.get_terrain_features(location)
        satellite = self.satellite_provider.get_satellite_observation(location)
        return EnvironmentalSnapshot(location=location, weather=weather, terrain=terrain, satellite=satellite)

    def build_response(self, location: LocationRef) -> dict:
        snapshot = self.build_environment_snapshot(location)
        return {
            "location": {
                "id": snapshot.location.id,
                "name": snapshot.location.name,
                "latitude": snapshot.location.latitude,
                "longitude": snapshot.location.longitude,
                "admin_region": snapshot.location.admin_region,
            },
            "weather": {
                "rainfall_24h_mm": snapshot.weather.rainfall_24h_mm,
                "rainfall_7d_mm": snapshot.weather.rainfall_7d_mm,
                "soil_moisture_pct": snapshot.weather.soil_moisture_pct,
                "wind_speed_kmh": snapshot.weather.wind_speed_kmh,
                "temperature_c": snapshot.weather.temperature_c,
                "source": snapshot.weather.source,
            },
            "terrain": {
                "elevation_m": snapshot.terrain.elevation_m,
                "slope_deg": snapshot.terrain.slope_deg,
                "curvature": snapshot.terrain.curvature,
                "ndvi": snapshot.terrain.ndvi,
                "land_cover": snapshot.terrain.land_cover,
                "source": snapshot.terrain.source,
            },
            "satellite": {
                "cloud_cover_pct": snapshot.satellite.cloud_cover_pct,
                "ndvi": snapshot.satellite.ndvi,
                "ndwi": snapshot.satellite.ndwi,
                "land_cover": snapshot.satellite.land_cover,
                "source": snapshot.satellite.source,
            },
            "last_updated": "2026-10-05T12:00:00Z",
            "data_status": "DEMO DATA",
        }
