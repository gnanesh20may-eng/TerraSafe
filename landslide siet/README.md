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

Data pipeline:
- `data_sources/registry.yaml` tracks source access, licence, coverage, fallback, and verification status. Ten approximate region bounds are query windows, not legal boundaries.
- Preview the approved Nilgiris requests with `scripts/download_all.py --source open_meteo_nilgiris_history --source usgs_earthquake_catalog --region nilgiris --dry-run`; remove `--dry-run` to fetch. Raw data, mocks, and logs are git-ignored.
- Run `scripts/check_sources.py --region nilgiris` to write the source health report and API snapshot. Run `scripts/validate_download.py <file>` to check supported JSON/GeoJSON structure.
- Only Open-Meteo historical reanalysis and USGS FDSN were queried. See [data_health.md](docs/data_health.md); NASA/GSI inventory and other sources remain manual or under review.

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
├── data_sources/
│   └── registry.yaml
├── scripts/
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

Create branches using `data/`, `ml/`, `backend/`, `frontend/`, or `rescue/` prefixes, followed by a short kebab-case task name. Keep pull requests scoped, add focused tests, and update `docs/status.md` when feature status or data provenance changes. See [issue-labels.md](docs/issue-labels.md) for triage conventions and the pull request template for the review checklist. The current CODEOWNERS file is only a placeholder and does not configure active reviewers.

Before opening a pull request, run `python -m pytest backend/tests -q`, `npm run typecheck`, and `npm run build` from `frontend/`. Do not commit `.env`, credentials, private data, downloaded datasets, or unreviewed model artifacts.
