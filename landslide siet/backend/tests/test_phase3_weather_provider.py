from __future__ import annotations

from datetime import datetime, timedelta, timezone

import httpx
import pytest
from fastapi import HTTPException

from backend.app.api.v1 import routes as api_routes
from backend.app.providers.base import LocationRef, ProviderUnavailableError
from backend.app.providers.satellite import DemoSatelliteProvider
from backend.app.providers.terrain import DemoTerrainProvider
from backend.app.providers.weather import OpenMeteoWeatherProvider
from backend.app.services.environment_service import EnvironmentService


def _weather_response() -> dict:
    now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    times = [
        (now - timedelta(hours=hour)).isoformat().replace("+00:00", "Z")
        for hour in range(168, -1, -1)
    ]
    return {
        "current": {
            "time": now.isoformat().replace("+00:00", "Z"),
            "temperature_2m": 22.5,
            "wind_speed_10m": 13.2,
        },
        "hourly": {
            "time": times,
            "precipitation": [1.0] * len(times),
            "soil_moisture_0_to_7cm": [0.42] * len(times),
        },
    }


def test_open_meteo_provider_maps_observations_and_accumulations():
    payload = _weather_response()
    client = httpx.Client(
        transport=httpx.MockTransport(
            lambda request: httpx.Response(200, json=payload, request=request)
        )
    )
    provider = OpenMeteoWeatherProvider(client=client)
    location = LocationRef("test", "Test location", 11.35, 76.8)

    result = provider.get_current_weather(location)

    assert result.rainfall_24h_mm == 24.0
    assert result.rainfall_7d_mm == 168.0
    assert result.soil_moisture_pct == 42.0
    assert result.wind_speed_kmh == 13.2
    assert result.temperature_c == 22.5
    assert result.source == "OPEN-METEO API"
    assert result.observed_at is not None


def test_open_meteo_provider_leaves_missing_soil_moisture_unavailable():
    payload = _weather_response()
    payload["hourly"].pop("soil_moisture_0_to_7cm")
    client = httpx.Client(
        transport=httpx.MockTransport(
            lambda request: httpx.Response(200, json=payload, request=request)
        )
    )
    provider = OpenMeteoWeatherProvider(client=client)

    result = provider.get_current_weather(LocationRef("test", "Test", 11.35, 76.8))

    assert result.soil_moisture_pct is None


def test_environment_service_reports_mixed_provider_provenance():
    payload = _weather_response()
    client = httpx.Client(
        transport=httpx.MockTransport(
            lambda request: httpx.Response(200, json=payload, request=request)
        )
    )
    service = EnvironmentService(
        weather_provider=OpenMeteoWeatherProvider(client=client),
        terrain_provider=DemoTerrainProvider(),
        satellite_provider=DemoSatelliteProvider(),
    )

    snapshot = service.get_environment(LocationRef("test", "Test", 11.35, 76.8))

    assert snapshot["data_status"] == "MIXED LIVE/DEMO DATA"
    assert snapshot["weather"]["source"] == "OPEN-METEO API"
    assert snapshot["terrain"]["source"].startswith("DEMO")
    assert snapshot["last_updated"]


def test_open_meteo_provider_rejects_invalid_coordinates():
    provider = OpenMeteoWeatherProvider()

    with pytest.raises(ValueError, match="coordinates"):
        provider.get_current_weather(LocationRef("test", "Test", 91, 0))


def test_open_meteo_provider_surfaces_upstream_http_failure():
    client = httpx.Client(
        transport=httpx.MockTransport(
            lambda request: httpx.Response(503, request=request)
        )
    )
    provider = OpenMeteoWeatherProvider(client=client)

    with pytest.raises(ProviderUnavailableError, match="unavailable"):
        provider.get_current_weather(LocationRef("test", "Test", 11.35, 76.8))


def test_environment_api_returns_503_when_provider_is_unavailable(monkeypatch):
    def fail_when_fetching(_location):
        raise ProviderUnavailableError("Open-Meteo weather service is unavailable")

    monkeypatch.setattr(api_routes.environment_service, "get_environment", fail_when_fetching)

    with pytest.raises(HTTPException) as error:
        api_routes.get_environment("coonor")

    assert error.value.status_code == 503