from __future__ import annotations

import httpx

from backend.app.providers.base import LocationRef, WeatherConditions, WeatherProvider
from backend.app.config import OPENMETEO_BASE_URL


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
            source="demo",
        )


class OpenMeteoWeatherProvider(WeatherProvider):
    def __init__(self, fallback: WeatherProvider | None = None) -> None:
        self.fallback = fallback or DemoWeatherProvider()

    def get_current_weather(self, location: LocationRef) -> WeatherConditions:
        try:
            response = httpx.get(
                f"{OPENMETEO_BASE_URL.rstrip('/')}/forecast",
                params={
                    "latitude": location.latitude,
                    "longitude": location.longitude,
                    "hourly": "precipitation,soil_moisture_0_to_7cm",
                    "past_days": 7,
                    "forecast_days": 1,
                    "timezone": "auto",
                },
                timeout=5.0,
            )
            response.raise_for_status()
            hourly = response.json()["hourly"]
            precipitation = hourly["precipitation"]
            moisture = hourly["soil_moisture_0_to_7cm"]
            if len(precipitation) < 168 or len(moisture) == 0:
                raise ValueError("Open-Meteo returned insufficient hourly observations")
            recent_moisture = next(value for value in reversed(moisture) if value is not None)
            demo = self.fallback.get_current_weather(location)
            return WeatherConditions(
                rainfall_24h_mm=sum(float(value or 0) for value in precipitation[-24:]),
                rainfall_7d_mm=sum(float(value or 0) for value in precipitation[-168:]),
                soil_moisture_pct=float(recent_moisture) * 100,
                wind_speed_kmh=demo.wind_speed_kmh,
                temperature_c=demo.temperature_c,
                source="open-meteo",
            )
        except (httpx.HTTPError, KeyError, TypeError, ValueError, StopIteration):
            return self.fallback.get_current_weather(location)
