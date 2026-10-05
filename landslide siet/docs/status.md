# TerraSafe Status Register

Last audited: 2026-10-05. This register describes the checked-out `landslide siet` workspace, not planned capabilities. Status labels: LIVE means an external source/provider was successfully used; DEMO means fixed or synthetic sample values; SIMULATED means scenario logic, not real operations; SCAFFOLD means code/documentation exists but was not executed; MISSING means no implementation was found.

| Feature | Status | Evidence / test coverage |
|---|---|---|
| Next.js app routes `/`, `/alerts`, `/evaluation`, `/rescue-hub`, `/settings` | DEMO | Static pages; `npm run build` and `npm run typecheck` pass. No `/rescue`, dashboard, data-sources, or transparency route. |
| Location catalogue and search | DEMO | Three hard-coded locations in `backend/app/api/v1/routes.py`; no geocoder or broad catalogue. |
| Map display | DEMO | MapLibre demo tile service and selected marker; no actual terrain source/3D elevation or risk overlay in the UI. Build passes; no browser E2E run. |
| Open-Meteo current weather adapter | LIVE-capable, not verified live in this run | Adapter implements current temperature/wind, hourly precipitation and optional modeled soil moisture. Default `DEMO_MODE=true`; mocked provider tests pass. No live request was made. |
| Terrain/elevation/slope | DEMO | `DemoTerrainProvider`; no DEM acquisition or derivation. |
| Satellite/NDVI/land cover | DEMO | `DemoSatelliteProvider`; no Earth Engine/Sentinel integration. |
| Risk score | DEMO | Hand-weighted GIS signals; not a trained production predictor. Risk-zone score output is bounded 0–100. Backend tests cover classification/GeoJSON. |
| Model evaluation | SCAFFOLD/DEMO | Synthetic pilot/evaluation code only; no real inventory labels or externally validated metrics verified in this audit. |
| Confidence/uncertainty | MISSING (calibrated) | Existing risk service returns a fixed confidence value; must not be interpreted as calibrated uncertainty. |
| Alerts and transitions | SIMULATED | In-process alert engine and response payload; no persistence, authorization, delivery, cooldown or audit chain. Existing alert tests pass. |
| Safe zones, rescue information and contact | DEMO | Hard-coded sample facilities and placeholder contact; not verified for real emergency use. |
| SOS API and delivery | MISSING | No `/sos` route found in `backend/main.py` or API router. |
| Data-source health API | MISSING | `/api/v1/data-sources` returns demo labels; no latency/check/record health endpoint. |
| Historical/forecast API | MISSING | No real rainfall history/forecast endpoint or stored observations. |
| Database/PostGIS/Alembic | MISSING | No ORM, migration or database persistence layer found. |
| Authentication/RBAC | MISSING | No verified auth dependency or role checks on API routes. |
| Redis/scheduler/notifications | MISSING | No active scheduled refresh, queue, push/SMS/email integration. |
| Offline PWA / local SOS queue | MISSING | No service worker, IndexedDB or offline synchronization implementation. |
| IoT sensor firmware and simulator | MISSING | No `iot/` directory or sensor ingestion endpoint found. |
| Mobile mesh / missing-person workflows | MISSING | No mobile project, mesh implementation or missing-person API found. |
| Tests | LIVE (local test execution) | `pytest backend/tests -q`: 17 passed on 2026-10-05. Coverage is focused unit tests; no API integration/database/E2E tests. |
| Frontend build | LIVE (local build execution) | `npm run build`: passed; six actual routes listed above. |
| Frontend dependencies/security audit | NEEDS REVIEW | `npm install` reported 8 findings (1 moderate, 6 high, 1 critical). No forced fix was applied. |
| Contributor setup and repository templates | LIVE (syntax-checked) | PowerShell and Bash setup scripts parse; README, onboarding, PR template, CODEOWNERS placeholder, issue-label guide, and CI lockfile/typecheck steps are present. Setup installs were not run by the syntax check. |
| API/data fallback labels | DEMO | Static screens/data include demo content; consistent provenance labelling is incomplete. |

## Verified API Routes

Backend routes found in source: `GET /`, `GET /health`, `GET /api/v1/health`, `GET /api/v1/locations/search`, `GET /api/v1/locations/{location_id}`, `GET /api/v1/risk/{location_id}`, `GET /api/v1/risk/{location_id}/history`, `GET /api/v1/environment/{location_id}`, `GET /api/v1/terrain/{location_id}`, `GET /api/v1/map/risk-zones`, `GET /api/v1/safe-zones`, `GET /api/v1/rescue/nearby`, `GET /api/v1/alerts`, and `GET /api/v1/data-sources`. These are source-defined routes; no live server calls were made in this audit.

## Safety Note

TerraSafe is a prototype decision-support project. It is not a replacement for official IMD, NDMA, GSI, or local authority warnings and emergency instructions. DEMO facilities and scores must never guide real evacuation decisions.
