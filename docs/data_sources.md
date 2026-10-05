# Data registry and download policy

The catalog at [`data_sources/registry.yaml`](../data_sources/registry.yaml)
contains candidate sources and access/provenance metadata. A registry entry is
not evidence that the source is available, licensed for this use, or validated.
The actual latest endpoint probe results are in
[`data_health.md`](data_health.md) and served by
`GET /api/v1/health/data-sources`.

The checker probes only the public Open-Meteo historical archive and USGS
earthquake GeoJSON endpoints for Nilgiris. `WORKING` means only that an HTTP
success and JSON object were observed; it does not validate scientific quality,
coverage, units, licensing, or data recency. All other rows remain `MANUAL` or
`NEEDS_REVIEW` until an approved no-login normalizer and licence review exist.
The NASA Global Landslide Catalog is catalogued as a candidate but is not
downloaded by this phase; its direct export and reuse terms need review. GSI
Bhukosh data must be requested manually; do not automate login or bypass access
controls.

## Supported operations

From the repository root:

```powershell
python scripts\check_sources.py --region Nilgiris
python scripts\download_all.py --all --dry-run --region Nilgiris
python scripts\download_all.py --source usgs_earthquakes --region Nilgiris --dry-run
python scripts\download_all.py --source open_meteo_archive --region Nilgiris --dry-run
```

The downloader implements only Open-Meteo historical weather and USGS
earthquake queries for Nilgiris. `--all` selects those implemented sources,
not every registry entry. Live downloads default to the last seven complete
days; use `--start-date` and `--end-date` for explicit ISO dates. `--resume`
uses HTTP Range where supported. `--mock` writes a labeled local fixture and
must not be confused with downloaded observations. `--dry-run` makes no
requests or files. Downloads have a five-second request timeout, bounded
retries, a hard 200 MiB limit, and SHA-256 manifests. Raw files are stored under
ignored `ml/data/raw/` and are not committed.

Search rectangles in the downloader are approximate regional request bounds,
not official administrative boundaries. Live downloads for regions other than
Nilgiris are deliberately disabled until data availability and spatial
coverage are reviewed.

## Quality checks

`backend.app.data_sources.inspect_observations()` can report null counts,
duplicate rows, class balance, coordinate-range errors, declared CRS status,
and spatial groups assigned to multiple folds. It operates only on rows
provided by the caller; this phase does not claim that downloaded terrain,
catalogue, or satellite datasets were validated.
