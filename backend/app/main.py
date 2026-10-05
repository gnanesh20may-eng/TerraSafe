"""FastAPI entry point for TerraSafe data, risk, SOS, and alert APIs."""

from __future__ import annotations

import json
import os
import re
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Query, Response, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from backend.app.alerts.cap import export_cap
from backend.app.alerts.engine import (
    TRANSITIONS,
    add_audit,
    create_or_deduplicate_alert,
    point_in_geofence,
    verify_audit_chain,
)
from backend.app.alerts.evacuation import MockOpenRouteServiceAdapter
from backend.app.alerts.notifications import (
    CHANNELS,
    notification_adapters,
    render_message,
)
from backend.app.alerts.schemas import (
    AlertCreate,
    AlertTransition,
    AlertUpdate,
    ScenarioInput,
    SmsInbound,
    SosCreate,
)
from backend.app.data_sources import get_source_health
from backend.app.database import Base, engine, get_db
from backend.app.ml.inference import infer_risk
from backend.app.ml.synthetic_data import FEATURE_COLUMNS, generate_nilgiris_pilot
from backend.app.models import Alert, AlertAudit, SosRequest
from backend.app.security import require_roles

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
METRICS_PATH = REPOSITORY_ROOT / "ml" / "data" / "generated" / "metrics.json"


@asynccontextmanager
async def lifespan(_app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="TerraSafe",
    description=(
        "Experimental landslide decision support. Not a replacement for "
        "official IMD, NDMA, or GSI warnings."
    ),
    version="0.2.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip().rstrip("/")
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:3001,http://127.0.0.1:3001",
        ).split(",")
        if origin.strip()
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


def _alert_payload(alert: Alert, *, deduplicated: bool | None = None) -> dict[str, Any]:
    output = {
        "id": alert.id,
        "zone_id": alert.zone_id,
        "location": alert.location,
        "pincode": alert.pincode,
        "latitude": alert.latitude,
        "longitude": alert.longitude,
        "risk_score": alert.risk_score,
        "risk_level": alert.risk_level,
        "status": alert.status,
        "message": alert.message,
        "language": alert.language,
        "created_at": alert.created_at.isoformat(),
        "updated_at": alert.updated_at.isoformat(),
        "feature_status": "DEMO",
        "disclaimer": "Not a replacement for official IMD, NDMA, or GSI warnings.",
    }
    if deduplicated is not None:
        output["deduplicated"] = deduplicated
    return output


def _get_alert(db: Session, alert_id: str) -> Alert:
    alert = db.scalar(
        select(Alert).where(Alert.id == alert_id, Alert.deleted_at.is_(None))
    )
    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@app.get("/health", tags=["health"])
def health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {
        "status": "LIVE",
        "database": "LIVE",
        "disclaimer": "Service health is not a warning or safety assessment.",
    }


@app.get("/api/v1/health/data-sources", tags=["data"])
def data_source_health():
    """Return registry metadata and latest source-check status."""
    return get_source_health()


