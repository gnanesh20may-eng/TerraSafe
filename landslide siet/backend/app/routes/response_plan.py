from fastapi import APIRouter
from backend.app.priority_summary import get_priority_summary

router = APIRouter()

@router.get("/api/response-plan")
def response_plan():
    return {
        "recommendations": [
            "Avoid Zone A road", 
            "Inspect Zone B for cut slopes",
            "Monitor Zone C with evacuation prep",
            "Maintain routine monitoring in Zone D",
        ],
        "priority_summary": get_priority_summary(),
    }
