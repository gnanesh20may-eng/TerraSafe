"""Evacuation route adapter with no fabricated destinations or directions."""

from __future__ import annotations

from typing import Any


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
