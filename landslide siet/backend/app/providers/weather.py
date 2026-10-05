from __future__ import annotations

from datetime import datetime, timedelta, timezone
import math

import httpx

from backend.app.config import OPENMETEO_BASE_URL, OPENMETEO_TIMEOUT_SECONDS
from backend.app.providers.base import (
    LocationRef,
    ProviderUnavailableError,
    WeatherConditions,
    WeatherProvider,
)


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


class OpenMeteoWeatherProvider(WeatherProvider):
    def __init__(
        self,
        base_url: str = OPENMETEO_BASE_URL,
        timeout_seconds: float = OPENMETEO_TIMEOUT_SECONDS,
        client: httpx.Client | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.client = client

    def get_current_weather(self, location: LocationRef) -> WeatherConditions:
        if not -90 <= location.latitude <= 90 or not -180 <= location.longitude <= 180:
            raise ValueError("Location coordinates are outside valid latitude/longitude ranges")

        params = {
            "latitude": location.latitude,
            "longitude": location.longitude,
            "current": "temperature_2m,wind_speed_10m",
            "hourly": "precipitation,soil_moisture_0_to_7cm",
            "past_days": 7,
            "forecast_days": 1,
            "timezone": "UTC",
        }
        try:
            if self.client is None:
                response = httpx.get(
                    f"{self.base_url}/forecast",
                    params=params,
                    timeout=self.timeout_seconds,
                )
            else:
                response = self.client.get(f"{self.base_url}/forecast", params=params)
            response.raise_for_status()
            payload = response.json()
            current = payload["current"]
            hourly = payload["hourly"]
            times = hourly["time"]
            precipitation = hourly["precipitation"]
            moisture = hourly.get("soil_moisture_0_to_7cm", [])
            if not times or len(times) != len(precipitation):
                raise ValueError("Hourly precipitation data is missing or misaligned")

            now = datetime.now(timezone.utc)
            parsed_times = [_parse_utc_time(value) for value in times]
            rainfall_24h = _sum_precipitation(parsed_times, precipitation, now - timedelta(hours=24), now)
            rainfall_7d = _sum_precipitation(parsed_times, precipitation, now - timedelta(days=7), now)
            latest_index = max(
                (index for index, observed_at in enumerate(parsed_times) if observed_at <= now),
                default=None,
            )
            soil_moisture_pct = None
            if latest_index is not None and latest_index < len(moisture):
                raw_moisture = moisture[latest_index]
                if raw_moisture is not None:
                    soil_moisture_pct = _finite_number(raw_moisture, "soil_moisture_0_to_7cm") * 100

            observed_at = str(current["time"])
            return WeatherConditions(
                rainfall_24h_mm=rainfall_24h,
                rainfall_7d_mm=rainfall_7d,
                soil_moisture_pct=soil_moisture_pct,
                wind_speed_kmh=_finite_number(current["wind_speed_10m"], "wind_speed_10m"),
                temperature_c=_finite_number(current["temperature_2m"], "temperature_2m"),
                source="OPEN-METEO API",
                observed_at=observed_at,
            )
        except httpx.HTTPError as error:
            raise ProviderUnavailableError("Open-Meteo weather service is unavailable") from error
        except (KeyError, IndexError, TypeError, ValueError) as error:
            raise ProviderUnavailableError("Open-Meteo returned incomplete or invalid weather data") from error


def _parse_utc_time(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _finite_number(value: object, field: str) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"Open-Meteo returned an invalid {field} value")
    return number


def _sum_precipitation(
    times: list[datetime],
    values: list[float | None],
    start: datetime,
    end: datetime,
) -> float:
    selected = [
        _finite_number(value, "precipitation")
        for observed_at, value in zip(times, values)
        if start < observed_at <= end and value is not None
    ]
    if not selected:
        raise ValueError("Open-Meteo returned no precipitation observations for the requested period")
    if any(value < 0 for value in selected):
        raise ValueError("Open-Meteo returned negative precipitation")
    return round(sum(selected), 2)
