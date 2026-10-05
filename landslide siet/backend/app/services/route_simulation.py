from __future__ import annotations

from typing import Any

from backend.app.gis.risk_zones import RiskSignals, calculate_risk_score

SIMULATION_LOCATIONS = {
    "coonor": {"id": "coonor", "name": "Coonoor", "admin_region": "Nilgiris District", "latitude": 11.35, "longitude": 76.8},
    "ooty": {"id": "ooty", "name": "Ooty", "admin_region": "Nilgiris District", "latitude": 11.41, "longitude": 76.7},
    "kodaikanal": {"id": "kodaikanal", "name": "Kodaikanal", "admin_region": "Dindigul District", "latitude": 10.24, "longitude": 77.48},
}


def simulate_scenario(payload: dict[str, Any]) -> dict[str, Any]:
    location = SIMULATION_LOCATIONS.get(payload["location_id"])
    if location is None:
        raise LookupError("Location not found")
    # Inputs not supplied by the caller are inherited from the explicitly DEMO baseline.
    baseline = {
        "rainfall_24h_mm": 18.0,
        "rainfall_7d_mm": 72.0,
        "soil_moisture_pct": 50.0,
        "slope_deg": 15.0,
        "ndvi": 0.6,
        "elevation_m": 800.0,
        "historical_landslides_nearby": 0.0,
    }
    by_id = {"coonor": (42.0, 156.0, 68.0, 27.0, 0.64, 520.0, 1.0),
             "ooty": (27.0, 98.0, 58.0, 18.0, 0.58, 2330.0, 1.0),
             "kodaikanal": (14.0, 60.0, 46.0, 12.0, 0.72, 2090.0, 0.0)}
    if location["id"] in by_id:
        rainfall24, rainfall7, moisture, slope, ndvi, elevation, history = by_id[location["id"]]
        baseline.update(rainfall_24h_mm=rainfall24, rainfall_7d_mm=rainfall7, soil_moisture_pct=moisture,
                        slope_deg=slope, ndvi=ndvi, elevation_m=elevation, historical_landslides_nearby=history)
    for key in ("rainfall_24h_mm", "rainfall_7d_mm", "soil_moisture_pct", "slope_deg"):
        if payload.get(key) is not None:
            baseline[key] = payload[key]
    before = calculate_risk_score(RiskSignals(**baseline))
    after_signals = RiskSignals(**baseline)
    if payload.get("road_cut"):
        after_signals.historical_landslides_nearby = min(4.0, after_signals.historical_landslides_nearby + 1)
    if payload.get("earthquake_magnitude") is not None and payload["earthquake_magnitude"] >= 4.0:
        after_signals.historical_landslides_nearby = min(4.0, after_signals.historical_landslides_nearby + 1)
    after = calculate_risk_score(after_signals)
    return {
        "status": "SIMULATED",
        "location": location,
        "baseline": {"score": before["score"], "level": before["level"]},
        "scenario": {"score": after["score"], "level": after["level"]},
        "inputs": payload,
        "disclaimer": "What-if output uses the DEMO weighted heuristic and is not a forecast or official warning.",
    }
