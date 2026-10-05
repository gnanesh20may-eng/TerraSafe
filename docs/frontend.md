# P5 dashboard — DEMO

The local Next.js App Router dashboard runs at `http://localhost:3001`. It
reads `/health` and `/api/v1/alerts` from the FastAPI service and renders only
records returned by that API. If the service cannot be reached, the UI reports
the observed error; it does not insert example incidents.

The capability cards are explicitly labelled LIVE, DEMO, SIMULATED, SCAFFOLD,
or MISSING. There is no map, offline queue, separate rescue page, alert-write
control, SOS form, or rescue dispatch control. SOS, notifications, and alerts
remain prototype features; follow official IMD, NDMA, and GSI information and
local emergency services. Do not enter real personal or emergency data.

## Run locally

From the repository root:

```powershell
npm install
npm run dev
```

Run the API in a separate terminal:

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --port 8000
```

The client API base defaults to `http://localhost:8000`; set
`NEXT_PUBLIC_API_BASE_URL` at build time to use a different API. Configure
`CORS_ORIGINS` in the API environment with exact trusted origins when needed.
The default allowlist contains only `http://localhost:3001` and
`http://127.0.0.1:3001`; credentials are disabled.

## Validate

```powershell
npm run build
npm run typecheck
.\.venv\Scripts\python.exe -m pytest backend/tests -q
```

The build validates the frontend bundle, not a deployment, live provider,
public warning, or safety outcome.
