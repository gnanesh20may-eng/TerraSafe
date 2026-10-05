from backend.app.providers.base import LocationRef
from backend.app.services.environment_service import EnvironmentService


def test_environment_service_returns_weather_and_terrain_data():
    service = EnvironmentService()
    location = LocationRef(id="coonor", name="Coonoor", latitude=11.35, longitude=76.8, admin_region="Nilgiris District")
    snapshot = service.get_environment(location)

    assert snapshot["location"]["id"] == "coonor"
    assert snapshot["weather"]["rainfall_24h_mm"] > 0
    assert snapshot["terrain"]["elevation_m"] > 0
    assert snapshot["satellite"]["land_cover"]
    assert snapshot["data_status"] == "DEMO DATA"


def test_demo_weather_provider_maps_known_location():
    service = EnvironmentService()
    location = LocationRef(id="ooty", name="Ooty", latitude=11.41, longitude=76.7, admin_region="Nilgiris District")
    snapshot = service.get_environment(location)
    assert snapshot["weather"]["soil_moisture_pct"] > 0
    assert snapshot["terrain"]["slope_deg"] > 0
