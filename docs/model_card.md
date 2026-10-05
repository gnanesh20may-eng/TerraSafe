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

The pipeline attempts Logistic Regression, Random Forest, XGBoost, and
LightGBM with five-fold `GroupKFold` cross-validation grouped by spatial
blocks. If native model imports are blocked, unavailable optional models are
omitted and the pipeline retains a Logistic Regression baseline. If the
scikit-learn linear-model extension is also blocked, a deterministic NumPy
binary Logistic Regression implementation is used. Available models report
fold accuracy, precision, recall, F1, ROC-AUC, false-alarm and miss rates, and
confusion counts. A final model is fit on all synthetic cells and emits Low,
Moderate, High, and Critical demo susceptibility polygons. Classes use
illustrative probability cutoffs 0.25, 0.50, and 0.75; they are not calibrated
warning thresholds.

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

## P3 inference and artifact status

The inference helper can load a local `.joblib` classifier only when its
adjacent `.sha256` integrity file matches; the checksum does not authenticate
the artifact publisher, and joblib files must be trusted before loading. If no
artifact exists, inference fits Logistic Regression on a deterministic
synthetic grid and labels its output `SIMULATED`. A loaded local model is
`SCAFFOLD` until its data lineage and validation are reviewed. Uncertainty is
`SCAFFOLD` unless adequate caller-supplied calibration residuals are provided;
the implementation does not claim that the current project has valid
real-world residuals. Zone quantiles, slope physics, rainfall memory, top
factors, and disagreement checks are scenario/demo features, not calibrated
causal explanations or safety thresholds.

Four Colab notebooks are checked in as **SCAFFOLD — NOT RUN**. No new
performance metric or trained LSTM/TFT result is reported for P3.
The export helper can produce ONNX, but the current inference loader accepts
only checksum-matched `.joblib` classifiers; ONNX Runtime inference is not
implemented.

## Reproduction

Install `requirements.txt`, then run:

```powershell
python -m backend.app.ml.train --no-mlflow
```

For MLflow logging, omit `--no-mlflow`; local metrics remain available in the
generated JSON regardless.
