from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app import core
from backend.app.api import sos as sos_api
from backend.app.api.v1 import routes
from backend.app.core import auth
from backend.app.db import Base
from backend.app.services.persistence_service import PersistenceService
from backend.main import app


def test_sos_contract_persists_and_queue_requires_responder_role(monkeypatch):
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    service = PersistenceService(sessionmaker(bind=engine, expire_on_commit=False), initialize=False)
    monkeypatch.setattr(sos_api, "persistence", service)
    monkeypatch.setattr(auth, "JWT_SECRET", "local-test-key-with-more-than-thirty-two-bytes")
    client = TestClient(app)

    created = client.post("/sos", json={"message": "Need help", "latitude": 11.35, "longitude": 76.8})

    assert created.status_code == 201
    assert created.json()["status"] == "OPEN"
    assert created.json()["delivery"].startswith("MOCK")
    assert client.get("/sos").status_code == 401
    token = auth.issue_token("responder-1", "field_responder")
    listed = client.get("/sos", headers={"Authorization": f"Bearer {token}"})
    assert listed.status_code == 200
    assert listed.json()["items"][0]["id"] == created.json()["id"]
    engine.dispose()


def test_authority_alert_lifecycle_and_cap_export(monkeypatch):
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    service = PersistenceService(sessionmaker(bind=engine, expire_on_commit=False), initialize=False)
    monkeypatch.setattr(routes, "persistence", service)
    monkeypatch.setattr(auth, "JWT_SECRET", "local-test-key-with-more-than-thirty-two-bytes")
    client = TestClient(app)
    public_token = auth.issue_token("public-1", "public")
    authority_token = auth.issue_token("officer-1", "district_officer")

    denied = client.post(
        "/api/v1/alerts",
        json={"location_id": "coonor", "risk_level": "HIGH", "message": "Demo"},
        headers={"Authorization": f"Bearer {public_token}"},
    )
    assert denied.status_code == 403

    created = client.post(
        "/api/v1/alerts",
        json={"location_id": "coonor", "risk_level": "HIGH", "message": "Demo alert"},
        headers={"Authorization": f"Bearer {authority_token}"},
    )
    assert created.status_code == 201
    alert_id = created.json()["id"]
    approved = client.post(
        f"/api/v1/alerts/{alert_id}/lifecycle",
        json={"state": "APPROVED"},
        headers={"Authorization": f"Bearer {authority_token}"},
    )
    assert approved.status_code == 200
    cap = client.get(f"/api/v1/alerts/{alert_id}/cap")
    assert cap.status_code == 200
    assert "urn:oasis:names:tc:emergency:cap:1.2" in cap.text
    assert "DEMO alert" in cap.text
    assert "<severity>Severe</severity>" in cap.text
    assert service.verify_alert_chain(alert_id)
    simulation = client.post("/api/v1/simulate", json={"location_id": "coonor", "rainfall_24h_mm": 120})
    assert simulation.status_code == 200
    assert simulation.json()["status"] == "SIMULATED"
    assert "not a forecast" in simulation.json()["disclaimer"]
    route = client.get("/api/v1/rescue/route?latitude=11.35&longitude=76.8")
    assert route.status_code == 200
    assert route.json()["status"] == "SIMULATED"
    assert route.json()["route"] is None
    engine.dispose()
