# TerraSafe implementation status

TerraSafe is an experimental landslide decision-support and rescue-platform
prototype. It is **not a replacement for official IMD, NDMA, or GSI warnings**.
Statuses below describe this checkout and verified work only; they do not imply
that a live provider, device, or public-safety workflow has been validated.

## Feature inventory

| Feature | Status | Verified state / limitations |
| --- | --- | --- |
| Susceptibility training pipeline | SIMULATED | P1 deterministic synthetic Nilgiris data and spatial cross-validation; metrics are not real-world performance. |
| Ingestion fixtures | SIMULATED | P2 provider adapters supply clearly marked local mock fixtures. |
| Open-Meteo and USGS ingestion | LIVE | Open-Meteo forecast weather fetch returned precipitation and soil-moisture observations during P5b verification; USGS endpoint probes previously returned HTTP 200. No dataset was downloaded. |
| Other NASA/IMD product ingestion | SCAFFOLD | Requires configured product-specific endpoints and normalization; no product data was downloaded. |
| Dynamic risk and forecast helpers | DEMO | P2 rainfall, slope, trigger, and horizon calculations are experimental, not calibrated warnings or trained time-series forecasts. |
| Model inference fallback | SIMULATED | Inference fits Logistic Regression on synthetic data when no trusted local artifact exists; output is not an operational prediction. |
| Checksum-verified model fetch/load | SCAFFOLD | Integrity checked against an operator-supplied digest; no trusted real model artifact is present and checksum is not publisher authentication. |
| Colab ML notebooks | SCAFFOLD | Four notebooks are marked NOT RUN; no trained LSTM/TFT or new evaluation metrics are claimed. |
| Data source health API | LIVE | `GET /api/v1/health/data-sources` returns registry status; only Open-Meteo Archive and USGS were probed live. |
| Data registry and downloader | SCAFFOLD | 47 candidate sources catalogued; live downloading is implemented only for Open-Meteo Archive and USGS in Nilgiris. No dataset was downloaded as part of this phase. |
| Data-quality report helpers | LIVE | Tested null, duplicate, label-balance, CRS declaration, coordinate range, and spatial-fold leakage reports; no external dataset was validated. |
| FastAPI service and health | LIVE | `/health` checks the configured database; data-source health is exposed at `/api/v1/health/data-sources`. Local API tests pass; this is not a hosted service. |
| Risk query | DEMO | `GET /api/v1/risk` uses live Open-Meteo rainfall/soil-moisture data when available, but risk zones and scores are generated from synthetic pilot geometry and are not calibrated warnings. Weather-provider failures use an explicit DEMO fallback. |
| Alert persistence and lifecycle | DEMO | SQLAlchemy persistence, role-checked lifecycle, deduplication, hysteresis, request-triggered escalation, and hash-chain audit are implemented and tested. Data and policy are not operationally validated. |
| JWT role authorization | LIVE | Short-lived HS256 tokens use `JWT_SECRET` from the environment; protected writes and SOS reads are tested. No production identity provider is configured. |
| Notification channels | DEMO | Web push, SMS, WhatsApp, email, and voice return mock results only; no provider adapter sends messages. |
| CAP export | DEMO | XML output is marked `Test`, uses unknown severity/urgency/certainty, and labels its generated 1 km circle SIMULATED. Do not redistribute as an official alert. |
| SOS intake | DEMO | `/sos` stores a request and omits phone from its create response; it does not dispatch emergency services. Listing is role-protected. |
| SMS inbound RISK query | DEMO | `/sms/inbound` performs a local alert lookup only; it does not connect to an SMS provider. |
| Evacuation destination and routing | MISSING | No verified shelter dataset or validated route service is configured; no locations or directions are fabricated. |
| Map shelter layer | SIMULATED | Map contains explicit placeholder shelters; they are not real evacuation destinations. |
| Scenario simulation | SIMULATED | `/api/v1/simulate` returns a transparent, uncalibrated what-if index. |
| Model metrics API | MISSING | No generated evaluation file exists in this checkout. |
| Rescue endpoint | SCAFFOLD | `/rescue` is a placeholder and is not a dispatch or rescue coordination service. |
| Next.js dashboard | DEMO | App Router dashboard at `http://localhost:3001` shows live API/database status when reachable, actual alert records, Leaflet map, generated zone overlays, layer toggles, zone explanations, seven-day rainfall trend, and alert lifecycle controls. Risk overlays are DEMO; shelters are SIMULATED. |
| Next.js rescue page | MISSING | No separate rescue page or dispatch workflow exists; the dashboard marks RESCUE coordination SCAFFOLD. |
| IoT firmware and sensor simulator | MISSING | No firmware or simulator source is present in tracked files. |
| Automated backend checks | LIVE | Latest full local run completed with 49 passed. This is code-test evidence, not field validation. |

