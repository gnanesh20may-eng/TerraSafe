from backend.app.config import DEMO_MODE
from backend.app.demo_data import get_demo_location


def get_gpm_precipitation(lat: float, lon: float):
    if DEMO_MODE:
        _, demo = get_demo_location(lat, lon)
        return {
            "status": "cached",
            "rain_24h_mm": demo.get("rain_24h_mm", 60),
            "rain_72h_mm": demo.get("rain_72h_mm", 120),
            "source": "DEMO_DATA",
        }
    return {"status": "temporarily unavailable", "rain_24h_mm": None, "rain_72h_mm": None, "source": "fallback"}
