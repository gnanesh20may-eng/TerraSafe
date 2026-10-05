<<<<<<< HEAD
# TerraSafe susceptibility model card (P1)

## Status and intended use

This is an engineering/demo baseline for Nilgiris, Tamil Nadu. It is **not
validated for operational landslide warning, evacuation, or public-safety
decisions** and must not replace official IMD, NDMA, GSI, or local-authority
warnings.

## Data and provenance

The training pipeline generates a deterministic synthetic 40 × 40 terrain
grid, feature proxies, and synthetic labels. The inference fallback fits a
LogisticRegression model on a deterministic 16 × 16 synthetic grid. No real
landslide inventory or terrain product was downloaded. Phase 2 did retrieve
168 hourly Open-Meteo ERA5-Land reanalysis rows for one Nilgiris coordinate and
queried USGS earthquakes (0 matching events); neither is a landslide label or
training observation in this model. Synthetic features include elevation,
slope, aspect, curvature, proxy TWI, NDVI-like values, soil-clay proxy,
land-cover codes, and synthetic road/stream distances. Synthetic GeoJSON cells
carry a `synthetic: true` marker.

## Methods

The code supports LogisticRegression and optional RandomForest, XGBoost, and
LightGBM candidates with `GroupKFold` spatial-block splits. Optional model
imports are guarded so LogisticRegression remains available if a tree library
cannot load. A single guarded probe confirmed that RandomForest imports in the
current workspace venv; no tree-model training or comparison has been run here.
When an exported artifact is absent, `InferenceEngine` fits a synthetic
LogisticRegression fallback in memory. Its response is labelled DEMO, returns
coefficient contributions rather than SHAP, and reports uncertainty as
unavailable. Physics and rainfall intensity-duration helpers require measured
soil parameters and locally reviewed threshold coefficients; their hybrid
weights are caller-supplied and marked SIMULATED.

## Performance and limitations

**No model performance metrics are reported in this card:** the training
pipeline has not been run for this work. Do not claim accuracy, AUC, lead time,
calibration, or generalization. Four Colab notebooks exist as SCAFFOLD and have
not been executed. TFT, MAPIE conformal intervals, SHAP, and ONNX export remain
unrun. Before applied use, the pilot needs licensed real inventory,
time-consistent terrain/environmental covariates, spatial and temporal holdout,
calibration, independent evaluation, and domain review.

## Reproduction

Install `requirements.txt`, then run the synthetic-only training command:

```powershell
python -m backend.app.ml.train --no-mlflow
```

The command has not been run as part of this implementation. Any generated
metrics/artifacts describe only synthetic data. Exported joblib files are
trusted-code-only; fetch them only from a reviewed HTTPS source with a matching
SHA-256 manifest using `scripts/fetch_models.py`.
=======
# TerraSafe susceptibility model card (P1)

## Status and intended use

This is an engineering/demo baseline for Nilgiris, Tamil Nadu. It is **not
validated for operational landslide warning, evacuation, or public-safety
decisions** and must not replace official IMD, NDMA, GSI, or local-authority
warnings.

## Data and provenance

The training pipeline generates a deterministic synthetic 40 × 40 terrain
grid, feature proxies, and synthetic labels. The inference fallback fits a
LogisticRegression model on a deterministic 16 × 16 synthetic grid. No real
landslide inventory or terrain product was downloaded. Phase 2 did retrieve
168 hourly Open-Meteo ERA5-Land reanalysis rows for one Nilgiris coordinate and
queried USGS earthquakes (0 matching events); neither is a landslide label or
training observation in this model. Synthetic features include elevation,
slope, aspect, curvature, proxy TWI, NDVI-like values, soil-clay proxy,
land-cover codes, and synthetic road/stream distances. Synthetic GeoJSON cells
carry a `synthetic: true` marker.

## Methods

The code supports LogisticRegression and optional RandomForest, XGBoost, and
LightGBM candidates with `GroupKFold` spatial-block splits. Optional model
imports are guarded so LogisticRegression remains available if a tree library
cannot load. A single guarded probe confirmed that RandomForest imports in the
current workspace venv; no tree-model training or comparison has been run here.
When an exported artifact is absent, `InferenceEngine` fits a synthetic
LogisticRegression fallback in memory. Its response is labelled DEMO, returns
coefficient contributions rather than SHAP, and reports uncertainty as
unavailable. Physics and rainfall intensity-duration helpers require measured
soil parameters and locally reviewed threshold coefficients; their hybrid
weights are caller-supplied and marked SIMULATED.

## Performance and limitations

**No model performance metrics are reported in this card:** the training
pipeline has not been run for this work. Do not claim accuracy, AUC, lead time,
calibration, or generalization. Four Colab notebooks exist as SCAFFOLD and have
not been executed. TFT, MAPIE conformal intervals, SHAP, and ONNX export remain
unrun. Before applied use, the pilot needs licensed real inventory,
time-consistent terrain/environmental covariates, spatial and temporal holdout,
calibration, independent evaluation, and domain review.

## Reproduction

Install `requirements.txt`, then run the synthetic-only training command:

```powershell
python -m backend.app.ml.train --no-mlflow
```

The command has not been run as part of this implementation. Any generated
metrics/artifacts describe only synthetic data. Exported joblib files are
trusted-code-only; fetch them only from a reviewed HTTPS source with a matching
SHA-256 manifest using `scripts/fetch_models.py`.
>>>>>>> 68247b28399611dceff7fde13ff6e92af3ed0419
