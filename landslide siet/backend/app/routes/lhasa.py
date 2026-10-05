from fastapi import APIRouter, Query
from backend.app.services.lhasa_service import get_lhasa_reference

router = APIRouter()

@router.get("/api/lhasa")
def get_lhasa(lat: float = Query(...), lon: float = Query(...)):
    return get_lhasa_reference(lat, lon)
