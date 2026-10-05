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
- `GET /api/v1/risk?latitude={lat}&longitude={lon}`
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
- `GET /sos`
- `POST /sos`

Weather fields include `source`, set to `open-meteo` when the live request
succeeds and `demo` when it falls back. `/health` and `/api/v1/health` report
`weather_source` and set `demo_mode` according to the current Open-Meteo check.

SOS events are stored in backend process memory for this demonstration and are
cleared when the process restarts. They are not delivered to emergency
services.

## Example risk response

```json
{
  "location": {
    "name": "Coonoor",
    "latitude": 11.35,
    "longitude": 76.8
  },
  "risk": {
    "score": 68,
    "level": "HIGH",
    "trend": "INCREASING"
  },
  "confidence": {
    "available": true,
    "value": 0.82
  },
  "environment": {
    "rainfall_24h": 48.5,
    "soil_moisture": 68,
    "wind_speed": 18,
    "temperature": 24.3
  },
  "terrain": {
    "elevation": 506,
    "slope": 28
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
  "timestamp": "2026-10-05T12:00:00Z"
}
```

## Response conventions

- use structured JSON
- include timestamps
- include stale-data flags where needed
- keep Pydantic schemas private to the API layer
- never expose DB models directly
