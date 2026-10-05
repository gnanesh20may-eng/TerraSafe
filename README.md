# LandSense

LandSense is an offline-first AI landslide early-warning and risk-monitoring
platform scaffold for PSA 04. **It is a decision-support tool, not a replacement
for official IMD, NDMA, or GSI warnings.** P1 currently provides a runnable
synthetic-data susceptibility experiment, not an operational warning service.

## P1: synthetic susceptibility baseline

Python 3.11+ is currently used for local development. The requested Python 3.12
interpreter is not installed on the inspected machine; use an installed
compatible interpreter for now.

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
