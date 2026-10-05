from __future__ import annotations

from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.core.auth import issue_token
from backend.app.db import Base
from backend.app.models_db import AlertEventRecord
from backend.app.services.persistence_service import PersistenceService


@pytest.fixture
def persistence():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    service = PersistenceService(factory, initialize=False)
    yield service
    Base.metadata.drop_all(engine)
    engine.dispose()


def test_sos_persists_and_never_claims_external_delivery(persistence):
    created = persistence.create_sos("Need assistance", 11.35, 76.8)
    listed = persistence.list_sos()

    assert listed[0]["id"] == created["id"]
    assert listed[0]["latitude"] == 11.35
    assert listed[0]["delivery"].startswith("MOCK")


def test_alert_lifecycle_hash_chain_and_mock_send(persistence):
    alert = persistence.create_alert("coonor", "HIGH", "Demo alert", "officer-1")
    approved = persistence.transition_alert(alert["id"], "APPROVED", "officer-1")
    sent = persistence.transition_alert(alert["id"], "SENT", "system", "adapter call skipped")
    delivered = persistence.transition_alert(alert["id"], "DELIVERED", "mock-adapter", "simulated receipt")

    assert approved["approved_by"] == "officer-1"
    assert sent["events"][-1]["detail"].startswith("MOCK ONLY")
    assert delivered["lifecycle_state"] == "DELIVERED"
    assert persistence.verify_alert_chain(alert["id"])


def test_alert_lifecycle_rejects_skipping_authority_approval(persistence):
    alert = persistence.create_alert("coonor", "WATCH", "Demo alert", "officer-1")

    with pytest.raises(ValueError, match="invalid lifecycle"):
        persistence.transition_alert(alert["id"], "SENT", "system")


def test_alert_chain_detects_tampering(persistence):
    alert = persistence.create_alert("coonor", "HIGH", "Demo alert", "officer-1")
    with persistence.session_factory() as session:
        event = session.query(AlertEventRecord).filter_by(alert_id=alert["id"]).one()
        event.detail = "edited"
        session.commit()

    assert persistence.verify_alert_chain(alert["id"]) is False


def test_jwt_roles_are_signed_and_expire_claims_are_present():
    token = issue_token("responder-1", "field_responder", secret="test-secret-key-with-at-least-32-bytes")
    import jwt

    claims = jwt.decode(token, "test-secret-key-with-at-least-32-bytes", algorithms=["HS256"])

    assert claims["sub"] == "responder-1"
    assert claims["role"] == "field_responder"
    assert "exp" in claims
