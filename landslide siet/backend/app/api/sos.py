from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status

from backend.app.api.schemas import SosCreate
from backend.app.core.auth import require_roles
from backend.app.services.persistence_service import PersistenceService

router = APIRouter(tags=["sos"])
persistence = PersistenceService()


@router.post("/sos", status_code=status.HTTP_201_CREATED)
def create_sos(payload: SosCreate):
    if (payload.latitude is None) != (payload.longitude is None):
        raise HTTPException(status_code=422, detail="latitude and longitude must be supplied together")
    return persistence.create_sos(payload.message, payload.latitude, payload.longitude)


@router.get("/sos")
def list_sos(
    limit: int = Query(default=50, ge=1, le=200),
    _principal: dict = Depends(require_roles("admin", "district_officer", "field_responder")),
):
    return {"items": persistence.list_sos(limit)}
