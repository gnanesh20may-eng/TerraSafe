from __future__ import annotations

from backend.app.providers.base import LocationRef, WeatherConditions, WeatherProvider


class DemoWeatherProvider(WeatherProvider):
    def get_current_weather(self, location: LocationRef) -> WeatherConditions:
        rainfall_map = {
            "coonor": (42.0, 156.0, 68.0, 18.0, 23.4),
            "ooty": (27.0, 98.0, 58.0, 15.0, 21.8),
            "kodaikanal": (14.0, 60.0, 46.0, 12.0, 19.5),
        }
        rainfall_24h, rainfall_7d, soil_moisture, wind_speed, temperature = rainfall_map.get(
            location.id,
            (18.0, 72.0, 50.0, 13.0, 22.0),
        )
        return WeatherConditions(
            rainfall_24h_mm=rainfall_24h,
            rainfall_7d_mm=rainfall_7d,
            soil_moisture_pct=soil_moisture,
            wind_speed_kmh=wind_speed,
            temperature_c=temperature,
            source="DEMO WEATHER PROVIDER",
        )
