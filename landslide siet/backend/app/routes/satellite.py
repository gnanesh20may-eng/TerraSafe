from fastapi import APIRouter, Query
from backend.app.services.sentinel_service import get_sentinel_data
from backend.app.services.stac_service import search_stac_scenes

router = APIRouter()

@router.get("/api/satellite")
def get_satellite(lat: float = Query(...), lon: float = Query(...)):
    return get_sentinel_data(lat, lon)

@router.get("/api/satellite-scenes")
def get_satellite_scenes(lat: float = Query(...), lon: float = Query(...), date: str | None = None):
    return search_stac_scenes(lat, lon, date=date)
