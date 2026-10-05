from fastapi import APIRouter, Query
from backend.app.services.geocoding_service import geocode_place
from backend.app.services.weather_service import get_weather_data
from backend.app.services.elevation_service import get_elevation_data
from backend.app.services.sentinel_service import get_sentinel_data
from backend.app.services.gpm_service import get_gpm_precipitation

router = APIRouter()

@router.get("/api/analysis")
def get_analysis(lat: float = Query(...), lon: float = Query(...), query: str | None = None):
    place = geocode_place(query or "Ooty")
    weather = get_weather_data(lat, lon)
    elevation = get_elevation_data(lat, lon)
    satellite = get_sentinel_data(lat, lon)
    precipitation = get_gpm_precipitation(lat, lon)
    return {
        "place": place,
        "weather": weather,
        "elevation": elevation,
        "satellite": satellite,
        "precipitation": precipitation,
    }
