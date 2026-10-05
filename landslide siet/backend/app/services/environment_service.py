from __future__ import annotations

from backend.app.providers.base import LocationRef, SatelliteObservation, TerrainFeatures, WeatherConditions, WeatherProvider, TerrainProvider, SatelliteProvider


class DemoWeatherProvider(WeatherProvider):
    def get_current_weather(self, location: LocationRef) -> WeatherConditions:
        rainfall_map = {
            "coonor": (42.0, 156.0, 68.0, 18.0, 23.4),
            "ooty": (27.0, 98.0, 58.0, 15.0, 21.8),
            "kodaikanal": (14.0, 60.0, 46.0, 12.0, 19.5),
        }
        rainfall_24h, rainfall_7d, soil, wind, temp = rainfall_map.get(location.id, (18.0, 72.0, 50.0, 13.0, 22.0))
        return WeatherConditions(
            rainfall_24h_mm=rainfall_24h,
            rainfall_7d_mm=rainfall_7d,
            soil_moisture_pct=soil,
            wind_speed_kmh=wind,
            temperature_c=temp,
            source="DEMO WEATHER PROVIDER",
        )


class DemoTerrainProvider(TerrainProvider):
    def get_terrain_features(self, location: LocationRef) -> TerrainFeatures:
        terrain_map = {
            "coonor": (520.0, 27.0, 0.92, 0.64, "steep-vegetated-slope"),
            "ooty": (2330.0, 18.0, 0.62, 0.58, "montane-forest"),
            "kodaikanal": (2090.0, 12.0, 0.35, 0.72, "temperate-forest"),
        }
        elevation, slope, curvature, ndvi, cover = terrain_map.get(location.id, (800.0, 15.0, 0.5, 0.6, "mixed-cover"))
        return TerrainFeatures(
            elevation_m=elevation,
            slope_deg=slope,
            curvature=curvature,
            ndvi=ndvi,
            land_cover=cover,
            source="DEMO TERRAIN PROVIDER",
        )


class DemoSatelliteProvider(SatelliteProvider):
    def get_satellite_observation(self, location: LocationRef) -> SatelliteObservation:
        obs_map = {
            "coonor": (18.0, 0.66, 0.42, "vegetated-slope"),
            "ooty": (25.0, 0.59, 0.31, "mixed-forest"),
            "kodaikanal": (12.0, 0.71, 0.23, "temperate-vegetation"),
        }
        cloud_cover, ndvi, ndwi, cover = obs_map.get(location.id, (20.0, 0.60, 0.28, "mixed-cover"))
        return SatelliteObservation(
            cloud_cover_pct=cloud_cover,
            ndvi=ndvi,
            ndwi=ndwi,
            land_cover=cover,
            source="DEMO SATELLITE PROVIDER",
        )
