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
| Open-Meteo and USGS ingestion | SCAFFOLD | Opt-in HTTP adapters exist; no live provider request was made in this audit. |
| Other NASA/IMD product ingestion | SCAFFOLD | Requires configured product-specific endpoints and normalization; no product data was downloaded. |
| Dynamic risk and forecast helpers | DEMO | P2 rainfall, slope, trigger, and horizon calculations are experimental, not calibrated warnings or trained time-series forecasts. |
| Model inference fallback | SIMULATED | Inference fits Logistic Regression on synthetic data when no trusted local artifact exists; output is not an operational prediction. |
| Checksum-verified model fetch/load | SCAFFOLD | Integrity checked against an operator-supplied digest; no trusted real model artifact is present and checksum is not publisher authentication. |
| Colab ML notebooks | SCAFFOLD | Four notebooks are marked NOT RUN; no trained LSTM/TFT or new evaluation metrics are claimed. |
| Data source health API | LIVE | `GET /api/v1/health/data-sources` returns registry status; only Open-Meteo Archive and USGS were probed live. |
| Data registry and downloader | SCAFFOLD | 47 candidate sources catalogued; live downloading is implemented only for Open-Meteo Archive and USGS in Nilgiris. No dataset was downloaded as part of this phase. |
| Data-quality report helpers | LIVE | Tested null, duplicate, label-balance, CRS declaration, coordinate range, and spatial-fold leakage reports; no external dataset was validated. |
| Other API services and routes | MISSING | `/health`, risk scoring, SOS persistence, alert lifecycle, and rescue endpoints are not present in this checkout. |
| Next.js dashboard and rescue page | MISSING | No frontend directory or npm build script is present. |
| Alert persistence, lifecycle, and delivery | MISSING | No API alert service or database implementation is present. |
| IoT firmware and sensor simulator | MISSING | No firmware or simulator source is present in tracked files. |
| Automated backend checks | LIVE | Latest full local run completed with 38 passed. This is code-test evidence, not field validation. |

## Phase tracker

| Phase | Status | Evidence / outstanding work |
| --- | --- | --- |
| P0 Audit | LIVE | Audited this checkout; backend tests pass. `npm run build` is unavailable because no build script/package manifest exists. Existing two test modules are populated (19 tests total), so no empty test files were found to fill. |
| P1 Repository and onboarding | LIVE | Added contribution guidance, PR template, CODEOWNERS, cross-platform setup, onboarding, CRLF-aware attributes, and CI. Frontend build is conditional because this checkout has no frontend package. |
| P2 Data registry and download tooling | LIVE | 47 candidate entries, 10 approximate region boxes, bounded downloader, source checks, quality helpers, and source-health endpoint added. Only two Nilgiris public endpoints are probed; GSI and access-controlled sources remain MANUAL/NEEDS_REVIEW. |
| P3 ML notebooks and inference | SIMULATED | Four NOT RUN notebook scaffolds, NumPy Logistic fallback for blocked sklearn linear DLL, hybrid inference, uncertainty placeholders, adaptive-zone demo thresholds, and model checksum tooling added. No real evaluation, trained forecast model, or trusted export is available. |
| P4 Alerts and API | MISSING | No backend API, persistence, alert lifecycle, auth, or delivery service is present. |
| P5 Dashboard | MISSING | No frontend is present. |
| P6 Offline and IoT | MISSING | No PWA, local queue, device firmware, or sensor simulator is present. |
| P7 Rescue | MISSING | No rescue service or rescue UI is present in tracked sources. |
| P8 Documentation and release gate | SCAFFOLD | P1/P2 model and dynamic-risk notes exist; requested architecture, API, offline, privacy, rescue, evaluation, pitch, demo, and final gate remain outstanding. |

## P0 audit record

- Repository: `main`, clean before this audit; latest commits are P1
  (`5d21328`) and P2 (`c8ff8d9`).
- Backend tests: `19 passed in 5.53s`.
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
