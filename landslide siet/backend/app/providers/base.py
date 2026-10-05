from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class LocationRef:
    id: str
    name: str
    latitude: float
    longitude: float
    admin_region: str = ""


@dataclass
class WeatherConditions:
    rainfall_24h_mm: float
    rainfall_7d_mm: float
    soil_moisture_pct: float
    wind_speed_kmh: float
    temperature_c: float
    source: str = "demo"


@dataclass
class TerrainFeatures:
    elevation_m: float
    slope_deg: float
    curvature: float
    ndvi: float
    land_cover: str
    source: str = "demo"


@dataclass
class SatelliteObservation:
    cloud_cover_pct: float
    ndvi: float
    ndwi: float
    land_cover: str
    source: str = "demo"


class WeatherProvider(ABC):
    @abstractmethod
    def get_current_weather(self, location: LocationRef) -> WeatherConditions:
        raise NotImplementedError


class TerrainProvider(ABC):
    @abstractmethod
    def get_terrain_features(self, location: LocationRef) -> TerrainFeatures:
        raise NotImplementedError


class SatelliteProvider(ABC):
    @abstractmethod
    def get_satellite_observation(self, location: LocationRef) -> SatelliteObservation:
        raise NotImplementedError


class BaseDemoProvider:
    source_name: str = "DEMO DATA"
