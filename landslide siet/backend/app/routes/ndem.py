from fastapi import APIRouter, Query
from backend.app.services.ndem_service import get_ndem_data

router = APIRouter()

@router.get("/api/ndem")
def get_ndem(lat: float = Query(...), lon: float = Query(...)):
    return get_ndem_data(lat, lon)
