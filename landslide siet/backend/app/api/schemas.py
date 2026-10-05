from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class SosCreate(BaseModel):
    message: str = Field(default="Emergency assistance requested", min_length=1, max_length=500)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)

    @field_validator("longitude")
    @classmethod
    def longitude_requires_latitude(cls, value, info):
        if value is not None and info.data.get("latitude") is None:
            raise ValueError("latitude is required when longitude is supplied")
        return value


class AlertCreate(BaseModel):
    location_id: str = Field(min_length=1, max_length=100)
    risk_level: str
    message: str = Field(min_length=1, max_length=1000)

    @field_validator("risk_level")
    @classmethod
    def valid_risk_level(cls, value: str) -> str:
        normalized = value.upper()
        if normalized not in {"LOW", "WATCH", "HIGH", "CRITICAL"}:
            raise ValueError("risk_level must be LOW, WATCH, HIGH, or CRITICAL")
        return normalized


class AlertTransition(BaseModel):
    state: str
    detail: str = Field(default="", max_length=500)


class SimulationRequest(BaseModel):
    location_id: str
    rainfall_24h_mm: float | None = Field(default=None, ge=0, le=2000)
    rainfall_7d_mm: float | None = Field(default=None, ge=0, le=10000)
    soil_moisture_pct: float | None = Field(default=None, ge=0, le=100)
    slope_deg: float | None = Field(default=None, ge=0, le=90)
    road_cut: bool = False
    earthquake_magnitude: float | None = Field(default=None, ge=0, le=10)
