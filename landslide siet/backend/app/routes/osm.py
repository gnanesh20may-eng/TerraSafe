from fastapi import APIRouter, Query
from backend.app.services.osm_service import get_osm_context

router = APIRouter()

@router.get("/api/osm")
def get_osm(lat: float = Query(...), lon: float = Query(...)):
    return get_osm_context(lat, lon)
