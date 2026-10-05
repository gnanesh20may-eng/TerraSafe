from backend.app.config import DEMO_MODE
from backend.app.demo_data import get_demo_location


def get_sentinel_data(lat: float, lon: float):
    if DEMO_MODE:
        _, demo = get_demo_location(lat, lon)
        return {
            "status": "cached",
            "ndvi": demo.get("ndvi", 0.45),
            "vegetation": demo.get("vegetation_cover", "moderate"),
            "cloud_cover_pct": demo.get("sentinel_cloud_cover_pct", 20),
            "source": "DEMO_DATA",
        }
    return {
        "status": "temporarily unavailable",
        "ndvi": None,
        "vegetation": None,
        "cloud_cover_pct": None,
        "source": "fallback",
    }
