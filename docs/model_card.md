# LandSense susceptibility model card (P1)

## Status and intended use

This is an engineering/demo baseline for a configurable pilot region, defaulting
to Nilgiris, Tamil Nadu. It is **not validated for operational landslide warning,
evacuation, or public-safety decisions** and must not replace official IMD, NDMA,
or GSI warnings.

## Data and provenance

The current pipeline generates a deterministic synthetic 40 × 40 terrain grid,
feature proxies, and synthetic landslide labels. No real DEM, NASA Global
Landslide Catalog, GSI Bhukosh, soil, land-cover, NDVI, or OSM download was
available or included. Synthetic features include elevation-derived slope,
aspect, curvature, proxy TWI, NDVI-like values, soil-clay proxy, land-cover
codes, and synthetic road/stream distances. All GeoJSON features carry a
`synthetic: true` marker.

## Methods

The pipeline compares Logistic Regression, Random Forest, XGBoost, and LightGBM
using five-fold `GroupKFold` cross-validation grouped by spatial blocks. It
reports mean fold accuracy, precision, recall, F1, ROC-AUC, and false-alarm and
miss rates, plus confusion counts aggregated across held-out folds. A final
model is fit on all synthetic cells and emits Low, Moderate, High, and Critical
demo susceptibility polygons. Classes use probability cutoffs 0.25, 0.50, and
0.75; these are illustrative, not calibrated thresholds.

## Performance and limitations

Metrics are produced locally by `backend/app/ml/train.py` and written to
`ml/data/generated/metrics.json`; they are intentionally not represented as
measured real-world performance. Synthetic train/test similarity makes these
scores unsuitable for generalization claims. The pilot needs real,
time-consistent, spatially held-out inventory and covariate data, calibration,
independent validation, and domain review before any applied use.

## P2 dynamic-risk status

The P2 code adds missingness-aware antecedent rainfall, configurable
intensity-duration comparisons, an infinite-slope factor-of-safety scenario
calculation, a non-calibrated hybrid risk index, and deterministic 24/48/72h
trigger outlooks. It does not claim a trained TFT/LSTM: real, time-aligned
training and calibration series were not available. Conformal intervals are
only emitted with an adequate held-out calibration set. PSI is used as an
operator-review drift signal, not an automatic retraining or promotion rule.
The P2 package also exposes MAPIE split-conformal intervals and ONNX export
helpers; neither constitutes deployment approval or calibration evidence.

## Reproduction

Install `requirements.txt`, then run:

```powershell
python -m backend.app.ml.train --no-mlflow
```

For MLflow logging, omit `--no-mlflow`; local metrics remain available in the
generated JSON regardless.
