from backend.app.config import DEMO_MODE, OPENMETEO_BASE_URL
from backend.app.demo_data import DEMO_LOCATIONS
from backend.app.services.base import fetch_json


def geocode_place(query: str):
    q = query.strip().lower()
    if DEMO_MODE:
        for name, meta in DEMO_LOCATIONS.items():
            if q in name.lower():
                return {
                    "results": [{
                        "name": name,
                        "latitude": meta["lat"],
                        "longitude": meta["lon"],
                        "country": meta["country"],
                        "state": meta["state"],
                        "source": "DEMO_DATA",
                    }],
                    "status": "cached",
                }

    try:
        data = fetch_json(f"{OPENMETEO_BASE_URL}/search", params={"name": query, "count": 5, "language": "en"})
        results = data.get("results", [])
        return {
            "results": [{
                "name": item.get("name"),
                "latitude": item.get("latitude"),
                "longitude": item.get("longitude"),
                "country": item.get("country"),
                "state": item.get("admin1"),
                "source": "open-meteo",
            } for item in results],
            "status": "connected",
        }
    except Exception:
        return {"results": [], "status": "temporarily unavailable"}
