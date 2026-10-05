from fastapi import APIRouter
from backend.app.priority_summary import get_priority_summary

router = APIRouter()

@router.get("/api/priority")
def priority():
    return get_priority_summary()
