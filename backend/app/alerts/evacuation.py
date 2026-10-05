"""Evacuation route adapter with no fabricated destinations or directions."""

from __future__ import annotations

from typing import Any

SIMULATED_SHELTERS = (
    {
        "shelter_id": "sim-shelter-01",
        "name": "SIMULATED shelter placeholder 1",
        "latitude": 11.25,
        "longitude": 76.35,
        "status": "SIMULATED",
    },
    {
        "shelter_id": "sim-shelter-02",
        "name": "SIMULATED shelter placeholder 2",
        "latitude": 11.45,
        "longitude": 76.55,
        "status": "SIMULATED",
    },
    {
        "shelter_id": "sim-shelter-03",
        "name": "SIMULATED shelter placeholder 3",
        "latitude": 11.35,
        "longitude": 76.82,
        "status": "SIMULATED",
    },
)


class MockOpenRouteServiceAdapter:
    """Explicit placeholder until a verified shelter list and ORS key exist."""

    def nearest_route(self, latitude: float, longitude: float) -> dict[str, Any]:
        if not -90 <= latitude <= 90 or not -180 <= longitude <= 180:
            raise ValueError("latitude or longitude is outside WGS84 bounds")
        return {
            "status": "MISSING",
            "source": "no verified shelter dataset configured",
            "origin": {"latitude": latitude, "longitude": longitude},
            "nearest_shelter": None,
            "route": None,
            "message": (
                "No verified shelter data or navigable route is available. "
                "This endpoint does not provide evacuation directions."
            ),
            "adapter_status": "SCAFFOLD",
        }
