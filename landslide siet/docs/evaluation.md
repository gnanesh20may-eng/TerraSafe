# Evaluation

## Dataset and method

No real landslide inventory CSV is included in this repository. These metrics
were computed from the deterministic synthetic Nilgiris pilot generated with
`grid_size=24` and `seed=42`: 576 rows (24 × 24), including 336 synthetic
positive labels. No row represents an observed landslide or measured terrain
sample.

The reported model is the pipeline's standardized, class-weighted Logistic
Regression classifier. Evaluation used five-fold `GroupKFold` with
`spatial_block` groups. Each row received one out-of-fold probability; the
classification threshold was 0.5. Metrics below were computed with
scikit-learn from the pooled out-of-fold predictions.

| Metric | Result |
| --- | ---: |
| Accuracy | 0.5990 |
| Precision | 0.6733 |
| Recall | 0.6071 |
| F1 | 0.6385 |
| ROC-AUC | 0.6396 |

Confusion matrix (actual rows: negative, positive; predicted columns:
negative, positive):

```text
              Predicted negative  Predicted positive
Actual negative              141                  99
Actual positive              132                 204
```

## Interpretation

These are software-pipeline demonstration metrics on synthetic labels, not
real-world model performance. They must not be used to guide evacuation,
emergency response, or landslide warnings. A real inventory, validated input
layers, independent spatial/temporal evaluation, calibration, and domain
review are required before operational use.

The repository's full four-model comparison could not be run in this Windows
environment: importing scikit-learn's tree estimators was blocked by the local
Application Control policy. Logistic Regression was evaluated separately
using the same project data generator and spatial-fold design; no results for
Random Forest, XGBoost, or LightGBM are claimed here.