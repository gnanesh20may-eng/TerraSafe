# LandSense

LandSense is an AI-assisted landslide early-warning and risk-monitoring platform for geospatial decision support. This repository currently contains the Phase 1 foundation for a production-grade architecture and a runnable local backend scaffold.

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
