# Contributor Onboarding

## Project state

This checkout is an early decision-support prototype. Read [status.md](status.md) and [limitations.md](limitations.md) if present before interpreting risk scores, shelter examples, weather, or maps. The dashboard is not a replacement for official IMD, NDMA, GSI, or local-authority warnings.

## Setup

From the repository root (`landslide siet`):

- Windows PowerShell: `scripts/setup.ps1`
- macOS/Linux: `bash scripts/setup.sh`

The scripts create a local `.venv`, install `requirements.txt`, copy `.env.example` to `.env` only if `.env` does not already exist, install the frontend lockfile, and print run/test commands. Keep credentials in `.env`; never commit it.

## Run and test

Backend: `python -m uvicorn backend.main:app --reload --port 8000`

Frontend: `cd frontend` then `npm run dev` (port 3001).

Backend tests: `python -m pytest backend/tests -q` from the project root.

Frontend validation: `cd frontend`, then `npm run typecheck` and `npm run build`.

## Data and model locations

- Source registry: `data_sources/registry.yaml` when available; source access and licence must be reviewed there before downloading.
- Local source outputs: `data_sources/raw/` and `data_sources/processed/`; do not commit downloaded datasets unless their licence and repository policy explicitly allow it.
- Training inputs and outputs: `ml/data/`; generated examples must remain labelled synthetic.
- Exported model destination: `backend/models/` when the model-fetch workflow is implemented. Verify checksums and the model card before loading any artifact.

## Colab model workflow

Colab notebooks are planned scaffolding unless marked executed in `docs/status.md`. Run them manually in an account with Drive access; record runtime, data provenance, split design, metrics, and artifact checksums. Do not report notebook outputs as locally verified until they have been reproduced or independently checked.

## Known Windows tree-library issue

On the project laptop, native scikit-learn tree-model imports can be blocked by Windows Application Control. Do not attempt to bypass that control. The inference path should attempt optional tree libraries inside a guarded import and use the existing LogisticRegression path when unavailable. A supported Colab/Linux export can be fetched only after checksum validation. Current status and exact evidence belong in `docs/status.md`.

## Contribution branches

Use prefixes: `data/`, `ml/`, `backend/`, `frontend/`, and `rescue/`, followed by a short kebab-case topic. Keep changes scoped, add focused tests, and update provenance/status documentation whenever a source, model, emergency workflow, or freshness claim changes.
