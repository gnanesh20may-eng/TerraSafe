import asyncio
import xml.etree.ElementTree as ET
from datetime import date, datetime, timedelta, timezone

import httpx
import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from backend.app.database import Base, get_db
from backend.app import main as main_module
from backend.app.main import app
from backend.app.models import Alert, AlertAudit
from backend.app.risk import (
    OPEN_METEO_TIMEOUT_SECONDS,
    fetch_open_meteo_weather,
)
from backend.app.security import create_access_token

TEST_SECRET = "test-only-secret-value-that-is-at-least-32-bytes"


@pytest.fixture
def api_client(tmp_path, monkeypatch):
    monkeypatch.setenv("JWT_SECRET", TEST_SECRET)
    database_engine = create_engine(
        f"sqlite:///{tmp_path / 'api-tests.db'}",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(database_engine)
    test_session = sessionmaker(
        bind=database_engine, autoflush=False, expire_on_commit=False
    )

    def override_db():
        session = test_session()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_db

    def request(method, path, *, role=None, **kwargs):
        headers = kwargs.pop("headers", {})
        if role is not None:
            token = create_access_token("pytest", role, secret=TEST_SECRET)
            headers = {**headers, "Authorization": f"Bearer {token}"}

        async def send():
            transport = httpx.ASGITransport(app=app)
            async with httpx.AsyncClient(
                transport=transport, base_url="http://test"
            ) as client:
                return await client.request(
                    method, path, headers=headers, **kwargs
                )

        return asyncio.run(send())

    request.session_factory = test_session
    yield request
    app.dependency_overrides.clear()
    database_engine.dispose()


def create_alert(api_client, **updates):
    payload = {
        "zone_id": "zone-a",
        "location": "Demo zone",
        "pincode": "643001",
        "risk_score": 0.82,
    }
    payload.update(updates)
    return api_client("POST", "/api/v1/alerts", role="district_officer", json=payload)


def test_health_and_public_alert_reads(api_client):
    health = api_client("GET", "/health")
    assert health.status_code == 200
    assert health.json()["status"] == "LIVE"
    preflight = api_client(
        "OPTIONS",
        "/health",
        headers={
            "Origin": "http://localhost:3001",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert preflight.status_code == 200
    assert preflight.headers["access-control-allow-origin"] == "http://localhost:3001"

    created = create_alert(api_client)
    assert created.status_code == 201
    alert_id = created.json()["id"]

    assert api_client("GET", "/api/v1/alerts").status_code == 200
    assert api_client("GET", f"/api/v1/alerts/{alert_id}").status_code == 200
    assert api_client("GET", "/api/v1/alerts?limit=0").status_code == 422


def test_risk_map_returns_nine_simulated_zones_with_live_weather(api_client, monkeypatch):
    async def live_weather(*, latitude, longitude):
        assert (latitude, longitude) == (11.35, 76.7)
        return {
            "status": "LIVE",
            "reason": None,
            "provider": "Open-Meteo Forecast API",
            "fetched_at": "2026-10-05T12:00:00+00:00",
            "data_timestamp": "2026-10-05T11:00:00+00:00",
            "precipitation_mm": 2.5,
            "soil_moisture_fraction": 0.4,
            "observations": [],
            "seven_day_trend": [
                {"date": f"2026-10-0{day}", "precipitation_mm": float(day)}
                for day in range(1, 8)
            ],
        }

    monkeypatch.setattr(main_module, "fetch_open_meteo_weather", live_weather)
    response = api_client("GET", "/api/v1/risk?location=Nilgiris")
    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "DEMO"
    assert result["weather"]["status"] == "LIVE"
    assert result["weather"]["precipitation_mm"] == 2.5
    assert len(result["weather"]["seven_day_trend"]) == 7
    assert result["zone_geometry_status"] == "SIMULATED"
    assert len(result["zones"]) == 9
    assert {zone["risk_status"] for zone in result["zones"]} == {"SIMULATED"}
    assert {zone["terrain_status"] for zone in result["zones"]} == {"SIMULATED"}
    assert all(zone["top_factors"] and zone["why"] for zone in result["zones"])


def test_risk_map_demo_fallback_has_no_fabricated_weather(api_client, monkeypatch):
    async def timed_out_weather(*, latitude, longitude):
        return {"status": "DEMO", "reason": "timeout"}

    monkeypatch.setattr(main_module, "fetch_open_meteo_weather", timed_out_weather)
    response = api_client("GET", "/api/v1/risk")
    assert response.status_code == 200
    result = response.json()
    assert result["weather"]["status"] == "DEMO"
    assert result["weather"]["reason"] == "timeout"
    assert result["weather"]["precipitation_mm"] is None
    assert result["weather"]["soil_moisture_fraction"] is None
    assert result["weather"]["seven_day_trend"] is None
    assert len(result["zones"]) == 9
    assert {zone["weather_status"] for zone in result["zones"]} == {"DEMO"}


def test_open_meteo_client_has_five_second_timeout_and_parses_real_fields(monkeypatch):
    current = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    daily_start = date.today() - timedelta(days=7)
    payload = {
        "hourly": {
            "time": [(current - timedelta(hours=1)).isoformat()],
            "precipitation": [3.25],
            "soil_moisture_0_to_7cm": [0.31],
        },
        "daily": {
            "time": [
                (daily_start + timedelta(days=day)).isoformat()
                for day in range(8)
            ],
            "precipitation_sum": [float(day) for day in range(8)],
        },
    }

    class MockClient:
        def __init__(self, *, timeout):
            assert timeout.connect == OPEN_METEO_TIMEOUT_SECONDS
            assert timeout.read == OPEN_METEO_TIMEOUT_SECONDS

        async def __aenter__(self):
            return self

        async def __aexit__(self, *_):
            return None

        async def get(self, url, *, params):
            assert url == "https://api.open-meteo.com/v1/forecast"
            assert params["past_days"] == 7
            return httpx.Response(
                200,
                json=payload,
                request=httpx.Request("GET", url),
            )

    monkeypatch.setattr("backend.app.risk.httpx.AsyncClient", MockClient)
    result = asyncio.run(fetch_open_meteo_weather(11.35, 76.7))
    assert result["status"] == "LIVE"
    assert result["precipitation_mm"] == 3.25
    assert result["soil_moisture_fraction"] == 0.31
    assert len(result["seven_day_trend"]) == 7


def test_open_meteo_timeout_returns_explicit_demo_fallback(monkeypatch):
    class TimeoutClient:
        def __init__(self, *, timeout):
            assert timeout.read == OPEN_METEO_TIMEOUT_SECONDS

        async def __aenter__(self):
            return self

        async def __aexit__(self, *_):
            return None

        async def get(self, url, *, params):
            raise httpx.ConnectTimeout(
                "simulated timeout", request=httpx.Request("GET", url)
            )

    monkeypatch.setattr("backend.app.risk.httpx.AsyncClient", TimeoutClient)
    result = asyncio.run(fetch_open_meteo_weather(11.35, 76.7))
    assert result == {"status": "DEMO", "reason": "timeout"}


def test_jwt_roles_lifecycle_mock_notifications_cap_and_audit(api_client):
    created = create_alert(api_client, latitude=11.4, longitude=76.7)
    assert created.status_code == 201
    alert = created.json()
    assert alert["risk_level"] == "Red"
    assert alert["status"] == "Created"

    no_role = api_client("POST", "/api/v1/alerts", json={
        "zone_id": "z",
        "location": "x",
        "risk_score": 0.3,
    })
    assert no_role.status_code == 401
    public_write = api_client(
        "POST",
        f"/api/v1/alerts/{alert['id']}/transition",
        role="public",
        json={"event": "Approved"},
    )
    assert public_write.status_code == 403

    for event in ("Approved", "Sent", "Delivered"):
        response = api_client(
            "POST",
            f"/api/v1/alerts/{alert['id']}/transition",
            role="district_officer",
            json={"event": event},
        )
        assert response.status_code == 200
        if event == "Sent":
            assert {item["status"] for item in response.json()["notifications"]} == {
                "DEMO"
            }
            assert {item["channel"] for item in response.json()["notifications"]} == {
                "web_push",
                "sms",
                "whatsapp",
                "email",
                "voice",
            }

    skipped = api_client(
        "POST",
        f"/api/v1/alerts/{alert['id']}/transition",
        role="field_responder",
        json={"event": "Resolved"},
    )
    assert skipped.status_code == 409
    acknowledged = api_client(
        "POST",
        f"/api/v1/alerts/{alert['id']}/transition",
        role="field_responder",
        json={"event": "Acknowledged"},
    )
    assert acknowledged.status_code == 200
    resolved = api_client(
        "POST",
        f"/api/v1/alerts/{alert['id']}/transition",
        role="field_responder",
        json={"event": "Resolved"},
    )
    assert resolved.status_code == 200
    assert resolved.json()["status"] == "Resolved"

    audit = api_client("GET", f"/api/v1/alerts/{alert['id']}/audit")
    assert audit.status_code == 200
    assert audit.json()["chain_valid"] is True
    assert [entry["sequence"] for entry in audit.json()["entries"]] == list(range(1, 7))

    cap_response = api_client("GET", f"/api/v1/alerts/{alert['id']}/cap")
    assert cap_response.status_code == 200
    cap_root = ET.fromstring(cap_response.text)
    assert cap_root.find("{urn:oasis:names:tc:emergency:cap:1.2}status").text == "Test"
    area = cap_root.find(
        ".//{urn:oasis:names:tc:emergency:cap:1.2}area/"
        "{urn:oasis:names:tc:emergency:cap:1.2}areaDesc"
    )
    assert area.text.startswith("SIMULATED area;")
    circle = cap_root.find(
        ".//{urn:oasis:names:tc:emergency:cap:1.2}area/"
        "{urn:oasis:names:tc:emergency:cap:1.2}circle"
    )
    assert circle.text == "11.4,76.7,1"


def test_alert_deduplication_hysteresis_and_geofence(api_client):
    first = create_alert(api_client, risk_score=0.76)
    assert first.status_code == 201
    assert first.json()["risk_level"] == "Red"

    duplicate = create_alert(api_client, risk_score=0.8)
    assert duplicate.status_code == 201
    assert duplicate.json()["deduplicated"] is True
    assert duplicate.json()["id"] == first.json()["id"]

    within_hysteresis = create_alert(api_client, risk_score=0.72)
    assert within_hysteresis.json()["risk_level"] == "Red"
    downgraded = create_alert(api_client, risk_score=0.69)
    assert downgraded.json()["risk_level"] == "Orange"

    outside = create_alert(
        api_client,
        zone_id="zone-b",
        risk_score=0.4,
        latitude=12.1,
        longitude=77,
        geofence_bounds=[76, 11, 77, 12],
    )
    assert outside.status_code == 422

    inside = create_alert(
        api_client,
        zone_id="zone-c",
        risk_score=0.4,
        latitude=11.5,
        longitude=76.5,
        geofence_bounds=[76, 11, 77, 12],
    )
    assert inside.status_code == 201
    invalid_geofence = create_alert(
        api_client,
        zone_id="zone-d",
        latitude=11.5,
        longitude=76.5,
        geofence_bounds=[77, 11, 76, 12],
    )
    assert invalid_geofence.status_code == 422


def test_alert_update_delete_and_capabilities_are_labeled(api_client):
    created = create_alert(api_client, risk_score=0.6)
    alert_id = created.json()["id"]
    changed = api_client(
        "PATCH",
        f"/api/v1/alerts/{alert_id}",
        role="district_officer",
        json={"message": "Updated DEMO message"},
    )
    assert changed.status_code == 200
    assert changed.json()["message"] == "Updated DEMO message"
    assert api_client(
        "DELETE", f"/api/v1/alerts/{alert_id}", role="admin"
    ).status_code == 204
    assert api_client("GET", f"/api/v1/alerts/{alert_id}").status_code == 404

    simulation = api_client(
        "POST",
        "/api/v1/simulate",
        json={"baseline_score": 0.4, "rainfall_mm": 100, "road_cut": True},
    )
    assert simulation.status_code == 200
    assert simulation.json()["status"] == "SIMULATED"
    route = api_client(
        "GET", "/api/v1/evacuation/nearest?latitude=11.4&longitude=76.7"
    )
    assert route.status_code == 200
    assert route.json()["feature_status"] == "MISSING"
    assert route.json()["nearest_shelter"] is None
    assert api_client("GET", "/api/v1/models/metrics").json()["status"] in {
        "MISSING",
        "SIMULATED",
        "SCAFFOLD",
    }


def test_sos_privacy_sms_query_and_rescue_status(api_client):
    created = api_client(
        "POST",
        "/sos",
        json={
            "phone": "+910000000000",
            "pincode": "643001",
            "latitude": 11.4,
            "longitude": 76.7,
            "message": "DEMO test",
        },
    )
    assert created.status_code == 201
    assert "phone" not in created.json()
    assert api_client("GET", "/sos").status_code == 401
    assert api_client("GET", "/sos", role="field_responder").json()["sos"][0]["id"] == created.json()["id"]

    alert = create_alert(api_client, risk_score=0.6)
    reply = api_client(
        "POST", "/sms/inbound", json={"message_text": "RISK 643001"}
    )
    assert reply.status_code == 200
    assert reply.json()["status"] == "DEMO"
    assert "DEMO risk" in reply.json()["reply"]
    assert api_client("GET", "/rescue").json()["status"] == "SCAFFOLD"


def test_persisted_alert_audit_chain_detects_mutation(api_client):
    created = create_alert(api_client)
    alert_id = created.json()["id"]

    audit = api_client("GET", f"/api/v1/alerts/{alert_id}/audit")
    assert audit.json()["chain_valid"] is True
    with api_client.session_factory() as db:
        entry = db.scalar(
            select(AlertAudit).where(AlertAudit.alert_id == alert_id)
        )
        entry.payload = '{"modified":true}'
        db.commit()
    tampered = api_client("GET", f"/api/v1/alerts/{alert_id}/audit")
    assert tampered.json()["chain_valid"] is False
    with api_client.session_factory() as db:
        entry = db.scalar(
            select(AlertAudit).where(AlertAudit.alert_id == alert_id)
        )
        entry.payload = "{"
        db.commit()
    malformed = api_client("GET", f"/api/v1/alerts/{alert_id}/audit")
    assert malformed.status_code == 200
    assert malformed.json()["chain_valid"] is False
    assert malformed.json()["entries"][0]["payload"] is None
    assert malformed.json()["entries"][0]["payload_error"] == "invalid_json"


def test_stale_alert_is_auto_escalated_with_audit(api_client):
    created = create_alert(
        api_client,
        zone_id="stale-zone",
        risk_score=0.3,
    )
    alert_id = created.json()["id"]
    with api_client.session_factory() as db:
        alert = db.get(Alert, alert_id)
        alert.updated_at = datetime.now(timezone.utc) - timedelta(minutes=31)
        db.commit()

    trigger_escalation = create_alert(
        api_client,
        zone_id="different-zone",
        risk_score=0.1,
    )
    assert trigger_escalation.status_code == 201
    with api_client.session_factory() as db:
        alert = db.get(Alert, alert_id)
        entry = db.scalar(
            select(AlertAudit).where(
                AlertAudit.alert_id == alert_id,
                AlertAudit.event == "AutoEscalated",
            )
        )
        assert alert.risk_level == "Orange"
        assert entry is not None
