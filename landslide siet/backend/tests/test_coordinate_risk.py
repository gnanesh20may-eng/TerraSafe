from backend.app.api.v1 import routes


def test_coordinate_risk_passes_browser_coordinates_to_risk_service(monkeypatch, api_request):
    captured = {}

    def fake_evaluate(location):
        captured["location"] = location
        return {
            "location": {
                "id": location.id,
                "name": location.name,
                "latitude": location.latitude,
                "longitude": location.longitude,
                "admin_region": location.admin_region,
            },
            "risk": {"score": 33, "level": "WATCH", "trend": "STABLE"},
            "confidence": {"available": True, "value": 0.8},
            "environment": {"source": "demo"},
            "terrain": {},
            "contributors": [],
            "recommendation": {"severity": "WATCH", "message": "Monitor conditions."},
            "timestamp": "2026-10-05T12:00:00Z",
        }

    monkeypatch.setattr(routes.risk_service, "evaluate_location", fake_evaluate)
    response = api_request(
        "GET",
        "/api/v1/risk",
        params={"latitude": 11.4, "longitude": 76.75, "name": "Current location"},
    )

    assert response.status_code == 200
    assert captured["location"].latitude == 11.4
    assert captured["location"].longitude == 76.75
    assert response.json()["location"]["name"] == "Current location"