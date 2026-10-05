import httpx
import pytest

from backend.app.providers.base import LocationRef, WeatherConditions
from backend.app.providers.weather import OpenMeteoWeatherProvider
from backend.app.services.environment_service import environment_service


LOCATION = LocationRef("coonor", "Coonoor", 11.35, 76.8, "Nilgiris District")


def test_open_meteo_weather_uses_live_hourly_values(monkeypatch):
    hourly = {
        "precipitation": [1.0] * 168,
        "soil_moisture_0_to_7cm": [0.42] * 168,
    }

    class Response:
        def raise_for_status(self):
            pass

        def json(self):
            return {"hourly": hourly}

    def fake_get(url, params, timeout):
        assert url.endswith("/forecast")
        assert params["latitude"] == LOCATION.latitude
        assert params["longitude"] == LOCATION.longitude
        assert timeout == 5.0
        return Response()

    monkeypatch.setattr(httpx, "get", fake_get)
    weather = OpenMeteoWeatherProvider().get_current_weather(LOCATION)

    assert weather.rainfall_24h_mm == 24.0
    assert weather.rainfall_7d_mm == 168.0
    assert weather.soil_moisture_pct == 42.0
    assert weather.source == "open-meteo"


def test_open_meteo_weather_falls_back_to_demo_on_request_failure(monkeypatch):
    def fake_get(*args, **kwargs):
        raise httpx.ConnectError("offline")

    monkeypatch.setattr(httpx, "get", fake_get)
    weather = OpenMeteoWeatherProvider().get_current_weather(LOCATION)

    assert weather.rainfall_24h_mm == 42.0
    assert weather.soil_moisture_pct == 68.0
    assert weather.source == "demo"


@pytest.mark.parametrize(("source", "demo_mode"), [("open-meteo", False), ("demo", True)])
def test_health_reports_current_weather_mode(monkeypatch, source, demo_mode, api_request):
    monkeypatch.setattr(
        environment_service.weather_provider,
        "get_current_weather",
        lambda location: WeatherConditions(1, 2, 3, 4, 5, source),
    )
    for path in ("/health", "/api/v1/health"):
        response = api_request("GET", path)
        assert response.status_code == 200
        assert response.json()["demo_mode"] is demo_mode
        assert response.json()["weather_source"] == source