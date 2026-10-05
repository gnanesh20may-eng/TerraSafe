from fastapi import APIRouter

router = APIRouter()

@router.get("/api/alerts")
def get_alerts():
    return {
        "alerts": [],
        "disclaimer": "AI-generated decision-support alert. This prototype does not replace official disaster-management warnings.",
        "status": "ok",
    }

@router.get("/api/alert-history")
def get_alert_history():
    return {
        "alerts": [
            {
                "timestamp": "2026-10-05T06:00:00Z",
                "zone": "Ooty",
                "risk_score": 72,
                "level": "HIGH",
                "trigger": "Heavy rainfall + soil moisture",
                "status": "reviewed",
                "action": "Monitor and inspect vulnerable locations",
            }
        ]
    }
