# Run Log

## Phase 0: Audit and baseline

- Start: 2026-10-05 18:50:19 +05:30
- End: 2026-10-05 19:07:10 +05:30
- Result: 17 pytest tests passed; `npm run build` passed; OpenAPI listed 17 effective routes.
- The phase exceeded its 10-minute allocation by more than 25%. The audit, requested test coverage, deprecation cleanup, status inventory, and dashboard disclaimer are complete. Remaining architecture beyond Phase 0 stays explicitly MISSING or SCAFFOLD in `status.md`.

## Phase 1: Team and repo hygiene

- Start: 2026-10-05 19:09:31 +05:30
- End: 2026-10-05 19:20:17 +05:30
- Result: Windows setup script ran; `.env` and frontend Next executable exist; `npm ci` succeeded (134 packages). `17` pytest tests and `npm run build` passed.
- CI YAML and PowerShell syntax checks passed. POSIX shell syntax was not checked because `sh` is unavailable. `npm audit` reported 8 advisories (6 high, 2 critical); only major-version automated fixes were offered and not applied.

## Phase 2: Data pipeline

- Start: 2026-10-05 19:21:42 +05:30
- End: 2026-10-05 19:57:19 +05:30
- Result: 44 source records validated for required metadata. Open-Meteo historical download returned HTTP 200, 5,368 bytes, 168 hourly rows; USGS returned HTTP 200, 369 bytes, 0 events in the query window. Both SHA-256 sidecars verified. Health report: 3 WORKING, 2 MANUAL, 0 FAILED, 39 NEEDS_REVIEW. `28` tests passed; frontend build passed.
- Phase exceeded its 20-minute allocation by more than 25%. No other registry sources were downloaded. NASA GLC current data page returned 404 and stays NEEDS_REVIEW; the other unverified, login/API-key, or manual sources remain MANUAL/NEEDS_REVIEW. Real data quality checks and negative-sampling limitations are documented; no real landslide inventory is available.