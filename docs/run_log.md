# TerraSafe phase run log

## P0 — repository audit

- Timestamp (`Get-Date`): 2026-10-05T19:40:30+05:30
- Result: audited the checked-out `main` branch at P2; working tree was clean
  before P0 documentation.
- Backend test command: `.venv\Scripts\python.exe -m pytest backend/tests -q`
- Backend test result: **19 passed in 5.53s**.
- Frontend build command: `npm run build`
- Frontend build result: **not available** — npm reported `Missing script:
  "build"`; this checkout has no frontend package manifest.
- API route inventory: no FastAPI application or route declarations found.
- Test-file audit: the two tracked test files are populated; no empty test files
  were present. Existing tests were retained.
- Warning audit: no Starlette/httpx warning appeared in the test output.
  Starlette is installed; httpx is not. No speculative dependency change made.
- Scope note: the supplied project-state description does not match this
  checkout. `docs/status.md` records observed gaps as MISSING rather than
  treating them as completed.

## P1 — repository and onboarding

- Timestamp (`Get-Date`): 2026-10-05T19:54:06+05:30
- Result: added contributor/PR/ownership guidance, cross-platform setup
  scripts, onboarding including Windows native tree-model limitations and a
  Colab safety workaround, CRLF-aware Git attributes, and CI.
- CI backend command: install `requirements.txt`, then
  `python -m pytest backend/tests -q`.
- CI frontend build: conditional on `frontend/package.json`; no frontend
  exists in this checkout, so no frontend build is claimed.
- Safety labels and official-warning disclaimer are included in onboarding
  and PR checklist.

## P2 — data registry and ingestion

- Timestamp (`Get-Date`): 2026-10-05T20:09:50+05:30
- Added a 47-entry candidate-source registry and 10 approximate search boxes.
- Added a bounded downloader with dry-run, resume, mock mode, retries,
  checksums, and a 200 MiB limit. Live downloaders are limited to Open-Meteo
  historical weather and USGS earthquakes for Nilgiris; no dataset was
  downloaded in this phase.
- Ran `scripts/check_sources.py --region Nilgiris` against the two supported
  open endpoints. Observed: `WORKING open_meteo_archive: HTTP 200; JSON object
  response received.` and `WORKING usgs_earthquakes: HTTP 200; JSON object
  response received.` Other sources are documented as MANUAL or
  NEEDS_REVIEW; see `docs/data_health.md`.
- Added and tested `/api/v1/health/data-sources` and observation-quality
  helpers for CRS status, coordinate ranges, nulls, duplicates, label balance,
  and spatial group/fold leakage.
- Backend tests: **28 passed in 4.69s**. Downloader dry-run listed only the
  two supported Nilgiris sources.
- NASA Global Landslide Catalog direct-export availability and reuse terms
  remain NEEDS_REVIEW; no login, captcha, or authentication was attempted.
- Completion timestamp (`Get-Date`): 2026-10-05T20:21:53+05:30.
- Final P2 backend gate: **28 passed in 4.97s**; Python compileall and Git
  whitespace checks passed.

## P3 — ML inference and notebook scaffolds

- Timestamp (`Get-Date`): 2026-10-05T20:23:36+05:30.
- Added `infer_risk()` with synthetic Logistic Regression fallback, hash-checked
  local joblib loading, rainfall intensity-duration scoring, infinite-slope
  scenario physics, 7d/30d antecedent rainfall memory, optional empirical
  per-zone thresholds, optional model-disagreement checks, top factors, and
  explicit SCAFFOLD uncertainty when adequate calibration is unavailable.
- The observed Windows environment blocks `sklearn.linear_model` import through
  Application Control (`_sgd_fast` DLL). Added a NumPy Logistic Regression
  fallback; tree-model imports remain optional and are isolated in a try/except.
- Training smoke command completed on a temporary synthetic 10x10 grid:
  `best_model=LogisticRegression; folds=5`. Output was SIMULATED and temporary
  generated files were removed.
- Added four valid nbformat 4 notebooks, each marked **SCAFFOLD — NOT RUN**.
  Python cell syntax and null execution counts were verified; no notebook was
  executed. LSTM/TFT and leakage-safe stacking remain plans/TODOs.
- Added an HTTPS-only, 200 MiB bounded `.joblib` fetcher requiring an
  operator-supplied SHA-256. Hash matching is integrity checking, not publisher
  authentication. No external model was fetched.
- Final full backend suite: **38 passed in 7.45s**. Notebook JSON/cell syntax,
  Python compileall, and CRLF-aware whitespace checks passed.
- Completion timestamp (`Get-Date`): 2026-10-05T20:38:07+05:30.

## P4 — alerts API and RESCUE service scaffolds

- Timestamp (`Get-Date`): 2026-10-05T20:47:37.6910807+05:30.
- Added SQLAlchemy alert/audit/SOS persistence, Alembic migration, environment
  based JWT role auth, strict alert lifecycle, de-duplication, score
  hysteresis, request-triggered stale-alert escalation, WGS84 geofence
  validation, hash-chain verification, CAP 1.2 `Test` output, and mock-only
  web-push/SMS/WhatsApp/email/voice adapters.
- Added `/sos`, protected SOS listing, mock `/sms/inbound` RISK query,
  deterministic `/api/v1/simulate`, MISSING shelter/route output, model
  metrics status, and `/rescue` SCAFFOLD. No phone is returned by SOS create;
  no message is sent, no shelter or route is invented, and no emergency
  dispatch is performed.
- Added `docs/api.md`; updated README and feature inventory with observed
  P4 labels and limitations.
- Backend command: `.venv\Scripts\python.exe -m pytest backend/tests -q`
- Backend result: **45 passed in 9.48s**.
- Migration check: `alembic upgrade head` succeeded against the temporary
  SQLite URL `sqlite:///./p4_migration_validation.db`; the temporary database
  was removed after successful validation.
- Frontend gate: `npm run build` was attempted and **did not run** because npm
  reported `Missing script: "build"`; the repository still has no frontend
  `package.json`. The P5 dashboard/build gate remains MISSING; no placeholder
  build script was added.
- Whitespace check: `git -c core.whitespace=cr-at-eol diff --check` passed.
- Completion timestamp (`Get-Date`): 2026-10-05T20:50:57.6286001+05:30.
