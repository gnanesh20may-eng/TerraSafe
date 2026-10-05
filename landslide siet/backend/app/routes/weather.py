from fastapi import APIRouter, Query
from backend.app.services.weather_service import get_weather_data

router = APIRouter()

@router.get("/api/weather")
def get_weather(lat: float = Query(...), lon: float = Query(...)):
    return get_weather_data(lat, lon)
