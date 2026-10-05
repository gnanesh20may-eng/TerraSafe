"""Generate clearly labelled, deterministic synthetic Nilgiris pilot data."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


FEATURE_COLUMNS = (
    "elevation_m",
    "slope_deg",
    "aspect_sin",
    "aspect_cos",
    "curvature",
    "twi",
    "ndvi",
    "soil_clay_fraction",
    "land_cover_code",
    "road_distance_km",
    "stream_distance_km",
)

LAND_COVER_CODES = {
    "forest": 0,
    "plantation": 1,
    "cropland": 2,
    "built_up": 3,
    "bare_earth": 4,
}


@dataclass(frozen=True)
class SyntheticPilot:
    """Synthetic terrain cells and their synthetic landslide inventory labels."""

    cells: pd.DataFrame
    region: str
    source_label: str = "SYNTHETIC — not an observed inventory or warning"
    bounds: tuple[float, float, float, float] = (76.2, 11.1, 76.9, 11.6)


def generate_nilgiris_pilot(
    grid_size: int = 40,
    seed: int = 42,
    region: str = "Nilgiris, Tamil Nadu",
    bounds: tuple[float, float, float, float] = (76.2, 11.1, 76.9, 11.6),
) -> SyntheticPilot:
    """Create a small synthetic raster-derived feature grid for local demos.

    Terrain and proxy layers are invented for software testing. In particular,
    TWI uses a synthetic contributing-area proxy, not a hydrologic DEM analysis.
    """
    if grid_size < 10:
        raise ValueError("grid_size must be at least 10 to support spatial folds")
    west, south, east, north = bounds
    if not (-180 <= west < east <= 180 and -90 <= south < north <= 90):
        raise ValueError("bounds must be valid (west, south, east, north) coordinates")

    rng = np.random.default_rng(seed)
    rows, cols = np.mgrid[0:grid_size, 0:grid_size]
    x = cols / (grid_size - 1)
    y = rows / (grid_size - 1)
    elevation = (
        1600
        + 850 * np.exp(-((x - 0.30) ** 2 + (y - 0.70) ** 2) / 0.075)
        + 620 * np.exp(-((x - 0.76) ** 2 + (y - 0.28) ** 2) / 0.045)
        + 180 * np.sin(2 * np.pi * x) * np.cos(np.pi * y)
        + 75 * x
    )
    cell_size_m = 1000 / (grid_size - 1)
    dz_dy, dz_dx = np.gradient(elevation, cell_size_m)
    slope_rad = np.arctan(np.hypot(dz_dx, dz_dy))
    slope_deg = np.degrees(slope_rad)
    aspect = np.arctan2(-dz_dy, dz_dx)
    curvature = np.gradient(dz_dx, cell_size_m, axis=1) + np.gradient(
        dz_dy, cell_size_m, axis=0
    )
    elevation_norm = (elevation - elevation.min()) / np.ptp(elevation)
    contributing_area_proxy = 1 + 600 * (1 - elevation_norm) ** 2
    twi = np.log(
        (contributing_area_proxy + 1e-6)
        / (np.tan(slope_rad) + 0.01)
    )
    ndvi = np.clip(
        0.78
        - 0.38 * np.exp(-((x - 0.54) ** 2 + (y - 0.52) ** 2) / 0.08)
        + rng.normal(0, 0.045, size=(grid_size, grid_size)),
        -0.1,
        0.95,
    )
    soil_clay = np.clip(
        0.22 + 0.42 * (1 - elevation_norm) + rng.normal(0, 0.06, elevation.shape),
        0.05,
        0.8,
    )

    land_cover = np.select(
        [
            ndvi > 0.72,
            (ndvi > 0.52) & (x < 0.62),
            (ndvi > 0.35) & (x >= 0.62),
            (ndvi <= 0.35) & (x > 0.62),
        ],
        [
            LAND_COVER_CODES["forest"],
            LAND_COVER_CODES["plantation"],
            LAND_COVER_CODES["cropland"],
            LAND_COVER_CODES["built_up"],
        ],
        default=LAND_COVER_CODES["bare_earth"],
    )
    road_distance = np.clip(
        np.minimum(np.abs(y - 0.24), np.abs(y - 0.78)) * 12
        + 0.15
        + rng.uniform(0, 0.25, elevation.shape),
        0.05,
        8,
    )
    stream_distance = np.clip(
        np.abs(x - (0.30 + 0.14 * np.sin(2 * np.pi * y))) * 10
        + 0.1
        + rng.uniform(0, 0.2, elevation.shape),
        0.05,
        8,
    )
    risk_logit = (
        -2.0
        + 0.055 * (slope_deg - 20)
        + 0.30 * (twi - 3)
        + 1.2 * (0.55 - ndvi)
        + 1.1 * (soil_clay - 0.4)
        + 0.55 * np.isin(land_cover, [3, 4])
        + 0.45 * np.exp(-stream_distance / 1.5)
        + rng.normal(0, 0.48, elevation.shape)
    )
    probability = 1 / (1 + np.exp(-risk_logit))
    labels = rng.binomial(1, probability)
    if labels.min() == labels.max():
        # Keep small/demo grids trainable while retaining deterministic labels.
        labels.flat[np.argsort(probability.ravel())[-max(1, grid_size // 3) :]] = 1
        labels.flat[np.argsort(probability.ravel())[: max(1, grid_size // 3)]] = 0

    longitude = west + x * (east - west)
    latitude = north - y * (north - south)
    block_size = max(2, grid_size // 8)
    frame = pd.DataFrame(
        {
            "longitude": longitude.ravel(),
            "latitude": latitude.ravel(),
            "row": rows.ravel(),
            "col": cols.ravel(),
            "spatial_block": (
                (rows // block_size) * (int(np.ceil(grid_size / block_size)))
                + (cols // block_size)
            ).ravel(),
            "elevation_m": elevation.ravel(),
            "slope_deg": slope_deg.ravel(),
            "aspect_sin": np.sin(aspect).ravel(),
            "aspect_cos": np.cos(aspect).ravel(),
            "curvature": curvature.ravel(),
            "twi": twi.ravel(),
            "ndvi": ndvi.ravel(),
            "soil_clay_fraction": soil_clay.ravel(),
            "land_cover_code": land_cover.ravel(),
            "road_distance_km": road_distance.ravel(),
            "stream_distance_km": stream_distance.ravel(),
            "landslide_label": labels.ravel(),
            "synthetic_inventory": True,
        }
    )
    return SyntheticPilot(cells=frame, region=region, bounds=bounds)
