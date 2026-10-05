# ML Pipeline

## Overview

LandSense uses two complementary models:

1. Susceptibility model: static and long-term terrain features
2. Trigger model: dynamic rainfall and environmental conditions

The final risk score is computed as:

```text
final_risk = normalize(susceptibility_score + trigger_risk_score)
```

with the final value normalized to a 0-100 scale and mapped to:

- 0-24: LOW
- 25-49: WATCH
- 50-74: HIGH
- 75-100: CRITICAL

These thresholds should be configurable rather than hard-coded.

## Model A: susceptibility

Inputs include:
- elevation
- slope
- aspect
- curvature
- terrain ruggedness
- geology and soil drainage
- land cover and vegetation index
- historical landslide density
- topographic wetness proxies

## Model B: trigger risk

Inputs include:
- rainfall in 1h, 6h, 24h, 3d, 7d windows
- rainfall anomaly
- soil moisture
- wind conditions
- temperature anomalies
- forecast instability

## Data validation and leakage control

- use temporal validation where possible
- avoid random splits on spatial grids that leak geography
- preserve region-level block structure for holdout validation
- report confusion matrix, ROC-AUC, PR-AUC, precision, recall, F1, and false negatives

## Registration and serving

- train models with reproducible features
- compare candidates using validation metrics
- select best model or ensemble if justified
- explain predictions with SHAP
- register model via MLflow
- serve inference through FastAPI

## Current implementation status

- `backend/app/ml/inference.py` loads a local model artifact when present; with no artifact it fits a deterministic LogisticRegression model on synthetic cells and marks its output DEMO. It is not wired into the risk API yet.
- Predictive uncertainty is explicitly unavailable without a conformal model. Current per-instance explanation is a LogisticRegression coefficient contribution, not SHAP.
- The physics helper calculates an infinite-slope factor of safety only from caller-supplied soil parameters. Rainfall intensity-duration coefficients and hybrid weights require local calibration; helper output is labelled SCAFFOLD/SIMULATED.
- Four notebooks under `notebooks/` are Colab scaffolds and have not been run. No tree-model comparison, TFT, SHAP, MAPIE, ONNX, or model export has been validated here.
- Optional tree imports are guarded and LogisticRegression remains the minimum viable local path. In this workspace, the RandomForest import probe returned `TREE_IMPORT_OK`; no tree model training was attempted.
- `scripts/fetch_models.py` requires HTTPS and a matching SHA-256 manifest, caps downloads at 200 MiB, and targets `backend/models/`. A checksum does not establish publisher trust; joblib artifacts are executable pickle payloads.

## Demo and production note

This repository uses demo/synthetic data in development mode. Production deployments should replace the demo provider with verified data and a trained model with documented validation metrics.
