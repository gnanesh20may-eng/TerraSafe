# GIS Pipeline

## Objectives

The GIS layer converts spatial environmental signals into terrain risk features that can be consumed by the ML models and risk API.

## Data sources

- DEM / terrain models
- Sentinel-1, Sentinel-2, Landsat where available
- NDVI and NDWI layers
- soil and geology layers
- land-cover and slope-derived products
- rainfall and weather rasters

## Processing flow

```text
Acquire source datasets
   -> validate projection and resolution
   -> align raster grids
   -> compute terrain metrics
   -> join vector/inventory layers
   -> export feature rasters and summaries
   -> generate risk polygons and route overlays
```

## Core features

- elevation
- slope
- aspect
- plan/ profile curvature
- terrain ruggedness
- drainage indices
- topographic wetness proxies
- rain accumulation anomalies
- vegetation condition
- land cover class
- historical landslide density

## Spatial operations

- raster reprojection
- resampling and clipping
- zonal statistics per census or ward region
- nearest-neighbor and spatial joins for points and polygons
- PostGIS geometry/geography storage for location-based queries

## Safe-zone and route overlays

The GIS layer also supports:
- safe-zone markers
- hazard-zone polygons
- route risk buffering
- evacuation path planning abstractions

## Operational caution

Raster and geospatial processing must be reproducible and efficient. The system should avoid downloading massive datasets into the browser or processing large remote rasters unnecessarily in the UI layer.
