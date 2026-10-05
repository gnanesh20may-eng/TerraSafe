from fastapi import APIRouter, Query
from backend.app.simulator import simulate_risk

router = APIRouter()

@router.post("/api/simulation")
def run_simulation(
    zone: str = Query("Ooty"),
    rainfall: float = Query(90.0),
    soil_moisture: float = Query(65.0),
    slope: float = Query(30.0),
):
    return simulate_risk(zone, rainfall, soil_moisture, slope)
