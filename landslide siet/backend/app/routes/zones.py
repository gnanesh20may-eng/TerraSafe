from fastapi import APIRouter, Query
from backend.app.zone_data import ZONES

router = APIRouter()

@router.get("/api/zones")
def get_zones():
    return {"zones": ZONES}

@router.get("/api/zones/{zone_name}")
def get_zone(zone_name: str):
    zone = next((z for z in ZONES if z["name"].lower() == zone_name.lower()), None)
    if zone is None:
        return {"error": "Zone not found"}
    return zone
