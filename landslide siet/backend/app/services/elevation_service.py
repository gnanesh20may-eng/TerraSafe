from backend.app.config import DEMO_MODE, OPENMETEO_BASE_URL
from backend.app.demo_data import get_demo_location
from backend.app.services.base import fetch_json


def get_elevation_data(lat: float, lon: float):
    if DEMO_MODE:
        _, demo = get_demo_location(lat, lon)
        return {
            "status": "cached",
            "elevation_m": demo.get("elevation_m", 1500),
            "slope_deg": demo.get("slope_deg", 20),
            "source": "DEMO_DATA",
        }

    try:
        data = fetch_json(f"{OPENMETEO_BASE_URL}/elevation", params={"latitude": lat, "longitude": lon})
        elevation = data.get("elevation", [0])[0]
        return {"status": "connected", "elevation_m": elevation, "slope_deg": None, "source": "open-meteo"}
    except Exception:
        return {"status": "temporarily unavailable", "elevation_m": None, "slope_deg": None, "source": "fallback"}
