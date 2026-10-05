from __future__ import annotations

from backend.app.api.v1 import routes


def test_health_reports_provider_provenance(monkeypatch):
    monkeypatch.setattr(routes, "DEMO_MODE", True)

    result = routes.health()

    assert result["service"] == "terrasafe-api"
    assert result["demo_mode"] is True
    assert result["weather_source"] == "DEMO WEATHER PROVIDER"
    assert result["terrain_source"].startswith("DEMO")
    assert result["satellite_source"].startswith("DEMO")


def test_risk_history_does_not_fabricate_unstored_observations():
    result = routes.get_risk_history("coonor")

    assert result == {"location_id": "coonor", "status": "MISSING", "history": []}


def test_risk_history_rejects_an_unknown_location():
    from fastapi import HTTPException

    try:
        routes.get_risk_history("unknown")
    except HTTPException as error:
        assert error.status_code == 404
    else:
        raise AssertionError("unknown location should not receive an empty history")
