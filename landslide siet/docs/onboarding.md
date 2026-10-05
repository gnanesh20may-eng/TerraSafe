# Contributor Onboarding

## Local run

Run `scripts/setup.ps1` on Windows PowerShell or `sh scripts/setup.sh` on
Linux/macOS, after stopping any frontend dev/production server. The scripts create a virtual environment, install Python and
frontend dependencies, and copy `.env.example` to `.env` only when `.env` does
not already exist. No credentials are provisioned. Then run:

```powershell
.\.venv\Scripts\python -m pytest backend/tests -q
.\.venv\Scripts\python -m uvicorn backend.main:app --reload
```

In another terminal:

```powershell
cd frontend
npm run dev
```

## Tests and source data

Run backend tests from the repository root and `npm run build` from `frontend/`.
Generated pilot inputs are created by `backend/app/ml/synthetic_data.py`; no
real landslide inventory CSV or downloaded source data is included. Data
provenance and evaluation boundaries are in `docs/evaluation.md` and
`docs/status.md`.

## Model downloads and Windows note

There is no checked-in Colab notebook, exported model, model downloader, or
checksum manifest yet. Those are SCAFFOLD/MISSING, not runnable instructions.
Do not download unverified model files into source control. When model export
is available, obtain it from the project-owned Colab Drive artifact, verify its
published SHA-256 checksum, then place it under `backend/models/` (ignored by
Git).

On the current Windows laptop, scikit-learn tree estimator imports can be
blocked by Windows Application Control (`DLL load failed`); the local
LogisticRegression evaluation works. The documented workaround is to run
training in an authorized Google Colab environment after notebooks and model
export are provided. No workaround has been run or verified here.

The 2026-10-05 frontend `npm audit` reported eight advisories (six high, two
critical). npm's suggested fixes require major-version upgrades to Next.js,
Tailwind CSS, or MapLibre; those migrations need compatibility review and were
not applied during setup.

## Contribution and safety

Use branch prefixes `backend/`, `frontend/`, `ml/`, or `data/`. Keep all API
secrets in `.env`, label synthetic/demo data, add focused tests, and never
present this application as a replacement for official IMD, NDMA, or GSI
warnings.