# TerraSafe

TerraSafe is an environmental intelligence and landslide early-warning decision-support prototype. 

> **Disclaimer**: AI-based risk estimation. Early-warning decision support. This prototype does not replace official disaster-management warnings, IMD, NDMA, or GSI official advisories.

## Architecture & Deployment

- **Frontend**: Vite + React + Tailwind (located in `terrasafe/`)
- **Backend**: FastAPI (`backend/app/main.py`), public API routes under `/api/v1/*`
- **Deploy Target**: Vercel Services (configured via `vercel.json`)
- **Database**: Neon Postgres via `DATABASE_URL` (PostGIS optional; local SQLite fallback `./terrasafe.db`)

## Risk Levels & Rules

- **LOW** (0–24)
- **WATCH** (25–49)
- **HIGH** (50–74)
- **CRITICAL** (75–100) — *False-alarm rule*: CRITICAL requires $\ge 2$ supporting factors and confidence threshold met.

## Local Setup (Windows PowerShell)

```powershell
# Copy environment variables
if (-not (Test-Path .env)) { Copy-Item .env.example .env }

# Backend setup
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn backend.app.main:app --port 8000 --reload

# Frontend setup (in a separate terminal)
cd terrasafe
npm install
npm run dev
```

## Environment Variables (.env)

- `DATABASE_URL`: Connection string (PostgreSQL/Neon or SQLite)
- `JWT_SECRET`: Secret key for JWT authentication (at least 32 characters)
- `VITE_API_URL`: Backend API base URL (defaults to `/api/v1` on Vercel)
- `VITE_MAPTILER_KEY`: Optional MapTiler key for 3D terrain maps (OSM raster fallback if unset)

## Testing

```powershell
python -m pytest backend/tests -v
cd terrasafe
npm run build
```
