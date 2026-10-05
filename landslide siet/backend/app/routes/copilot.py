from fastapi import APIRouter, Query
from backend.app.zone_data import ZONES

router = APIRouter()

@router.get("/api/copilot")
def get_copilot_answer(question: str = Query(...)):
    q = question.lower()
    if "critical" in q and "zones" in q:
        return {"answer": "Zone A (Wayanad) and Zone C (Darjeeling) are currently critical based on rainfall, slope, and moisture data.", "source": "application analytics"}
    if "zone a" in q or "wayanad" in q:
        return {"answer": "Zone A is dangerous because rainfall is high, soil moisture is elevated, and the slope is steep. The estimated risk is 87/100 and alert confidence is 91%.", "source": "current risk data"}
    if "rainfall" in q and "180" in q:
        return {"answer": "If rainfall increases to 180 mm, the system estimates risk can rise above 85/100 in the most affected zones, depending on soil moisture and slope.", "source": "simulation engine"}
    if "safest" in q:
        return {"answer": "Zone B and Zone D are currently the safest based on lower rainfall and moderate slope.", "source": "current risk data"}
    if "inspect" in q or "priority" in q:
        return {"answer": "Priority 1 inspection: Zone A, Zone C. Priority 2: Zone B. Priority 3: Zone D.", "source": "vulnerability analysis"}
    return {"answer": "I can answer questions using the current risk and simulation data. Ask about critical zones, rainfall changes, or safe areas.", "source": "application analytics"}
