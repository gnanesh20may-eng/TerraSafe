from __future__ import annotations

from backend.app.providers.base import LocationRef, TerrainFeatures, TerrainProvider


class DemoTerrainProvider(TerrainProvider):
    def get_terrain_features(self, location: LocationRef) -> TerrainFeatures:
        terrain_map = {
            "coonor": (520.0, 27.0, 0.92, 0.64, "steep-vegetated-slope"),
            "ooty": (2330.0, 18.0, 0.62, 0.58, "montane-forest"),
            "kodaikanal": (2090.0, 12.0, 0.35, 0.72, "temperate-forest"),
        }
        elevation, slope, curvature, ndvi, cover = terrain_map.get(
            location.id,
            (800.0, 15.0, 0.5, 0.6, "mixed-cover"),
        )
        return TerrainFeatures(
            elevation_m=elevation,
            slope_deg=slope,
            curvature=curvature,
            ndvi=ndvi,
            land_cover=cover,
            source="DEMO TERRAIN PROVIDER",
        )
