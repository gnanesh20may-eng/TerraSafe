"""Validated request bodies for demo alerts and SOS records."""

from __future__ import annotations

from pydantic import BaseModel, Field, model_validator


class AlertCreate(BaseModel):
    zone_id: str = Field(min_length=1, max_length=160)
    location: str = Field(min_length=1, max_length=240)
    pincode: str | None = Field(default=None, max_length=16)
    risk_score: float = Field(ge=0, le=1)
    message: str | None = Field(default=None, max_length=2000)
    language: str = Field(default="en", pattern="^(en|ta|hi|ml)$")
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    geofence_bounds: tuple[float, float, float, float] | None = None

    @model_validator(mode="after")
    def validate_geofence_coordinates(self):
        if (self.latitude is None) != (self.longitude is None):
            raise ValueError("latitude and longitude must be supplied together")
        if self.geofence_bounds and self.latitude is None:
            raise ValueError("coordinates are required when geofence_bounds are supplied")
        if self.geofence_bounds:
            west, south, east, north = self.geofence_bounds
            if not (-180 <= west < east <= 180 and -90 <= south < north <= 90):
                raise ValueError("geofence_bounds must be valid WGS84 coordinates")
        return self


class AlertUpdate(BaseModel):
    message: str | None = Field(default=None, max_length=2000)
    pincode: str | None = Field(default=None, max_length=16)
    language: str | None = Field(default=None, pattern="^(en|ta|hi|ml)$")


class AlertTransition(BaseModel):
    event: str = Field(pattern="^(Approved|Sent|Delivered|Acknowledged|Resolved)$")


class ScenarioInput(BaseModel):
    baseline_score: float = Field(ge=0, le=1)
    rainfall_mm: float = Field(default=0, ge=0, le=1000)
    duration_hours: float = Field(default=24, gt=0, le=720)
    earthquake_magnitude: float | None = Field(default=None, ge=0, le=10)
    road_cut: bool = False


class SmsInbound(BaseModel):
    message_text: str = Field(min_length=1, max_length=240)
    sender: str | None = Field(default=None, max_length=40)


class SosCreate(BaseModel):
    phone: str = Field(min_length=3, max_length=40)
    pincode: str | None = Field(default=None, max_length=16)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    message: str = Field(default="", max_length=1000)

    @model_validator(mode="after")
    def validate_location_pair(self):
        if (self.latitude is None) != (self.longitude is None):
            raise ValueError("latitude and longitude must be supplied together")
        return self
