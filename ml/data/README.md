# Pilot data

No real Nilgiris DEM, landslide inventory, soil, land-cover, NDVI, or OSM
extract was present in this workspace at project start. The P1 pipeline creates
a deterministic **synthetic demonstration dataset** when run; it does not
download or imply access to NASA Global Landslide Catalog or GSI Bhukosh data.

Generated training metrics and GeoJSON are written under
`ml/data/generated/`, which is excluded from Git. Replace the synthetic
generator with provenance-tracked, licensed regional inputs before any
operational or scientific use. The synthetic TWI feature is based on a proxy,
not on a real flow-accumulation calculation.
