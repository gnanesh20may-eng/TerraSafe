from fastapi import APIRouter
from backend.app.priority_summary import get_priority_summary

router = APIRouter()

@router.get("/api/vulnerable-locations")
def vulnerable_locations():
    return get_priority_summary()