@app.get("/api/v1/risk/{location}", tags=["risk"])
def risk_by_location(location: str):
    """Return synthetic Nilgiris susceptibility until real inputs are approved."""
    if location.casefold() not in {"nilgiris", "nilgiris-tamil-nadu"}:
        return {
            "location": location,
            "status": "MISSING",
            "message": "No verified terrain, inventory, or weather inputs are available for this location.",
            "disclaimer": "Not a replacement for official IMD, NDMA, or GSI warnings.",
        }
    pilot = generate_nilgiris_pilot(grid_size=10)
    row = pilot.cells.iloc[len(pilot.cells) // 2]
    result = infer_risk(
        {name: float(row[name]) for name in FEATURE_COLUMNS},
        zone="Nilgiris",
    )
    return {"location": location, **result}


@app.post("/sos", status_code=status.HTTP_201_CREATED, tags=["sos"])
def create_sos(request: SosCreate, db: Session = Depends(get_db)):
    """Create a minimal SOS record; phone and message are not returned."""
    record = SosRequest(
        id=str(uuid.uuid4()),
        phone=request.phone,
        pincode=request.pincode,
        latitude=request.latitude,
        longitude=request.longitude,
        message=request.message,
        status="Created",
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return {
        "id": record.id,
        "status": record.status,
        "created_at": record.created_at.isoformat(),
        "feature_status": "DEMO",
        "disclaimer": "This prototype does not dispatch emergency services.",
    }


@app.get("/sos", tags=["sos"])
def list_sos(
    _actor: dict[str, Any] = Depends(
        require_roles("admin", "district_officer", "field_responder")
    ),
    db: Session = Depends(get_db),
):
    records = db.scalars(select(SosRequest).order_by(SosRequest.created_at.desc())).all()
    return {
        "sos": [
            {
                "id": record.id,
                "pincode": record.pincode,
                "latitude": record.latitude,
                "longitude": record.longitude,
                "message": record.message,
                "status": record.status,
                "created_at": record.created_at.isoformat(),
            }
            for record in records
        ],
        "feature_status": "DEMO",
    }


@app.post("/api/v1/alerts", status_code=status.HTTP_201_CREATED, tags=["alerts"])
def create_alert(
    request: AlertCreate,
    actor: dict[str, Any] = Depends(require_roles("admin", "district_officer")),
    db: Session = Depends(get_db),
):
    if request.geofence_bounds and not point_in_geofence(
        request.latitude,
        request.longitude,
        request.geofence_bounds,
    ):
        raise HTTPException(status_code=422, detail="Coordinates are outside geofence")
    from backend.app.alerts.engine import risk_level

    level = risk_level(request.risk_score)
    message = request.message or render_message(
        request.language, level, request.location
    )
    try:
        alert, deduplicated = create_or_deduplicate_alert(
            db,
            zone_id=request.zone_id,
            location=request.location,
            pincode=request.pincode,
            latitude=request.latitude,
            longitude=request.longitude,
            risk_score=request.risk_score,
            message=message,
            language=request.language,
            actor=actor["subject"],
        )
        db.commit()
        db.refresh(alert)
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return _alert_payload(alert, deduplicated=deduplicated)


@app.get("/api/v1/alerts", tags=["alerts"])
def list_alerts(
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    alerts = db.scalars(
        select(Alert)
        .where(Alert.deleted_at.is_(None))
        .order_by(Alert.created_at.desc())
        .limit(limit)
    ).all()
    return {"alerts": [_alert_payload(alert) for alert in alerts]}


@app.get("/api/v1/alerts/{alert_id}", tags=["alerts"])
def get_alert(
    alert_id: str,
    db: Session = Depends(get_db),
):
    return _alert_payload(_get_alert(db, alert_id))


@app.patch("/api/v1/alerts/{alert_id}", tags=["alerts"])
def update_alert(
    alert_id: str,
    request: AlertUpdate,
    actor: dict[str, Any] = Depends(
        require_roles("admin", "district_officer", "field_responder")
    ),
    db: Session = Depends(get_db),
):
    alert = _get_alert(db, alert_id)
    changes = request.model_dump(exclude_unset=True)
    if not changes:
        raise HTTPException(status_code=422, detail="At least one field is required")
    for key, value in changes.items():
        if value is not None:
            setattr(alert, key, value)
    alert.updated_at = datetime.now(timezone.utc)
    add_audit(db, alert, "Updated", actor["subject"], changes)
    db.commit()
    db.refresh(alert)
    return _alert_payload(alert)


@app.delete("/api/v1/alerts/{alert_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["alerts"])
def delete_alert(
    alert_id: str,
    actor: dict[str, Any] = Depends(require_roles("admin")),
    db: Session = Depends(get_db),
):
    alert = _get_alert(db, alert_id)
    if alert.status not in {"Created", "Resolved"}:
        raise HTTPException(status_code=409, detail="Only Created or Resolved alerts may be deleted")
    now = datetime.now(timezone.utc)
    add_audit(db, alert, "Deleted", actor["subject"], {})
    alert.deleted_at = now
    alert.updated_at = now
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.post("/api/v1/alerts/{alert_id}/transition", tags=["alerts"])
def transition_alert(
    alert_id: str,
    request: AlertTransition,
    actor: dict[str, Any] = Depends(
        require_roles("admin", "district_officer", "field_responder")
    ),
    db: Session = Depends(get_db),
):
    alert = _get_alert(db, alert_id)
    expected = TRANSITIONS.get(alert.status)
    if request.event != expected:
        raise HTTPException(
            status_code=409,
            detail=f"Invalid lifecycle transition from {alert.status}; expected {expected}",
        )
    actor_roles = {
        "Approved": {"admin", "district_officer"},
        "Sent": {"admin", "district_officer"},
        "Delivered": {"admin", "district_officer"},
        "Acknowledged": {"admin", "district_officer", "field_responder"},
        "Resolved": {"admin", "district_officer", "field_responder"},
    }
    if actor["role"] not in actor_roles[request.event]:
        raise HTTPException(status_code=403, detail="Role cannot perform this lifecycle transition")
    payload: dict[str, Any] = {}
    if request.event == "Sent":
        payload["notifications"] = [
            notification_adapters()[channel].send(alert) for channel in CHANNELS
        ]
    alert.status = request.event
    alert.updated_at = datetime.now(timezone.utc)
    add_audit(db, alert, request.event, actor["subject"], payload)
    db.commit()
    db.refresh(alert)
    result = _alert_payload(alert)
    if payload:
        result["notifications"] = payload["notifications"]
    return result


@app.get("/api/v1/alerts/{alert_id}/audit", tags=["alerts"])
def alert_audit(
    alert_id: str,
    db: Session = Depends(get_db),
):
    alert = _get_alert(db, alert_id)
    entries = db.scalars(
        select(AlertAudit)
        .where(AlertAudit.alert_id == alert.id)
        .order_by(AlertAudit.sequence)
    ).all()
    serialized_entries = []
    for entry in entries:
        try:
            payload = json.loads(entry.payload)
            payload_error = None
        except json.JSONDecodeError:
            payload = None
            payload_error = "invalid_json"
        serialized_entries.append(
            {
                "sequence": entry.sequence,
                "event": entry.event,
                "actor": entry.actor,
                "payload": payload,
                "payload_error": payload_error,
                "previous_hash": entry.previous_hash,
                "entry_hash": entry.entry_hash,
                "created_at": entry.created_at,
            }
        )
    return {
        "entries": serialized_entries,
        "chain_valid": verify_audit_chain(entries),
    }


@app.get("/api/v1/alerts/{alert_id}/cap", tags=["alerts"])
def alert_cap(
    alert_id: str,
    db: Session = Depends(get_db),
):
    return Response(content=export_cap(_get_alert(db, alert_id)), media_type="application/cap+xml")


@app.post("/api/v1/simulate", tags=["simulation"])
def simulate_scenario(request: ScenarioInput):
    """Return a deterministic what-if index, never a live warning."""
    rainfall_trigger = min(1.0, request.rainfall_mm / (request.duration_hours * 2))
    earthquake_trigger = (
        min(1.0, max(0.0, (request.earthquake_magnitude - 2) / 5))
        if request.earthquake_magnitude is not None
        else 0.0
    )
    score = min(
        1.0,
        request.baseline_score
        + 0.3 * rainfall_trigger
        + 0.2 * earthquake_trigger
        + (0.1 if request.road_cut else 0),
    )
    return {
        "status": "SIMULATED",
        "risk_score": round(score, 4),
        "risk_level": "Green" if score < 0.25 else "Yellow" if score < 0.5 else "Orange" if score < 0.75 else "Red",
        "inputs": request.model_dump(),
        "method": "transparent demonstration scenario; not calibrated",
        "disclaimer": "Not a replacement for official IMD, NDMA, or GSI warnings.",
    }


@app.get("/api/v1/evacuation/nearest", tags=["evacuation"])
def nearest_evacuation_route(
    latitude: float = Query(ge=-90, le=90),
    longitude: float = Query(ge=-180, le=180),
):
    result = MockOpenRouteServiceAdapter().nearest_route(latitude, longitude)
    return {**result, "feature_status": "MISSING"}


@app.get("/api/v1/models/metrics", tags=["models"])
def model_metrics():
    if not METRICS_PATH.is_file():
        return {
            "status": "MISSING",
            "metrics": None,
            "message": "No generated evaluation file exists in this checkout.",
        }
    with METRICS_PATH.open(encoding="utf-8") as metrics_file:
        metrics = json.load(metrics_file)
    return {
        "status": "SIMULATED"
        if "SYNTHETIC" in str(metrics.get("data_source", "")).upper()
        else "SCAFFOLD",
        "metrics": metrics,
    }


@app.post("/sms/inbound", tags=["messaging"])
def inbound_sms(request: SmsInbound, db: Session = Depends(get_db)):
    """Mock inbound RISK <pincode> query. No SMS provider is contacted."""
    match = re.fullmatch(r"RISK\s+(\d{4,10})", request.message_text.strip(), re.IGNORECASE)
    if not match:
        return {
            "status": "DEMO",
            "reply": "Use RISK <pincode>. This mock does not send an SMS.",
            "provider": "mock",
        }
    pincode = match.group(1)
    alert = db.scalar(
        select(Alert)
        .where(
            Alert.pincode == pincode,
            Alert.deleted_at.is_(None),
            Alert.status != "Resolved",
        )
        .order_by(Alert.created_at.desc())
        .limit(1)
    )
    if alert is None:
        return {
            "status": "MISSING",
            "reply": "No alert record is available for this pincode.",
            "provider": "mock",
        }
    return {
        "status": "DEMO",
        "reply": f"DEMO risk {alert.risk_level} for {alert.location}. Follow official IMD/NDMA/GSI warnings.",
        "provider": "mock",
    }


@app.get("/rescue", tags=["rescue"])
def rescue_status():
    return {
        "status": "SCAFFOLD",
        "message": "Rescue workflows are not implemented in this checkout.",
        "disclaimer": "Not a replacement for official emergency services or IMD/NDMA/GSI warnings.",
    }
