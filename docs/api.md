# P4 API — DEMO / SIMULATED

TerraSafe is experimental decision support, **not a replacement for official
IMD, NDMA, or GSI warnings**. The API is local prototype code; it is not a
deployed or emergency-response service. Do not use its risk outputs or
generated CAP messages as operational warnings.

## Start locally

From the repository root in PowerShell:

```powershell
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
# Set a private JWT_SECRET of at least 32 characters in .env.
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --port 8000
```

The default local database is `./terrasafe.db` (SQLite). `DATABASE_URL` can
select PostgreSQL; credentials belong only in `.env` or the deployment
environment. The app checks database connectivity on `/health`. Alembic
migrations are the schema-upgrade path; startup metadata creation is retained
for local prototype convenience, not as a production migration strategy.

Create a short-lived development token without putting a key in source:

```powershell
$env:JWT_SECRET = "replace-with-a-private-value-of-at-least-32-characters"
.\.venv\Scripts\python.exe scripts\create_token.py --subject local-operator --role district_officer
```

`JWT_SECRET` must be at least 32 characters. The token tool prints a bearer
token to the terminal; do not commit or share it. Roles are `admin`,
`district_officer`, `field_responder`, and `public`. Public alert reads are
unauthenticated; creating alerts requires admin/district-officer; alert
updates and transitions use role checks; deletion requires admin; SOS listing
requires admin/district-officer/field-responder.

## Routes and evidence labels

| Method and path | Status | Behavior and limits |
| --- | --- | --- |
| `GET /health` | LIVE | Confirms the configured database answers `SELECT 1`; not a safety assessment. |
| `GET /api/v1/health/data-sources` | LIVE | Returns registry and recorded source-check state; only documented provider probes are live. |
| `GET /api/v1/risk/{location}` | SIMULATED / MISSING | Nilgiris uses generated synthetic inputs; other locations have no verified inputs. |
| `POST /api/v1/alerts` | DEMO | Persists a prototype alert; optional WGS84 geofence and coordinates are validated. |
| `GET /api/v1/alerts[?limit=N]` | DEMO | Lists non-deleted prototype alerts. |
| `GET /api/v1/alerts/{id}` | DEMO | Reads one alert. |
| `PATCH /api/v1/alerts/{id}` | DEMO | Role-checked metadata update, with audit entry. |
| `DELETE /api/v1/alerts/{id}` | DEMO | Admin-only soft delete for Created or Resolved alerts. |
| `POST /api/v1/alerts/{id}/transition` | DEMO | Strict Created → Approved → Sent → Delivered → Acknowledged → Resolved lifecycle. |
| `GET /api/v1/alerts/{id}/audit` | DEMO | Exposes the persisted hash-chain and reports invalid JSON/hash tampering. |
| `GET /api/v1/alerts/{id}/cap` | DEMO | CAP 1.2 XML is marked `Test`; generated geometry is labelled SIMULATED. |
| `POST /sos` | DEMO | Stores an SOS request; does not dispatch responders. Caller phone is omitted from create response. |
| `GET /sos` | DEMO | Role-protected prototype SOS listing. |
| `POST /sms/inbound` | DEMO / MISSING | Local `RISK <pincode>` query only; no SMS provider is contacted. |
| `POST /api/v1/simulate` | SIMULATED | Transparent uncalibrated scenario calculation; never a live warning. |
| `GET /api/v1/evacuation/nearest` | MISSING | No verified shelters or routes; returns no destination or directions. |
| `GET /api/v1/models/metrics` | MISSING | No generated evaluation metrics file is present. |
| `GET /rescue` | SCAFFOLD | Placeholder only; no dispatch, rescue coordination, or live incident feed. |

Every SMS, WhatsApp, email, voice, and web-push adapter is mock-only and
returns DEMO. There are no external notification credentials or provider calls.
Risk thresholds, escalation timing, and the 1 km CAP circle are demonstration
policies, not approved operational rules. Do not enter real personal or
emergency data into this prototype.
