# TerraSafe

TerraSafe is a landslide early-warning and rescue-platform prototype for PSA
04. **It is a decision-support tool, not a replacement for official IMD, NDMA,
or GSI warnings.** The current checkout contains synthetic susceptibility and
dynamic-risk/forecast helpers plus a P4 FastAPI service, but no Next.js
frontend. Its alerts, SOS, and notification paths remain DEMO-only. Check
[`docs/status.md`](docs/status.md) for observed feature status and limitations.

## P1: synthetic susceptibility baseline

Python 3.11+ is used for local development. On Windows, run
`.\scripts\setup.ps1`; on macOS/Linux, run `./scripts/setup.sh`.

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m backend.app.ml.train
python -m pytest backend/tests
```

To run without MLflow tracking:

```powershell
python -m backend.app.ml.train --no-mlflow
```

The default command generates a clearly labelled synthetic Nilgiris grid,
compares Logistic Regression, Random Forest, XGBoost, and LightGBM with
spatial-block cross-validation, logs to local MLflow, and writes metrics and
susceptibility polygons to `ml/data/generated/`. No API keys or external
downloads are required for this phase. Synthetic output is not a real warning
and must never guide safety decisions.

Pass `--region` and four WGS84 coordinates (`west south east north`) to label
and place a synthetic pilot grid for another area. Its terrain layers and
inventory labels remain synthetic.

## P2: dynamic risk and forecast baseline

The async source adapters run entirely from labeled fixtures by default.
Open-Meteo and USGS have opt-in live JSON adapters; NASA/IMD sources require
configured product-specific endpoints and normalization. The P2 rainfall,
infinite-slope, dynamic-risk, 24/48/72-hour forecast, conformal interval, SHAP,
counterfactual, and PSI helpers are documented in `docs/dynamic-risk.md`.
Thresholds and the trigger-based forecast are experimental, and no real
provider feed or trained time-series model is implied.

The source registry, health checker, and bounded Nilgiris downloader are
described in [`docs/data_sources.md`](docs/data_sources.md). Health checks
probe only Open-Meteo Archive and USGS; other source rows are MANUAL or
NEEDS_REVIEW. Run the API with
`python -m uvicorn backend.app.main:app --port 8000`. Route behavior,
authentication, migration, and explicit demo limitations are documented in
[`docs/api.md`](docs/api.md).

## P3: model inference scaffold

`backend.app.ml.inference.infer_risk()` provides a labeled synthetic Logistic
Regression fallback, optional checksum-verified local model loading, hybrid
rainfall/slope calculations, zone-threshold and disagreement indicators, and
explicit placeholder uncertainty when calibration is absent. The four
notebooks under `notebooks/` are SCAFFOLD and NOT RUN. See
[`docs/model_card.md`](docs/model_card.md) for limits and artifact trust notes.

## Contributing

See [`docs/onboarding.md`](docs/onboarding.md) for setup and contribution
guidance. Pull requests must include focused tests and update feature labels in
`docs/status.md`. Use `git -c core.whitespace=cr-at-eol diff --check` before
committing. The CI workflow runs the backend tests; it runs a frontend build
only when a frontend package manifest is present.
