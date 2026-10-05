import httpx

from backend.app.services import data_health
from backend.app.api.v1 import routes


class FakeResponse:
    def __init__(self, body):
        self.body = body

    def raise_for_status(self):
        pass

    def json(self):
        return self.body


def test_open_meteo_archive_health_reports_record_count_and_latest_time(monkeypatch):
    monkeypatch.setattr(
        data_health.httpx,
        "get",
        lambda *args, **kwargs: FakeResponse({
            "hourly": {
                "time": ["2026-09-20T00:00", "2026-09-20T01:00"],
                "precipitation": [0.0, 1.2],
                "soil_moisture_0_to_7cm": [0.3, 0.31],
            }
        }),
    )

    result = data_health.check_source({
        "id": "open_meteo_archive", "name": "Open-Meteo", "category": "meteorology", "access_type": "open"
    })

    assert result["status"] == "WORKING"
    assert result["record_count"] == 2
    assert result["newest_timestamp"] == "2026-09-20T01:00"
    assert result["latency_ms"] is not None


def test_usgs_health_counts_geojson_features(monkeypatch):
    monkeypatch.setattr(
        data_health.httpx,
        "get",
        lambda *args, **kwargs: FakeResponse({
            "features": [{"properties": {"time": 1791200000000}}, {"properties": {"time": 1791200001000}}]
        }),
    )

    result = data_health.check_source({
        "id": "usgs_earthquakes", "name": "USGS", "category": "sensors", "access_type": "open"
    })

    assert result["status"] == "WORKING"
    assert result["record_count"] == 2
    assert result["newest_timestamp"].startswith("2026-")


def test_data_health_classifies_manual_and_failed_sources(monkeypatch):
    manual = data_health.check_source({
        "id": "private_sensor_feed", "name": "Private feed", "category": "sensors",
        "status": "manual", "access_type": "login",
    })
    monkeypatch.setattr(data_health.httpx, "get", lambda *args, **kwargs: (_ for _ in ()).throw(httpx.ConnectError("offline")))
    failed = data_health.check_source({
        "id": "usgs_earthquakes", "name": "USGS", "category": "sensors", "access_type": "open"
    })

    assert manual["status"] == "MANUAL"
    assert failed["status"] == "FAILED"
    assert "ConnectError" in failed["error"]


def test_needs_review_status_takes_precedence_over_manual_access():
    result = data_health.check_source({
        "id": "catalog_unverified", "name": "Unverified catalog", "category": "ground_landslide",
        "status": "needs_review", "access_type": "manual",
    })

    assert result["status"] == "NEEDS_REVIEW"


def test_data_source_health_route_returns_check_results(monkeypatch, api_request):
    report = {"region": "nilgiris", "sources": [{"id": "usgs_earthquakes", "status": "WORKING"}]}
    monkeypatch.setattr(routes, "check_all_sources", lambda: report)

    response = api_request("GET", "/api/v1/health/data-sources")

    assert response.status_code == 200
    assert response.json() == report