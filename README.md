# TerraSafe

TerraSafe is a landslide early-warning and rescue-platform prototype for PSA
04. **It is a decision-support tool, not a replacement for official IMD, NDMA,
or GSI warnings.** The current checkout contains synthetic susceptibility and
dynamic-risk/forecast helper code; it does not contain a FastAPI service or
Next.js frontend. Check [`docs/status.md`](docs/status.md) for observed feature
status and limitations.

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

## Contributing

See [`docs/onboarding.md`](docs/onboarding.md) for setup and contribution
guidance. Pull requests must include focused tests and update feature labels in
`docs/status.md`. Use `git -c core.whitespace=cr-at-eol diff --check` before
committing. The CI workflow runs the backend tests; it runs a frontend build
only when a frontend package manifest is present.
