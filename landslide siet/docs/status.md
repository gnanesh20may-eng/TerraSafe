# TerraSafe Status

Audit snapshot: 2026-10-05. Status reflects implementation and local checks,
not operational readiness. “LIVE” means an external source or browser API was
observed working in this environment; it does not mean a safety service is
validated.

| Feature | Status | Evidence / test coverage |
| --- | --- | --- |
| TerraSafe frontend and FastAPI startup | LIVE | `npm run build`; API smoke checks; route table below |
| Open-Meteo rainfall and soil moisture | LIVE with DEMO fallback | Live `/health` and Coonoor risk smoke check; mocked success/failure tests in `test_weather_provider.py` |
| Terrain and satellite observations | DEMO | Provider source labels; `test_environment_service.py` asserts demo provenance |
| Location catalogue and history | DEMO | Static sample catalogue/history; no external geocoder or storage |
| Risk scoring | DEMO | Formula-based risk engine uses live weather plus demo terrain/catalogue inputs; coordinate and location routes |
| GIS risk-zone visualization | DEMO | Synthetic polygons from sample locations; `test_risk_zones.py` checks polygon closure, thresholds, and disclaimer |
| Browser current-location request | LIVE browser API / DEMO risk inputs | Permission-gated geolocation feeds coordinate risk route; `test_coordinate_risk.py` checks coordinate forwarding |
| SOS API | SIMULATED | `POST /sos` and `GET /sos`; `test_sos.py`; events are process-memory only and are not dispatched |
| Alert endpoint and transitions | DEMO | Sample alert response and local state transitions; tests in `test_alerts.py`; no delivery adapters |
| Susceptibility evaluation | DEMO | Synthetic-only metrics in `docs/evaluation.md`; the local LogisticRegression evaluation ran; tree DLL import is blocked by Windows policy |
| Trained production inference artifact | MISSING | No exported, validated model is available for production serving |
| Authentication and authorization | SCAFFOLD | Bootstrap helper exists; protected role-based routes are not implemented or tested |
| Rescue mesh and family relay visualization | SIMULATED | `/rescue` is an illustrative UI only; no Bluetooth, radio, or device relay is implemented |
| Persistent SOS/alert database and audit log | MISSING | No SQLAlchemy/Alembic persistence or hash-chained log |
| Data source registry | DEMO / NEEDS_REVIEW | `data_sources/registry.yaml` contains 44 records; only Open-Meteo and USGS are implemented as open live adapters; NASA GLC is needs-review after the current data page returned 404 |
| Source health monitor | LIVE for three open APIs; others are MANUAL/NEEDS_REVIEW | `scripts/check_sources.py` writes `docs/data_health.md`; `GET /api/v1/health/data-sources` reports latency, record count, newest timestamp, status, and errors |
| Historical Open-Meteo and USGS download | LIVE | `scripts/download_all.py` ran both Nilgiris downloads and wrote checksum sidecars under ignored `data/raw/` |
| Offline PWA, background queue, and offline maps | MISSING | No service worker or IndexedDB queue |
| SMS, WhatsApp, email, voice, push delivery | MISSING | No adapters or credentials; no external messages are sent |
| Frontend dependency security remediation | MISSING | `npm audit` reports 8 advisories (6 high, 2 critical); available automated fixes require major Next/Tailwind/MapLibre upgrades and were not applied |
| Hardware sensor firmware/simulator | MISSING | No runnable sensor client or tested firmware in this phase |

## Effective API routes

`GET /`, `GET /health`, `GET /api/v1/health`, `GET /api/v1/locations/search`,
`GET /api/v1/locations/{location_id}`, `GET /api/v1/risk`,
`GET /api/v1/risk/{location_id}`, `GET /api/v1/risk/{location_id}/history`,
`GET /api/v1/environment/{location_id}`, `GET /api/v1/terrain/{location_id}`,
`GET /api/v1/map/risk-zones`, `GET /api/v1/safe-zones`,
`GET /api/v1/rescue/nearby`, `GET /api/v1/alerts`,
`GET /api/v1/data-sources`, `GET /sos`, and `POST /sos`.

All risk information is decision support only and is not a replacement for
official IMD, NDMA, or GSI warnings.