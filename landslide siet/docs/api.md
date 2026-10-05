# API Design

## Base URL

```text
/api/v1
```

## Core endpoints

- `GET /api/v1/health`
- `POST /api/v1/auth/login`
- `GET /api/v1/locations/search`
- `GET /api/v1/locations/{id}`
- `GET /api/v1/risk/{location_id}`
- `GET /api/v1/risk/{location_id}/history`
- `GET /api/v1/environment/{location_id}`
- `GET /api/v1/terrain/{location_id}`
- `GET /api/v1/map/risk-zones`
- `GET /api/v1/safe-zones`
- `GET /api/v1/rescue/nearby`
- `GET /api/v1/rescue/route`
- `GET /api/v1/alerts`
- `POST /api/v1/alerts/preferences`
- `GET /api/v1/data-sources`
- `GET /api/v1/models`

## SOS and persistence

- `POST /sos` accepts `{ "message": "...", "latitude": 11.35, "longitude": 76.8 }`. It persists an OPEN report in SQLite by default and returns `delivery: MOCK`; no responder is notified by this API.
- `GET /sos` requires a bearer token with `admin`, `district_officer`, or `field_responder` role.
- `GET /api/v1/alerts` is public and returns persisted alert history (empty until alerts have been created).
- `POST /api/v1/alerts` requires `admin` or `district_officer`; it creates a CREATED alert and a hash-chained event.
- `POST /api/v1/alerts/{id}/lifecycle` supports CREATED -> APPROVED -> SENT -> DELIVERED -> ACKNOWLEDGED -> RESOLVED, with the service enforcing allowed transitions. Approval requires authority role. SENT is mock-only and explicitly states that no message was delivered.
- `GET /api/v1/alerts/{id}/cap` returns CAP 1.2 XML in Test status; it is not an official warning.
- `POST /api/v1/simulate` returns SIMULATED what-if output from the demo weighted heuristic.
- `GET /api/v1/rescue/route?latitude=...&longitude=...` chooses the nearest demo shelter by straight-line distance; it does not provide road routing or hazard avoidance.
- `POST /api/v1/sms/inbound` is a parser simulation only. It sends and receives no SMS.
- `GET /api/v1/models/metrics` returns MISSING unless a generated metrics file exists; no sample metrics are synthesized.
- `GET /api/v1/health/data-sources` returns the last source-health snapshot, or NEEDS_REVIEW before one has been generated.

Database: `DATABASE_URL` defaults to `sqlite:///./terrasafe.db`; configure a PostgreSQL URL for PostgreSQL. Apply Alembic migrations from the project root with `python -m alembic upgrade head`.

JWT: set `JWT_SECRET` outside source control. A trusted local operator can issue a short-lived role token using `python scripts/issue_token.py --subject operator-id --role district_officer`; protect the terminal/output. There is no public user registration or password login endpoint.

## Risk response contract

```json
{
  "location": {
    "name": "Coonoor",
    "latitude": 11.35,
    "longitude": 76.8
  },
  "risk": {
    "score": 0,
    "level": "LOW",
    "trend": "STABLE",
    "model_status": "DEMO — weighted heuristic, not a validated model"
  },
  "confidence": {
    "available": false,
    "value": null,
    "reason": "No calibrated model confidence is available."
  },
  "environment": {
    "rainfall_24h_mm": null,
    "soil_moisture_pct": null,
    "wind_speed_kmh": null,
    "temperature_c": null
  },
  "terrain": {
    "elevation_m": null,
    "slope_deg": null
  },
  "contributors": [
    {
      "factor": "Rainfall",
      "impact": "HIGH",
      "direction": "INCREASE"
    }
  ],
  "recommendation": {
    "severity": "HIGH",
    "message": "Risk is elevated. Avoid unnecessary travel through steep or vulnerable areas and monitor official emergency instructions."
  },
  "timestamp": "<server-generated ISO-8601 timestamp>"
}
```

## Response conventions

- use structured JSON
- include timestamps
- include stale-data flags where needed
- keep Pydantic schemas private to the API layer
- never expose DB models directly
- never present fixed confidence as calibrated uncertainty
- public risk output is demo weighted logic until a reviewed model is integrated
