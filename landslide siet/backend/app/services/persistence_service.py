from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from backend.app.db import SessionLocal, init_db
from backend.app.models_db import AlertEventRecord, AlertRecord, SosRecord

ALERT_STATES = ("CREATED", "APPROVED", "SENT", "DELIVERED", "ACKNOWLEDGED", "RESOLVED")
ALLOWED_TRANSITIONS = {
    "CREATED": {"APPROVED", "RESOLVED"},
    "APPROVED": {"SENT", "RESOLVED"},
    "SENT": {"DELIVERED", "ACKNOWLEDGED", "RESOLVED"},
    "DELIVERED": {"ACKNOWLEDGED", "RESOLVED"},
    "ACKNOWLEDGED": {"RESOLVED"},
    "RESOLVED": set(),
}
GENESIS_HASH = "0" * 64


class PersistenceService:
    def __init__(self, session_factory: sessionmaker[Session] = SessionLocal, initialize: bool = True) -> None:
        self.session_factory = session_factory
        if initialize and session_factory is SessionLocal:
            init_db()

    def create_sos(self, message: str, latitude: float | None, longitude: float | None, source: str = "WEB") -> dict[str, Any]:
        with self.session_factory() as session:
            record = SosRecord(id=str(uuid.uuid4()), message=message, latitude=latitude, longitude=longitude, status="OPEN", source=source)
            session.add(record)
            session.commit()
            session.refresh(record)
            return self._sos_dict(record)

    def list_sos(self, limit: int = 50) -> list[dict[str, Any]]:
        with self.session_factory() as session:
            rows = session.scalars(select(SosRecord).order_by(SosRecord.created_at.desc()).limit(limit)).all()
            return [self._sos_dict(row) for row in rows]

    def create_alert(self, location_id: str, risk_level: str, message: str, actor: str) -> dict[str, Any]:
        if risk_level not in {"LOW", "WATCH", "HIGH", "CRITICAL"}:
            raise ValueError("unsupported risk level")
        with self.session_factory() as session:
            record = AlertRecord(id=str(uuid.uuid4()), location_id=location_id, risk_level=risk_level, message=message, lifecycle_state="CREATED", created_by=actor)
            session.add(record)
            session.flush()
            self._append_event(session, record, None, "CREATED", actor, "Alert created; no external delivery performed.")
            session.commit()
            session.refresh(record)
            return self._alert_dict(record)

    def list_alerts(self, limit: int = 50) -> list[dict[str, Any]]:
        with self.session_factory() as session:
            rows = session.scalars(select(AlertRecord).order_by(AlertRecord.created_at.desc()).limit(limit)).all()
            return [self._alert_dict(row) for row in rows]

    def transition_alert(self, alert_id: str, next_state: str, actor: str, detail: str = "") -> dict[str, Any]:
        if next_state not in ALERT_STATES:
            raise ValueError("unsupported alert lifecycle state")
        with self.session_factory() as session:
            record = session.get(AlertRecord, alert_id)
            if record is None:
                raise LookupError("alert not found")
            previous = record.lifecycle_state
            if next_state not in ALLOWED_TRANSITIONS[previous]:
                raise ValueError(f"invalid lifecycle transition: {previous} -> {next_state}")
            if next_state == "SENT":
                detail = "MOCK ONLY: no SMS, WhatsApp, email, voice, or push was sent. " + (detail or "")
            record.lifecycle_state = next_state
            record.updated_at = datetime.now(timezone.utc)
            if next_state == "APPROVED":
                record.approved_by = actor
            self._append_event(session, record, previous, next_state, actor, detail or f"Transitioned {previous} to {next_state}.")
            session.commit()
            session.refresh(record)
            return self._alert_dict(record)

    def verify_alert_chain(self, alert_id: str) -> bool:
        with self.session_factory() as session:
            events = session.scalars(select(AlertEventRecord).where(AlertEventRecord.alert_id == alert_id).order_by(AlertEventRecord.sequence)).all()
            previous_hash = GENESIS_HASH
            for expected_sequence, event in enumerate(events, start=1):
                if event.sequence != expected_sequence or event.previous_hash != previous_hash:
                    return False
                expected_hash = self._event_hash(alert_id=event.alert_id, sequence=event.sequence, from_state=event.from_state, to_state=event.to_state, actor=event.actor, detail=event.detail, created_at=event.created_at.isoformat(), previous_hash=previous_hash)
                if event.event_hash != expected_hash:
                    return False
                previous_hash = event.event_hash
            return bool(events)

    @staticmethod
    def _append_event(session: Session, alert: AlertRecord, from_state: str | None, to_state: str, actor: str, detail: str) -> None:
        latest = session.scalar(select(AlertEventRecord).where(AlertEventRecord.alert_id == alert.id).order_by(AlertEventRecord.sequence.desc()).limit(1))
        sequence = latest.sequence + 1 if latest else 1
        previous_hash = latest.event_hash if latest else GENESIS_HASH
        created_at = datetime.now(timezone.utc)
        digest = PersistenceService._event_hash(alert_id=alert.id, sequence=sequence, from_state=from_state, to_state=to_state, actor=actor, detail=detail, created_at=created_at.isoformat(), previous_hash=previous_hash)
        session.add(AlertEventRecord(alert_id=alert.id, sequence=sequence, from_state=from_state, to_state=to_state, actor=actor, detail=detail, created_at=created_at, previous_hash=previous_hash, event_hash=digest))

    @staticmethod
    def _event_hash(**values: Any) -> str:
        timestamp = values.get("created_at")
        if timestamp:
            parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            values["created_at"] = parsed.astimezone(timezone.utc).isoformat()
        serialized = json.dumps(values, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    @staticmethod
    def _sos_dict(record: SosRecord) -> dict[str, Any]:
        return {"id": record.id, "message": record.message, "latitude": record.latitude, "longitude": record.longitude, "status": record.status, "source": record.source, "created_at": record.created_at.isoformat(), "delivery": "MOCK — no external contact notified"}

    @staticmethod
    def _alert_dict(record: AlertRecord) -> dict[str, Any]:
        return {"id": record.id, "location_id": record.location_id, "risk_level": record.risk_level, "message": record.message, "lifecycle_state": record.lifecycle_state, "created_by": record.created_by, "approved_by": record.approved_by, "created_at": record.created_at.isoformat(), "events": [{"sequence": event.sequence, "from_state": event.from_state, "to_state": event.to_state, "actor": event.actor, "detail": event.detail, "created_at": event.created_at.isoformat(), "previous_hash": event.previous_hash, "event_hash": event.event_hash} for event in record.events]}
