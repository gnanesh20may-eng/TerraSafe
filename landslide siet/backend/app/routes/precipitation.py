from fastapi import APIRouter, Query
from backend.app.services.gpm_service import get_gpm_precipitation

router = APIRouter()

@router.get("/api/precipitation")
def get_precipitation(lat: float = Query(...), lon: float = Query(...)):
    return get_gpm_precipitation(lat, lon)
