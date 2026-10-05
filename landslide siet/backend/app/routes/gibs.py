from fastapi import APIRouter, Query
from backend.app.services.gibs_service import get_gibs_layer

router = APIRouter()

@router.get("/api/gibs")
def get_gibs(lat: float = Query(...), lon: float = Query(...), layer: str = "MODIS_Terra_Land_Surface_Temp"):
    return get_gibs_layer(lat, lon, layer=layer)
