from backend.app.config import DEMO_MODE
from backend.app.demo_data import get_demo_location


def get_osm_context(lat: float, lon: float):
    if DEMO_MODE:
        _, demo = get_demo_location(lat, lon)
        return {
            "status": "connected",
            "roads": [{"type": "road", "distance_km": demo.get("roads_proximity_km", 1.0)}],
            "settlements": [{"type": "settlement", "distance_km": demo.get("settlements_proximity_km", 1.0)}],
            "rivers": [{"type": "river", "distance_km": 2.4}],
            "important_locations": [{"name": "community facility", "distance_km": 1.2}],
            "source": "DEMO_DATA",
        }
    return {"status": "temporarily unavailable", "roads": [], "settlements": [], "rivers": [], "important_locations": [], "source": "fallback"}
