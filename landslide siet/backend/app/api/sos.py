from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, status
from pydantic import BaseModel, Field

router = APIRouter(prefix="/sos", tags=["sos"])


class SOSEventRequest(BaseModel):
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)
    name: str = Field(min_length=1, max_length=120)
    timestamp: datetime


_sos_events: list[dict] = []


@router.post("", status_code=status.HTTP_201_CREATED)
def create_sos(payload: SOSEventRequest):
    event = {"id": str(uuid4()), **payload.model_dump(mode="json")}
    _sos_events.append(event)
    return event


@router.get("")
def list_sos():
    return {"items": list(_sos_events)}