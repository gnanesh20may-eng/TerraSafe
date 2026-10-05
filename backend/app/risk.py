"""Open-Meteo weather lookup and explicitly synthetic map zones."""

from __future__ import annotations

import asyncio
import logging
import math
from datetime import date, datetime, timedelta, timezone
from typing import Any

import httpx

LOGGER = logging.getLogger(__name__)
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
OPEN_METEO_TIMEOUT_SECONDS = 5.0
NILGIRIS_BOUNDS = (76.2, 11.1, 76.9, 11.6)
GRID_SIZE = 10
ZONE_COUNT = 3


def _finite_number(value: Any, name: str, *, minimum: float = 0) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool):
        raise ValueError(f"{name} must be numeric")
    number = float(value)
    if not math.isfinite(number) or number < minimum:
        raise ValueError(f"{name} must be finite and at least {minimum}")
    return number


async def fetch_open_meteo_weather(
    latitude: float,
    longitude: float,
) -> dict[str, Any]:
    """Fetch recent hourly weather with a hard five-second client timeout."""
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "precipitation,soil_moisture_0_to_7cm",
        "daily": "precipitation_sum",
        "past_days": 7,
        "forecast_days": 1,
        "timezone": "UTC",
    }
    try:
        async with asyncio.timeout(OPEN_METEO_TIMEOUT_SECONDS):
            async with httpx.AsyncClient(
                timeout=httpx.Timeout(OPEN_METEO_TIMEOUT_SECONDS)
            ) as client:
                response = await client.get(OPEN_METEO_URL, params=params)
                response.raise_for_status()
                payload = response.json()
    except (httpx.TimeoutException, TimeoutError):
        LOGGER.warning("Open-Meteo request timed out after %s seconds", OPEN_METEO_TIMEOUT_SECONDS)
        return {"status": "DEMO", "reason": "timeout"}
    except httpx.RequestError as exc:
        LOGGER.warning("Open-Meteo request failed: %s", type(exc).__name__)
        return {"status": "DEMO", "reason": "unavailable"}
    except httpx.HTTPStatusError as exc:
        LOGGER.warning("Open-Meteo returned HTTP %s", exc.response.status_code)
        return {"status": "DEMO", "reason": "upstream_error"}

    try:
        if not isinstance(payload, dict):
            raise ValueError("response must be an object")
        hourly = payload["hourly"]
        times = hourly["time"]
        precipitation = hourly["precipitation"]
        soil_moisture = hourly["soil_moisture_0_to_7cm"]
        if not (
            isinstance(times, list)
            and isinstance(precipitation, list)
            and isinstance(soil_moisture, list)
            and len(times) == len(precipitation) == len(soil_moisture)
        ):
            raise ValueError("hourly weather arrays are missing or inconsistent")

        now = datetime.now(timezone.utc)
        start = now - timedelta(days=7)
        observations: list[dict[str, Any]] = []
        latest_soil: float | None = None
        latest_precipitation: float | None = None
        latest_timestamp: datetime | None = None
        for timestamp_value, rain_value, soil_value in zip(
            times, precipitation, soil_moisture
        ):
            if not isinstance(timestamp_value, str):
                raise ValueError("hourly time values must be strings")
            timestamp = datetime.fromisoformat(
                timestamp_value.replace("Z", "+00:00")
            ).astimezone(timezone.utc)
            if timestamp > now or timestamp < start:
                continue
            rain = _finite_number(rain_value, "precipitation")
            soil = _finite_number(soil_value, "soil moisture")
            if rain is not None:
                observations.append(
                    {
                        "timestamp": timestamp.isoformat(),
                        "precipitation_mm": rain,
                    }
                )
                latest_precipitation = rain
            if soil is not None:
                if soil > 1:
                    raise ValueError("soil moisture must be a fraction in [0, 1]")
                latest_soil = soil
            if rain is not None or soil is not None:
                latest_timestamp = timestamp

        daily = payload.get("daily")
        if not isinstance(daily, dict):
            raise ValueError("daily weather is missing")
        daily_dates = daily.get("time")
        daily_precipitation = daily.get("precipitation_sum")
        if not (
            isinstance(daily_dates, list)
            and isinstance(daily_precipitation, list)
            and len(daily_dates) == len(daily_precipitation)
        ):
            raise ValueError("daily weather arrays are missing or inconsistent")
        yesterday = date.today() - timedelta(days=1)
        first_day = yesterday - timedelta(days=6)
        trend = []
        for day_value, amount in zip(daily_dates, daily_precipitation):
            if not isinstance(day_value, str):
                raise ValueError("daily date values must be strings")
            day = date.fromisoformat(day_value)
            if first_day <= day <= yesterday:
                trend.append(
                    {
                        "date": day.isoformat(),
                        "precipitation_mm": _finite_number(
                            amount, "daily precipitation"
                        ),
                    }
                )
        status = (
            "LIVE"
            if latest_precipitation is not None and latest_soil is not None
            else "DEMO"
        )
        return {
            "status": status,
            "reason": None if status == "LIVE" else "incomplete_observations",
            "provider": "Open-Meteo Forecast API",
            "fetched_at": now.isoformat(),
            "data_timestamp": latest_timestamp.isoformat()
            if latest_timestamp
            else None,
            "precipitation_mm": latest_precipitation,
            "soil_moisture_fraction": latest_soil,
            "observations": observations,
            "seven_day_trend": trend,
        }
    except (KeyError, TypeError, ValueError, OverflowError) as exc:
        LOGGER.warning("Open-Meteo response could not be used: %s", exc)
        return {"status": "DEMO", "reason": "invalid_response"}


