from fastapi import APIRouter
from backend.app.trend_tracker import trend_tracker

router = APIRouter()

@router.get("/api/trends")
def get_trends():
    return {"trend": trend_tracker.get_trend(87), "current": 87, "previous": 74, "projected": 92}
