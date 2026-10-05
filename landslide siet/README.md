# TerraSafe

TerraSafe (formerly LandSense) is an AI-assisted landslide early-warning and risk-monitoring platform for geospatial decision support. This repository is an early prototype, not an operational warning system.

## Purpose

The system supports:
- Search and selection of a monitored area
- Collection of terrain, weather, and satellite signals
- ML-based landslide susceptibility and trigger analysis
- Risk scoring with explanation and action guidance
- Rescue and safe-zone workflows
- Alerts, monitoring, and operational dashboards

Important: This platform is decision-support software and is not a replacement for official IMD, NDMA, GSI, or local-authority warnings and emergency instructions.

## Current implementation status

Completed foundation:
- Monorepo structure and project architecture
- Database and API architecture design
- ML and GIS pipeline documentation
- Frontend and backend skeletons
- Docker and CI scaffolding
- Basic authentication and health endpoints
- Validation via Python tests

Current provider slice:
- Open-Meteo weather is selected when `DEMO_MODE=false`.
- Terrain and satellite responses remain demo data until real DEM and Earth-observation processors are configured.
- Mixed-source status is explicit; upstream weather failures return HTTP 503 without silently substituting demo measurements.

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

### Recommended setup

Run `scripts/setup.ps1` from PowerShell on Windows or `bash scripts/setup.sh` on macOS/Linux. See [Contributor Onboarding](docs/onboarding.md) for the manual steps and known platform limitations.

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

Set `DEMO_MODE=false` to request live Open-Meteo weather. This does not enable live terrain, satellite observations, or a validated landslide model.

```bash
cp .env.example .env
```

## Risk disclaimer

This project intentionally uses clearly marked demo/synthetic data and monitoring logic for development. Real operational deployment requires validated data sources, trained models, geospatial grounding, and official warning workflows.

## Contributing

Create branches using `data/`, `ml/`, `backend/`, `frontend/`, or `rescue/` prefixes, followed by a short kebab-case task name. Keep pull requests scoped, add focused tests, and update `docs/status.md` when feature status or data provenance changes. See [issue-labels.md](docs/issue-labels.md) for triage conventions and the pull request template for the review checklist. The current CODEOWNERS file is only a placeholder and does not configure active reviewers.

Before opening a pull request, run `python -m pytest backend/tests -q`, `npm run typecheck`, and `npm run build` from `frontend/`. Do not commit `.env`, credentials, private data, downloaded datasets, or unreviewed model artifacts.
