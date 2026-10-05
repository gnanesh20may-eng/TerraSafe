from __future__ import annotations

import json
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, tostring

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from pydantic import BaseModel

from backend.app.alert_engine import alert_engine
from backend.app.api.schemas import AlertCreate, AlertTransition, SimulationRequest
from backend.app.core.auth import current_principal, require_roles
from backend.app.gis.risk_zones import build_risk_zone_geojson
from backend.app.providers.base import LocationRef, ProviderUnavailableError
from backend.app.services.environment_service import environment_service
from backend.app.services.persistence_service import PersistenceService
from backend.app.services.route_simulation import simulate_scenario
from backend.app.services.risk_service import risk_service

router = APIRouter(prefix="/api/v1", tags=["v1"])
DATA_HEALTH_PATH = Path(__file__).resolve().parents[4] / "data_sources" / "health.json"
METRICS_PATH = Path(__file__).resolve().parents[4] / "ml" / "data" / "generated" / "metrics.json"
persistence = PersistenceService()


class LocationSummary(BaseModel):
    id: str
    name: str
    latitude: float
    longitude: float
    admin_region: str = "Demo district"
    risk_level: str = "WATCH"


class RiskResponse(BaseModel):
    location: dict
    risk: dict
    confidence: dict
    environment: dict
    terrain: dict
    contributors: list[dict]
    recommendation: dict
    timestamp: str


DEMO_LOCATIONS = [
    {
        "id": "coonor",
        "name": "Coonoor",
        "latitude": 11.35,
        "longitude": 76.8,
        "admin_region": "Nilgiris District",
        "risk_level": "HIGH",
    },
    {
        "id": "ooty",
        "name": "Ooty",
        "latitude": 11.41,
        "longitude": 76.7,
        "admin_region": "Nilgiris District",
        "risk_level": "WATCH",
    },
    {
        "id": "kodaikanal",
        "name": "Kodaikanal",
        "latitude": 10.24,
        "longitude": 77.48,
        "admin_region": "Dindigul District",
        "risk_level": "LOW",
    },
]


def get_location_by_id(location_id: str) -> dict | None:
    for location in DEMO_LOCATIONS:
        if location["id"] == location_id:
            return location
    return None


@router.get("/health")
def health():
    return {
        "status": "ok",
        "service": "landsense-api",
        "environment": "development",
        "demo_mode": True,
    }


@router.get("/locations/search")
def search_locations(q: str = Query(default="", description="Location search text")):
    query = q.strip().lower()
    if not query:
        return {"results": DEMO_LOCATIONS}

    results = [
        location
        for location in DEMO_LOCATIONS
        if query in location["name"].lower() or query in location["admin_region"].lower()
    ]
    return {"results": results}


@router.get("/locations/{location_id}")
def get_location(location_id: str):
    location = get_location_by_id(location_id)
    if location is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found")
    return location


@router.get("/risk/{location_id}", response_model=RiskResponse)
def get_risk(location_id: str):
    location = get_location_by_id(location_id)
    if location is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found")
    location_ref = LocationRef(
        id=location["id"],
        name=location["name"],
        latitude=float(location["latitude"]),
        longitude=float(location["longitude"]),
        admin_region=location["admin_region"],
    )
    result = risk_service.evaluate_location(location_ref)
    alert = alert_engine.generate_alert(result["risk"]["score"], previous_level=None)
    return {
        "location": result["location"],
        "risk": result["risk"],
        "confidence": result["confidence"],
        "environment": result["environment"],
        "terrain": result["terrain"],
        "contributors": result["contributors"],
        "recommendation": {
            "severity": result["recommendation"]["severity"],
            "message": alert["message"],
        },
        "timestamp": result["timestamp"],
    }


@router.get("/risk/{location_id}/history")
def get_risk_history(location_id: str):
    return {
        "location_id": location_id,
        "history": [
            {"timestamp": "2026-10-05T09:00:00Z", "score": 58, "level": "HIGH"},
            {"timestamp": "2026-10-05T10:00:00Z", "score": 63, "level": "HIGH"},
            {"timestamp": "2026-10-05T12:00:00Z", "score": 68, "level": "HIGH"},
        ],
    }


