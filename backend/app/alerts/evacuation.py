"""Evacuation route adapter with no fabricated destinations or directions."""

from __future__ import annotations

import math
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


def nearest_simulated_shelter(latitude: float, longitude: float) -> dict[str, Any]:
    if not -90 <= latitude <= 90 or not -180 <= longitude <= 180:
        raise ValueError("latitude or longitude is outside WGS84 bounds")

    earth_radius_km = 6371.0088
    origin_latitude = math.radians(latitude)
    origin_longitude = math.radians(longitude)

    def distance_to(shelter: dict[str, Any]) -> float:
        shelter_latitude = math.radians(shelter["latitude"])
        shelter_longitude = math.radians(shelter["longitude"])
        latitude_delta = shelter_latitude - origin_latitude
        longitude_delta = shelter_longitude - origin_longitude
        haversine = (
            math.sin(latitude_delta / 2) ** 2
            + math.cos(origin_latitude)
            * math.cos(shelter_latitude)
            * math.sin(longitude_delta / 2) ** 2
        )
        return 2 * earth_radius_km * math.asin(
            math.sqrt(min(1.0, max(0.0, haversine)))
        )

    shelter = min(SIMULATED_SHELTERS, key=distance_to)
    return {
        "status": "SIMULATED",
        "feature_status": "SIMULATED",
        "origin": {"latitude": latitude, "longitude": longitude},
        "nearest_shelter": shelter,
        "distance_km": round(distance_to(shelter), 3),
        "distance_method": "straight-line Haversine distance",
        "route": None,
        "route_status": "MISSING",
        "notice": (
            "The destination is a simulated placeholder, not a real shelter. "
            "Distance is straight-line only; no navigable route is available."
        ),
    }


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
