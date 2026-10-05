# TerraSafe

TerraSafe is an AI-assisted landslide early-warning and risk-monitoring platform for geospatial decision support. This repository currently contains a runnable local demonstration and backend scaffold.

## Purpose

The system supports:
- Search and selection of a monitored area
- Collection of terrain, weather, and satellite signals
- ML-based landslide susceptibility and trigger analysis
- Risk scoring with explanation and action guidance
- Rescue and safe-zone workflows
- Alerts, monitoring, and operational dashboards

Important: This platform is decision-support software and not a replacement for official disaster-management warnings or emergency instructions.

## Current phase

Phase 1 includes:
- Monorepo structure and project architecture
- Database and API architecture design
- ML and GIS pipeline documentation
- Frontend and backend skeletons
- Docker and CI scaffolding
- Basic authentication and health endpoints
- Validation via Python tests

## Repository layout

```text
landslide siet/
├── README.md
├── .env.example
├── requirements.txt
├── docker-compose.yml
├── docker/
│   ├── backend.Dockerfile
│   └── frontend.Dockerfile
├── .github/
│   └── workflows/
│       └── ci.yml
├── docs/
│   ├── architecture.md
│   ├── api.md
│   ├── ml-pipeline.md
│   ├── gis-pipeline.md
│   └── deployment.md
├── frontend/
│   ├── app/
│   ├── package.json
│   ├── next.config.mjs
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   ├── postcss.config.js
│   └── .eslintrc.json
├── backend/
│   ├── app/
│   ├── tests/
│   └── main.py
├── ml/
│   └── data/
└── gis/
    └── preprocessing/
```

## Quick start

### Python backend

```bash
cd "landslide siet"
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
python -m pip install -r requirements.txt
python -m pytest backend/tests
uvicorn backend.main:app --reload
```

### Docker

```bash
cd "landslide siet"
docker compose up --build
```

## Environment variables

Copy `.env.example` to `.env` and configure values as needed.

```bash
cp .env.example .env
```

## Risk disclaimer

This project intentionally uses clearly marked demo/synthetic data and monitoring logic for development. Real operational deployment requires validated data sources, trained models, geospatial grounding, and official warning workflows.

## Known limitations

- **Live:** Weather requests use Open-Meteo without an API key and have a five-second timeout. A failed request falls back to clearly labelled demo weather. Browser geolocation is used only after the user grants permission.
- **Demo:** Terrain and satellite observations, location catalogue, risk history, shelters, contacts, and susceptibility training data are demonstration data. Risk estimates are not official warnings.
- **Simulated:** The `/rescue` relay path, device signal states, and family links are UI simulation only; no Bluetooth, radio, or device-to-device mesh is implemented. SOS API events are kept in process memory and are lost when the backend restarts; they are not forwarded to emergency services.

See [docs/evaluation.md](docs/evaluation.md) for the measured synthetic-data metrics and their limits.

## Contributing

Create focused branches using `backend/`, `frontend/`, `ml/`, or `data/`
prefixes, for example `backend/sos-storage` or `data/open-meteo-history`.
Keep credentials in an untracked `.env`; never commit real API keys, downloaded
datasets, or model artifacts. Add or update tests for behavior changes and run
`python -m pytest backend/tests -q` and `npm run build` before opening a PR.
Use the [pull request template](.github/PULL_REQUEST_TEMPLATE.md) and follow
[docs/onboarding.md](docs/onboarding.md) for the local setup.

## Phase 1 outcomes

Completed in this stage:
- System architecture definition
- Database ER model and API design
- ML and GIS pipeline concepts
- Frontend and backend skeletons
- Security/auth foundations
- Docker and CI scaffolding
- Testable baseline

## Next phase

The next step is to extend the home screen, location search, map, and backend risk API flow from this foundation.
