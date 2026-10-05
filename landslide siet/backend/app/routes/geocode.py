from fastapi import APIRouter, Query
from backend.app.services.geocoding_service import geocode_place

router = APIRouter()

@router.get("/api/geocode")
def get_geocode(query: str = Query(..., description="Place name to geocode")):
    return geocode_place(query)
