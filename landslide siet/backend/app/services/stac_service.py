from backend.app.config import DEMO_MODE
from backend.app.demo_data import get_demo_location


def search_stac_scenes(lat: float, lon: float, date: str | None = None):
    if DEMO_MODE:
        _, demo = get_demo_location(lat, lon)
        return {
            "status": "cached",
            "scenes": [{
                "id": "demo-sentinel-scene",
                "date": date or "2026-10-05",
                "cloud_cover_pct": demo.get("sentinel_cloud_cover_pct", 20),
                "bbox": [lon - 0.1, lat - 0.1, lon + 0.1, lat + 0.1],
                "source": "DEMO_DATA",
            }],
            "source": "DEMO_DATA",
        }
    return {"status": "temporarily unavailable", "scenes": [], "source": "fallback"}
