"""Alert scoring, lifecycle, deduplication, and tamper-evident audit helpers."""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models import Alert, AlertAudit

RISK_LEVELS = ("Green", "Yellow", "Orange", "Red")
RISK_THRESHOLDS = {"Yellow": 0.25, "Orange": 0.50, "Red": 0.75}
TRANSITIONS = {
    "Created": "Approved",
    "Approved": "Sent",
    "Sent": "Delivered",
    "Delivered": "Acknowledged",
    "Acknowledged": "Resolved",
}
COOLDOWN = timedelta(minutes=10)
AUTO_ESCALATION_AGE = timedelta(minutes=30)
HYSTERESIS_MARGIN = 0.05


def risk_level(score: float) -> str:
    if not 0 <= score <= 1:
        raise ValueError("risk_score must be between 0 and 1")
    return "Green" if score < 0.25 else "Yellow" if score < 0.5 else "Orange" if score < 0.75 else "Red"


def apply_hysteresis(score: float, previous_level: str | None) -> str:
    candidate = risk_level(score)
    if previous_level not in RISK_LEVELS:
        return candidate
    if RISK_LEVELS.index(candidate) >= RISK_LEVELS.index(previous_level):
        return candidate
    if previous_level != "Green" and score >= RISK_THRESHOLDS[previous_level] - HYSTERESIS_MARGIN:
        return previous_level
    return candidate


def point_in_geofence(
    latitude: float,
    longitude: float,
    bounds: tuple[float, float, float, float],
) -> bool:
    """Check a point against west/south/east/north WGS84 bounds."""
    west, south, east, north = bounds
    if not (-180 <= west < east <= 180 and -90 <= south < north <= 90):
        raise ValueError("geofence bounds must be valid WGS84 coordinates")
    if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
        raise ValueError("coordinates must be valid WGS84 coordinates")
    return west <= longitude <= east and south <= latitude <= north


def add_audit(
    db: Session,
    alert: Alert,
    event: str,
    actor: str,
    payload: dict[str, Any] | None = None,
) -> AlertAudit:
    previous = db.scalar(
        select(AlertAudit)
        .where(AlertAudit.alert_id == alert.id)
        .order_by(AlertAudit.sequence.desc())
        .limit(1)
    )
    previous_hash = previous.entry_hash if previous else "0" * 64
    sequence = previous.sequence + 1 if previous else 1
    created_at = datetime.now(timezone.utc).isoformat()
    encoded_payload = json.dumps(payload or {}, sort_keys=True, separators=(",", ":"))
    canonical = json.dumps(
        {
            "alert_id": alert.id,
            "sequence": sequence,
            "event": event,
            "actor": actor,
            "payload": json.loads(encoded_payload),
            "previous_hash": previous_hash,
            "created_at": created_at,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    entry_hash = hashlib.sha256((previous_hash + canonical).encode("utf-8")).hexdigest()
    record = AlertAudit(
        id=str(uuid.uuid4()),
        alert_id=alert.id,
        sequence=sequence,
        event=event,
        actor=actor,
        payload=encoded_payload,
        previous_hash=previous_hash,
        entry_hash=entry_hash,
        created_at=created_at,
    )
    db.add(record)
    return record


def verify_audit_chain(entries: list[AlertAudit]) -> bool:
    previous_hash = "0" * 64
    for expected_sequence, entry in enumerate(entries, start=1):
        if entry.sequence != expected_sequence or entry.previous_hash != previous_hash:
            return False
        try:
            payload = json.loads(entry.payload)
        except json.JSONDecodeError:
            return False
        canonical = json.dumps(
            {
                "alert_id": entry.alert_id,
                "sequence": entry.sequence,
                "event": entry.event,
                "actor": entry.actor,
                "payload": payload,
                "previous_hash": entry.previous_hash,
                "created_at": entry.created_at,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        actual_hash = hashlib.sha256(
            (entry.previous_hash + canonical).encode("utf-8")
        ).hexdigest()
        if actual_hash != entry.entry_hash:
            return False
        previous_hash = entry.entry_hash
    return True


def auto_escalate_stale_alerts(db: Session, now: datetime | None = None) -> int:
    current = now or datetime.now(timezone.utc)
    alerts = db.scalars(
        select(Alert).where(
            Alert.deleted_at.is_(None),
            Alert.status.in_(("Created", "Approved", "Sent", "Delivered")),
        )
    ).all()
    changed = 0
    for alert in alerts:
        updated = alert.updated_at
        if updated.tzinfo is None:
            updated = updated.replace(tzinfo=timezone.utc)
        if current - updated < AUTO_ESCALATION_AGE or alert.risk_level == "Red":
            continue
        old_level = alert.risk_level
        alert.risk_level = RISK_LEVELS[RISK_LEVELS.index(old_level) + 1]
        alert.updated_at = current
        add_audit(
            db,
            alert,
            "AutoEscalated",
            "system",
            {"from": old_level, "to": alert.risk_level},
        )
        changed += 1
    return changed


def create_or_deduplicate_alert(
    db: Session,
    *,
    zone_id: str,
    location: str,
    pincode: str | None,
    latitude: float | None,
    longitude: float | None,
    risk_score: float,
    message: str,
    language: str,
    actor: str,
    now: datetime | None = None,
) -> tuple[Alert, bool]:
    if not zone_id.strip() or not location.strip():
        raise ValueError("zone_id and location must not be blank")
    current = now or datetime.now(timezone.utc)
    auto_escalate_stale_alerts(db, current)
    previous = db.scalar(
        select(Alert)
        .where(
            Alert.zone_id == zone_id,
            Alert.deleted_at.is_(None),
            Alert.status != "Resolved",
        )
        .order_by(Alert.created_at.desc())
        .limit(1)
    )
    level = apply_hysteresis(risk_score, previous.risk_level if previous else None)
    dedupe = db.scalar(
        select(Alert)
        .where(
            Alert.zone_id == zone_id,
            Alert.risk_level == level,
            Alert.deleted_at.is_(None),
            Alert.created_at >= current - COOLDOWN,
            Alert.status != "Resolved",
        )
        .order_by(Alert.created_at.desc())
        .limit(1)
    )
    if dedupe:
        return dedupe, True

    alert = Alert(
        id=str(uuid.uuid4()),
        zone_id=zone_id,
        location=location,
        pincode=pincode,
        latitude=latitude,
        longitude=longitude,
        risk_score=risk_score,
        risk_level=level,
        status="Created",
        message=message,
        language=language,
        created_at=current,
        updated_at=current,
    )
    db.add(alert)
    db.flush()
    add_audit(
        db,
        alert,
        "Created",
        actor,
        {"risk_score": risk_score, "risk_level": level, "synthetic_policy": True},
    )
    return alert, False
