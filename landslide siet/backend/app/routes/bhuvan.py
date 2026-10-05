from fastapi import APIRouter, Query
from backend.app.services.bhuvan_service import get_bhuvan_data

router = APIRouter()

@router.get("/api/bhuvan")
def get_bhuvan(lat: float = Query(...), lon: float = Query(...)):
    return get_bhuvan_data(lat, lon)
