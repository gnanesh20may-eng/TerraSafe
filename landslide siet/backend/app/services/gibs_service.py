from backend.app.config import DEMO_MODE
from backend.app.demo_data import get_demo_location


def get_gibs_layer(lat: float, lon: float, layer: str = "MODIS_Terra_Land_Surface_Temp"):
    if DEMO_MODE:
        _, demo = get_demo_location(lat, lon)
        return {
            "status": "cached",
            "layer": layer,
            "url": "demo://gibs/layer",
            "bbox": [lon - 0.15, lat - 0.15, lon + 0.15, lat + 0.15],
            "source": "DEMO_DATA",
        }
    return {"status": "temporarily unavailable", "layer": layer, "url": None, "source": "fallback"}
