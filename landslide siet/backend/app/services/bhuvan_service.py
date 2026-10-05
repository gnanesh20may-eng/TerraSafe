from backend.app.config import DEMO_MODE
from backend.app.demo_data import get_demo_location


def get_bhuvan_data(lat: float, lon: float):
    if DEMO_MODE:
        _, demo = get_demo_location(lat, lon)
        return {
            "status": "optional",
            "hazard": "landslide susceptibility reference map",
            "region": demo.get("region", "demo region"),
            "source": "DEMO_DATA",
        }
    return {"status": "temporarily unavailable", "hazard": None, "region": None, "source": "fallback"}