@router.get("/environment/{location_id}")
def get_environment(location_id: str):
    location = get_location_by_id(location_id)
    if location is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found")
    location_ref = LocationRef(
        id=location["id"],
        name=location["name"],
        latitude=float(location["latitude"]),
        longitude=float(location["longitude"]),
        admin_region=location["admin_region"],
    )
    try:
        return environment_service.get_environment(location_ref)
    except ProviderUnavailableError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error


@router.get("/terrain/{location_id}")
def get_terrain(location_id: str):
    location = get_location_by_id(location_id)
    if location is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found")
    location_ref = LocationRef(
        id=location["id"],
        name=location["name"],
        latitude=float(location["latitude"]),
        longitude=float(location["longitude"]),
        admin_region=location["admin_region"],
    )
    try:
        snapshot = environment_service.get_environment(location_ref)
    except ProviderUnavailableError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    return {"location": location["name"], "terrain": snapshot["terrain"], "source": snapshot["terrain"]["source"]}


@router.get("/map/risk-zones")
def map_risk_zones():
    risk_scores = {}
    for location in DEMO_LOCATIONS:
        location_ref = LocationRef(
            id=location["id"],
            name=location["name"],
            latitude=float(location["latitude"]),
            longitude=float(location["longitude"]),
            admin_region=location["admin_region"],
        )
        risk_scores[location["id"]] = risk_service.evaluate_location(location_ref)["risk"]["score"]
    return build_risk_zone_geojson(DEMO_LOCATIONS, risk_scores)


@router.get("/safe-zones")
def get_safe_zones():
    return {
        "results": [
            {"id": "shelter-1", "name": "Town Relief Center", "latitude": 11.36, "longitude": 76.81, "type": "Emergency shelter"},
            {"id": "shelter-2", "name": "District Control Hub", "latitude": 11.54, "longitude": 76.71, "type": "Government emergency center"},
        ]
    }


@router.get("/rescue/nearby")
def get_rescue_nearby():
    return {
        "location": "Coonoor",
        "safe_zones": [
            {"name": "Town Relief Center", "distance_km": 2.8, "capacity": 120},
            {"name": "District Control Hub", "distance_km": 6.1, "capacity": 200},
        ],
        "emergency_contacts": [
            {"name": "District Control Room", "phone": "+91-00000-00000", "status": "demo"},
        ],
    }


@router.get("/alerts")
def get_alerts():
    return {"items": persistence.list_alerts()}


@router.post("/alerts", status_code=status.HTTP_201_CREATED)
def create_alert(
    payload: AlertCreate,
    principal: dict = Depends(require_roles("admin", "district_officer")),
):
    try:
        return persistence.create_alert(payload.location_id, payload.risk_level, payload.message, principal["sub"])
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@router.post("/alerts/{alert_id}/lifecycle")
def transition_alert(
    alert_id: str,
    payload: AlertTransition,
    principal: dict = Depends(require_roles("admin", "district_officer", "field_responder")),
):
    if payload.state == "APPROVED" and principal["role"] not in {"admin", "district_officer"}:
        raise HTTPException(status_code=403, detail="Only an authority role may approve alerts")
    try:
        return persistence.transition_alert(alert_id, payload.state.upper(), principal["sub"], payload.detail)
    except LookupError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error


