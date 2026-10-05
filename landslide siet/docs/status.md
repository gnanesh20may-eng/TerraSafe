# TerraSafe Status Register

Last audited: 2026-10-05. This register describes the checked-out `landslide siet` workspace, not planned capabilities. Status labels: LIVE means an external source/provider was successfully used; DEMO means fixed or synthetic sample values; SIMULATED means scenario logic, not real operations; SCAFFOLD means code/documentation exists but was not executed; MISSING means no implementation was found.

| Feature | Status | Evidence / test coverage |
|---|---|---|
| Next.js app routes `/`, `/alerts`, `/evaluation`, `/rescue-hub`, `/settings` | DEMO | Static pages; `npm run build` and `npm run typecheck` pass. No `/rescue`, dashboard, data-sources, or transparency route. |
| Location catalogue and search | DEMO | Three hard-coded locations in `backend/app/api/v1/routes.py`; no geocoder or broad catalogue. |
| Map display | DEMO | MapLibre demo tile service and selected marker; no actual terrain source/3D elevation or risk overlay in the UI. Build passes; no browser E2E run. |
| Open-Meteo current weather adapter | LIVE-capable, not verified live in this run | Adapter implements current temperature/wind, hourly precipitation and optional modeled soil moisture. Default `DEMO_MODE=true`; mocked provider tests pass. No live request was made. |
| Open-Meteo historical Nilgiris rainfall/soil moisture | LIVE | Archive returned HTTP 200 with 168 hourly rows for 2026-09-23 through 2026-09-29; response 5,367 bytes. ERA5-Land modeled reanalysis, not a gauge. Integrity validation passed; raw response/checksum are not committed. |
| USGS earthquake context | LIVE (empty result) | FDSN query returned HTTP 200, valid 386-byte GeoJSON and 0 features for the approximate Nilgiris bounds, 2026-09-05 through 2026-10-05, magnitude >=2.5. This does not mean no lower-magnitude earthquakes occurred. |
| NASA Global Landslide Catalog | NEEDS_REVIEW | NASA catalog documentation describes metadata and onward archive links, not a confirmed direct export; no request/download was attempted. |
| Terrain/elevation/slope | DEMO | `DemoTerrainProvider`; no DEM acquisition or derivation. |
| Satellite/NDVI/land cover | DEMO | `DemoSatelliteProvider`; no Earth Engine/Sentinel integration. |
| Risk score | DEMO | Hand-weighted GIS signals; not a trained production predictor. Risk-zone score output is bounded 0–100. Backend tests cover classification/GeoJSON. |
| Model evaluation | SCAFFOLD/DEMO | Synthetic pilot/evaluation code only; no real inventory labels or externally validated metrics verified in this audit. |
| LogisticRegression inference fallback | DEMO | `InferenceEngine` loads a local artifact or fits LogisticRegression on generated synthetic cells. It is not connected to `/api/v1/risk`; its probability is not a real-event prediction. |
| Tree model import fallback | LIVE (probe and test) | Optional imports are guarded; LogisticRegression remains available. RandomForest import probe returned `TREE_IMPORT_OK`; no tree-model training was run. |
| Confidence/uncertainty | MISSING (calibrated) | Risk service now reports confidence unavailable; inference returns a placeholder until a calibrated conformal model is supplied. |
| Physics and rainfall hybrid | SCAFFOLD/SIMULATED | Infinite-slope and intensity-duration helpers have pure unit tests; no measured soil parameters, locally calibrated coefficients, or hybrid weights are available. Hybrid is not connected to risk API. |
| Slope memory/adaptive thresholds/model disagreement | SCAFFOLD | Pure helper modules and unit tests exist; no operational histories or zone calibration data are connected. |
| Colab notebooks and model export | SCAFFOLD (NOT RUN) | Four notebooks exist with empty execution outputs. No model training/export, ONNX, TFT, MAPIE, or SHAP run occurred. |
| Exported model artifacts | MISSING | No reviewed export is present. HTTPS/SHA-256 <=200 MiB fetch script exists; no artifact fetched. |
| Alert persistence/lifecycle | LIVE (local SQLite) | SQLAlchemy 2 tables and Alembic baseline persist alerts/events. Authority roles create/approve; allowed lifecycle is enforced; audit events are hash-chained and tamper-tested. `SENT` is explicitly MOCK ONLY. |
| SOS API | LIVE (local persistence) | `POST /sos` persists an OPEN request with optional coordinates; `GET /sos` requires responder/authority JWT. Integration tests pass. Delivery remains MOCK and no responders are notified. |
| JWT role authorization | SCAFFOLD / locally tested | Signed short-lived JWT roles gate alert create/approval and SOS queue reads; trusted operator token helper exists. No user directory/password login, refresh, revocation or external identity provider. |
| CAP 1.2 export / SMS parser | SIMULATED | CAP export has Test status; inbound SMS only parses text and returns a SIMULATED response. No official message or SMS send. |
| What-if and evacuation route | SIMULATED | What-if calls demo weighted logic. Shelter fallback picks closest demo shelter by straight-line distance; road routing/hazard avoidance not implemented. |
| Alert cooldown/escalation/geofence/adapters | MISSING | No cooldown, dedupe escalation worker, geo-fence query, or real push/SMS/WhatsApp/email/voice provider. |
| Safe zones, rescue information and contact | DEMO | Hard-coded sample facilities and placeholder contact; not verified for real emergency use. |
| Data-source health API | LIVE (generated snapshot) | `scripts/check_sources.py` wrote `data_sources/health.json` and `docs/data_health.md`: 2 WORKING, 0 FAILED, 12 MANUAL, 29 NEEDS_REVIEW. `/api/v1/health/data-sources` is covered by direct route tests; live server call not run. |
| Source registry and download tooling | LIVE / SCAFFOLD | Registry has 43 sources and ten approximate regions. Streaming, retry, SHA-256, timeout, resume, dry-run and mock modes exist; only two open adapters were queried. |
| Download data integrity checks | LIVE (local checks) | 168 weather rows passed timestamp order/uniqueness, array alignment, null/finite checks; WGS84 point validated. USGS GeoJSON parsed with 0 features. Spatial block leakage and label-balance helper tests pass. |
| Historical/forecast API | MISSING | No real rainfall history/forecast endpoint or stored observations. |
| Database/PostGIS/Alembic | PARTIAL | SQLite/PostgreSQL SQLAlchemy persistence and Alembic migration for alerts/SOS. PostgreSQL driver configured; PostGIS geometry, broader domain schema, and production database verification remain missing. |
| Authentication/RBAC | PARTIAL | JWT roles protect selected alert/SOS actions. Public alerts remain readable. No login/user store, general route policy, refresh/revocation, rate limiting, or audit identity verification. |
| Redis/scheduler/notifications | MISSING | No active scheduled refresh, queue, push/SMS/email integration. |
| Offline PWA / local SOS queue | MISSING | No service worker, IndexedDB or offline synchronization implementation. |
| IoT sensor firmware and simulator | MISSING | No `iot/` directory or sensor ingestion endpoint found. |
| Mobile mesh / missing-person workflows | MISSING | No mobile project, mesh implementation or missing-person API found. |
| Tests | LIVE (local test execution) | Phase 4 `pytest backend/tests -q`: 47 passed on 2026-10-05. SQLite integration/hash-chain tests included; no PostgreSQL/PostGIS or browser E2E suite. |
| Frontend build | LIVE (local build execution) | `npm run build`: passed; six actual routes listed above. |
| Frontend dependencies/security audit | NEEDS REVIEW | `npm install` reported 8 findings (1 moderate, 6 high, 1 critical). No forced fix was applied. |
| Contributor setup and repository templates | LIVE (syntax-checked) | PowerShell and Bash setup scripts parse; README, onboarding, PR template, CODEOWNERS placeholder, issue-label guide, and CI lockfile/typecheck steps are present. Setup installs were not run by the syntax check. |
| API/data fallback labels | DEMO | Static screens/data include demo content; consistent provenance labelling is incomplete. |

## Verified API Routes

Backend routes found in source include `POST /sos`, protected `GET /sos`, persistent `GET/POST /api/v1/alerts`, `POST /api/v1/alerts/{id}/lifecycle`, `GET /api/v1/alerts/{id}/cap`, `POST /api/v1/simulate`, `GET /api/v1/rescue/route`, `POST /api/v1/sms/inbound`, and `GET /api/v1/models/metrics`, alongside the previously listed locations/risk/environment routes. API integration tests use TestClient; a separately started server has not been checked yet.

## Safety Note

TerraSafe is a prototype decision-support project. It is not a replacement for official IMD, NDMA, GSI, or local authority warnings and emergency instructions. DEMO facilities and scores must never guide real evacuation decisions.
