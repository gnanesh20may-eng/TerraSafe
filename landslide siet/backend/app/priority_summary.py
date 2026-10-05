from __future__ import annotations
from typing import Any, Dict

from backend.app.zone_data import ZONES
from backend.app.vulnerable_locations import VULNERABLE_LOCATIONS


def get_priority_summary():
    return {
        "Priority 1": [loc["name"] for loc in VULNERABLE_LOCATIONS if loc["risk_priority"] == "Priority 1"],
        "Priority 2": [loc["name"] for loc in VULNERABLE_LOCATIONS if loc["risk_priority"] == "Priority 2"],
        "Priority 3": [loc["name"] for loc in VULNERABLE_LOCATIONS if loc["risk_priority"] == "Priority 3"],
        "zones": ZONES,
    }
