from fastapi import APIRouter, Query
from backend.app.services.elevation_service import get_elevation_data

router = APIRouter()

@router.get("/api/elevation")
def get_elevation(lat: float = Query(...), lon: float = Query(...)):
    return get_elevation_data(lat, lon)