@router.get("/alerts/{alert_id}/cap")
def export_alert_cap(alert_id: str):
    alert = next((item for item in persistence.list_alerts(limit=500) if item["id"] == alert_id), None)
    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    root = Element("alert", xmlns="urn:oasis:names:tc:emergency:cap:1.2")
    for name, value in (
        ("identifier", alert["id"]),
        ("sender", "terrasafe-demo"),
        ("sent", alert["created_at"]),
        ("status", "Test"),
        ("msgType", "Alert"),
        ("scope", "Public"),
    ):
        SubElement(root, name).text = str(value)
    info = SubElement(root, "info")
    SubElement(info, "category").text = "Safety"
    SubElement(info, "event").text = f"Landslide risk {alert['risk_level']}"
    SubElement(info, "urgency").text = "Unknown"
    cap_severity = {"LOW": "Minor", "WATCH": "Moderate", "HIGH": "Severe", "CRITICAL": "Extreme"}
    SubElement(info, "severity").text = cap_severity[alert["risk_level"]]
    SubElement(info, "certainty").text = "Unknown"
    SubElement(info, "headline").text = "DEMO alert; not an official warning"
    SubElement(info, "description").text = alert["message"]
    SubElement(info, "instruction").text = "Follow official IMD, NDMA, GSI, and local authority instructions."
    return Response(content=tostring(root, encoding="unicode"), media_type="application/cap+xml")


@router.post("/simulate")
def simulate(payload: SimulationRequest):
    try:
        return simulate_scenario(payload.model_dump())
    except LookupError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.post("/rescue/evacuation")
def evacuation_route(latitude: float = Query(ge=-90, le=90), longitude: float = Query(ge=-180, le=180)):
    import math

    shelters = [
        {"id": "shelter-1", "name": "Town Relief Center", "latitude": 11.36, "longitude": 76.81, "type": "DEMO emergency shelter"},
        {"id": "shelter-2", "name": "District Control Hub", "latitude": 11.54, "longitude": 76.71, "type": "DEMO government center"},
    ]
    def distance_km(shelter):
        lat1, lat2 = math.radians(latitude), math.radians(shelter["latitude"])
        dlat = lat2 - lat1
        dlon = math.radians(shelter["longitude"] - longitude)
        arc = 2 * math.asin(math.sqrt(math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2))
        return 6371.0 * arc
    destination = min(shelters, key=distance_km)
    return {
        "status": "SIMULATED",
        "destination": destination,
        "straight_line_distance_km": round(distance_km(destination), 2),
        "route": None,
        "route_provider": "MOCK — road network and hazard avoidance are not integrated",
        "disclaimer": "Not a safest-route guarantee. Follow local authority instructions.",
    }


@router.get("/rescue/route")
def get_rescue_route(latitude: float = Query(ge=-90, le=90), longitude: float = Query(ge=-180, le=180)):
    return evacuation_route(latitude, longitude)


@router.post("/sms/inbound")
def inbound_sms(payload: dict):
    text = str(payload.get("text", "")).strip().upper()
    parts = text.split()
    if len(parts) != 2 or parts[0] != "RISK" or not parts[1].isdigit() or len(parts[1]) != 6:
        return {"status": "SIMULATED", "reply": "Use RISK <6-digit pincode>. No SMS was sent."}
    return {"status": "SIMULATED", "reply": "Pincode risk lookup is not configured. No SMS was sent."}


@router.get("/models/metrics")
def model_metrics():
    if not METRICS_PATH.is_file():
        return {"status": "MISSING", "metrics": None, "message": "No evaluated model metrics are available."}
    try:
        return {"status": "DEMO", "metrics": json.loads(METRICS_PATH.read_text(encoding="utf-8"))}
    except (OSError, json.JSONDecodeError) as error:
        raise HTTPException(status_code=503, detail="Model metrics file is unreadable") from error


@router.get("/data-sources")
def get_data_sources():
    return {
        "weather_source": "DEMO WEATHER PROVIDER",
        "satellite_source": "DEMO SATELLITE PROVIDER",
        "terrain_source": "DEMO TERRAIN PROVIDER",
        "last_update": "2026-10-05T12:00:00Z",
    }


@router.get("/health/data-sources")
def health_data_sources():
    if not DATA_HEALTH_PATH.exists():
        return {
            "status": "NEEDS_REVIEW",
            "updated_at": None,
            "sources": [],
            "message": "Run scripts/check_sources.py to generate a source-health snapshot.",
        }
    try:
        return json.loads(DATA_HEALTH_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise HTTPException(status_code=503, detail="Data-source health snapshot is unreadable") from error
