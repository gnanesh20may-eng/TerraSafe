from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel

from backend.app.providers.base import LocationRef
from backend.app.services.environment_service import environment_service

router = APIRouter(prefix="/api/v1", tags=["v1"])


class LocationSummary(BaseModel):
    id: str
    name: str
    latitude: float
    longitude: float
    admin_region: str = "Demo district"
    risk_level: str = "WATCH"


class RiskResponse(BaseModel):
    location: dict[str, Any]
    risk: dict[str, Any]
    confidence: dict[str, Any]
    environment: dict[str, Any]
    terrain: dict[str, Any]
    contributors: list[dict[str, Any]]
    recommendation: dict[str, Any]
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
        "service": "terrasafe-api",
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

    base_score = {"coonor": 68, "ooty": 41, "kodaikanal": 18}.get(location_id, 32)
    if base_score >= 75:
        risk_level = "CRITICAL"
    elif base_score >= 50:
        risk_level = "HIGH"
    elif base_score >= 25:
        risk_level = "WATCH"
    else:
        risk_level = "LOW"

    trend = "INCREASING" if base_score >= 50 else "STABLE"
    if base_score < 25:
        trend = "DECREASING"

    return {
        "location": {
            "name": location["name"],
            "latitude": location["latitude"],
            "longitude": location["longitude"],
            "admin_region": location["admin_region"],
        },
        "risk": {"score": base_score, "level": risk_level, "trend": trend},
        "confidence": {"available": True, "value": 0.8},
        "environment": {
            "rainfall_24h_mm": 42 if base_score >= 50 else 18,
            "soil_moisture_pct": 68 if base_score >= 50 else 52,
            "wind_speed_kmh": 16,
            "temperature_c": 23.4,
        },
        "terrain": {"elevation_m": 520, "slope_deg": 27, "vegetation_index": 0.64},
        "contributors": [
            {"factor": "Rainfall", "impact": "HIGH", "direction": "INCREASE"},
            {"factor": "Soil Moisture", "impact": "HIGH", "direction": "INCREASE"},
            {"factor": "Slope", "impact": "MEDIUM", "direction": "INCREASE"},
            {"factor": "Recent accumulation", "impact": "MEDIUM", "direction": "INCREASE"},
        ],
        "recommendation": {
            "severity": risk_level,
            "message": "Conditions are being monitored. Follow official local guidance and avoid steep vulnerable routes unless necessary.",
        },
        "timestamp": "2026-10-05T12:00:00Z",
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
    return environment_service.get_environment(location_ref)


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
    snapshot = environment_service.get_environment(location_ref)
    return {"location": location["name"], "terrain": snapshot["terrain"], "source": snapshot["terrain"]["source"]}


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
    return {
        "items": [
            {"id": "a1", "risk_state": "HIGH", "alert_state": "NEW", "message": "Elevated rainfall and soil moisture in monitored area.", "created_at": "2026-10-05T11:40:00Z"},
        ]
    }


def test_environment_response_keeps_live_weather_separate_from_demo_layers(monkeypatch):
    from backend.app.providers.base import WeatherConditions

    monkeypatch.setattr(
        environment_service.weather_provider,
        "get_current_weather",
        lambda location: WeatherConditions(12, 48, 37, 10, 21, "open-meteo"),
    )
    location = LocationRef("coonor", "Coonoor", 11.35, 76.8, "Nilgiris District")

    snapshot = environment_service.get_environment(location)

    assert snapshot["weather"]["rainfall_24h_mm"] == 12
    assert snapshot["weather"]["source"] == "open-meteo"
    assert snapshot["data_status"] == "LIVE WEATHER + DEMO TERRAIN/SATELLITE"
    assert snapshot["terrain"]["source"].startswith("DEMO")
    assert snapshot["satellite"]["source"].startswith("DEMO")