def build_nilgiris_risk_zones(
    *,
    weather: dict[str, Any],
    infer_risk: Any,
    generate_pilot: Any,
) -> list[dict[str, Any]]:
    """Build three-by-three approximate zones from deterministic synthetic terrain."""
    pilot = generate_pilot(grid_size=GRID_SIZE)
    west, south, east, north = NILGIRIS_BOUNDS
    observations = weather.get("observations", [])
    soil_moisture = weather.get("soil_moisture_fraction")
    selected_indexes = (1, 4, 8)
    zones = []
    for row_number, row_index in enumerate(selected_indexes):
        for column_number, column_index in enumerate(selected_indexes):
            cell_index = row_index * GRID_SIZE + column_index
            cell = pilot.cells.iloc[cell_index]
            score = infer_risk(
                {
                    name: float(cell[name])
                    for name in (
                        "elevation_m",
                        "slope_deg",
                        "aspect_sin",
                        "aspect_cos",
                        "curvature",
                        "twi",
                        "ndvi",
                        "soil_clay_fraction",
                        "land_cover_code",
                        "road_distance_km",
                        "stream_distance_km",
                    )
                },
                zone=f"Nilgiris-{row_number + 1}-{column_number + 1}",
                rainfall_observations=observations,
                soil_moisture_fraction=soil_moisture,
            )
            zone_west = west + (east - west) * column_number / ZONE_COUNT
            zone_east = west + (east - west) * (column_number + 1) / ZONE_COUNT
            zone_north = north - (north - south) * row_number / ZONE_COUNT
            zone_south = north - (north - south) * (row_number + 1) / ZONE_COUNT
            zones.append(
                {
                    "zone_id": f"nilgiris-{row_number + 1}-{column_number + 1}",
                    "location": f"Nilgiris demo zone {row_number + 1}-{column_number + 1}",
                    "latitude": float(cell["latitude"]),
                    "longitude": float(cell["longitude"]),
                    "bounds": [zone_west, zone_south, zone_east, zone_north],
                    "risk_score": score["risk"]["risk_score"],
                    "risk_level": score["risk"]["risk_level"],
                    "risk_status": score["status"],
                    "weather_status": weather.get("status", "DEMO"),
                    "terrain_status": "SIMULATED",
                    "top_factors": score["top_factors"],
                    "why": score["why"],
                }
            )
    return zones
