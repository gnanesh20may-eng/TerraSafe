from backend.app.config import DEMO_MODE
from backend.app.demo_data import get_demo_location


def get_lhasa_reference(lat: float, lon: float):
    if DEMO_MODE:
        _, demo = get_demo_location(lat, lon)
        return {
            "status": "optional",
            "reference_hazard": demo.get("reference_hazard", "reference hazard not available"),
            "notes": "Reference hazard layer only for comparison and validation. Not our prediction.",
            "source": "DEMO_DATA_REFERENCE_ONLY",
        }
    return {
        "status": "optional",
        "reference_hazard": "not available",
        "notes": "Reference hazard layer only. Not a prediction claim.",
        "source": "reference-only",
    }