## Phase tracker

| Phase | Status | Evidence / outstanding work |
| --- | --- | --- |
| P0 Audit | LIVE | Audited this checkout; backend tests pass. `npm run build` is unavailable because no build script/package manifest exists. Existing two test modules are populated (19 tests total), so no empty test files were found to fill. |
| P1 Repository and onboarding | LIVE | Added contribution guidance, PR template, CODEOWNERS, cross-platform setup, onboarding, CRLF-aware attributes, and CI. Frontend build is conditional because this checkout has no frontend package. |
| P2 Data registry and download tooling | LIVE | 47 candidate entries, 10 approximate region boxes, bounded downloader, source checks, quality helpers, and source-health endpoint added. Only two Nilgiris public endpoints are probed; GSI and access-controlled sources remain MANUAL/NEEDS_REVIEW. |
| P3 ML notebooks and inference | SIMULATED | Four NOT RUN notebook scaffolds, NumPy Logistic fallback for blocked sklearn linear DLL, hybrid inference, uncertainty placeholders, adaptive-zone demo thresholds, and model checksum tooling added. No real evaluation, trained forecast model, or trusted export is available. |
| P4 Alerts and API | DEMO | FastAPI routes, SQLite/PostgreSQL persistence models, Alembic migration, JWT roles, lifecycle, dedupe/hysteresis, request-triggered escalation, mock channel adapters, CAP export, SOS intake, SMS query, simulation, and audit verification are implemented. 45 backend tests pass. No notification sends, real warning, shelter data, or dispatch is claimed. |
| P5 Dashboard | DEMO | Next.js dashboard added with honest status cards, API health/alert reads, explicit backend errors, responsive layout, and no fabricated incidents. `npm run build` and `npm run typecheck` pass; a separate rescue page, field workflows, and map are not implemented. |
| P5b Map dashboard | DEMO | Leaflet dashboard, Open-Meteo live weather with five-second DEMO fallback, synthetic risk zones, SIMULATED shelter placeholders, bilingual interface strings, alert lifecycle controls, and seven-day observed rainfall chart implemented. Full backend tests (49), frontend typecheck, and production build pass. |
| P5c Decision support | SIMULATED | Existing what-if scenario endpoint retained; nearest-shelter straight-line estimate and UI are not implemented. |
| P6 Offline and IoT | MISSING | No PWA, local queue, device firmware, or sensor simulator is present. |
| P7 Rescue | MISSING | No rescue service or rescue UI is present in tracked sources. |
| P8 Documentation and release gate | SCAFFOLD | P1/P2 model and dynamic-risk notes exist; requested architecture, API, offline, privacy, rescue, evaluation, pitch, demo, and final gate remain outstanding. |

## P0 audit record

- Repository: `main`, clean before this audit; latest commits are P1
  (`5d21328`) and P2 (`c8ff8d9`).
- Backend tests: `19 passed in 5.53s` at the P0 audit.
- Frontend build: attempted with `npm run build`; npm returned
  `Missing script: "build"`.
- Route inventory: no FastAPI application or route decorators found.
- Test inventory: `backend/tests/test_susceptibility.py` and
  `backend/tests/test_dynamic_risk.py` are non-empty and already contain
  behavior tests.
- Warning check: the test run emitted no Starlette/httpx warning. Starlette is
  installed in the selected virtual environment; httpx is not installed.
  There is no HTTP application in this checkout to exercise. No dependency
  change was made based only on a warning mentioned in the supplied state.
