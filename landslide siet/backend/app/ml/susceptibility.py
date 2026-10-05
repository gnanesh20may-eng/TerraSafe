"""Spatially validated susceptibility model comparison and GeoJSON export."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

from backend.app.ml.synthetic_data import FEATURE_COLUMNS, SyntheticPilot

LOGGER = logging.getLogger(__name__)


def _model_factories(seed: int) -> dict[str, Any]:
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler

    factories = {
        "LogisticRegression": lambda: make_pipeline(
            StandardScaler(),
            LogisticRegression(max_iter=1000, class_weight="balanced", random_state=seed),
        ),
    }
    try:
        from sklearn.ensemble import RandomForestClassifier

        factories["RandomForest"] = lambda: RandomForestClassifier(
            n_estimators=120,
            min_samples_leaf=2,
            class_weight="balanced",
            random_state=seed,
            n_jobs=1,
        )
    except Exception as exc:
        LOGGER.warning("RandomForest unavailable; continuing without it: %s", exc)
    try:
        from xgboost import XGBClassifier

        factories["XGBoost"] = lambda: XGBClassifier(
            n_estimators=100,
            max_depth=3,
            learning_rate=0.06,
            subsample=0.9,
            colsample_bytree=0.9,
            eval_metric="logloss",
            tree_method="hist",
            n_jobs=1,
            random_state=seed,
        )
    except Exception as exc:
        LOGGER.warning("XGBoost unavailable; continuing without it: %s", exc)
    try:
        from lightgbm import LGBMClassifier

        factories["LightGBM"] = lambda: LGBMClassifier(
            n_estimators=100,
            max_depth=4,
            learning_rate=0.06,
            verbosity=-1,
            n_jobs=1,
            random_state=seed,
        )
    except Exception as exc:
        LOGGER.warning("LightGBM unavailable; continuing without it: %s", exc)
    return factories


def _classification_metrics(y_true: np.ndarray, scores: np.ndarray) -> dict[str, Any]:
    predicted = (scores >= 0.5).astype(int)
    positive = y_true == 1
    negative = ~positive
    predicted_positive = predicted == 1
    tp = int(np.count_nonzero(positive & predicted_positive))
    tn = int(np.count_nonzero(negative & ~predicted_positive))
    fp = int(np.count_nonzero(negative & predicted_positive))
    fn = int(np.count_nonzero(positive & ~predicted_positive))
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    roc_auc = None
    if np.count_nonzero(positive) and np.count_nonzero(negative):
        roc_auc = float(roc_auc_score(y_true, scores))
    return {
        "accuracy": float(np.mean(y_true == predicted)),
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),
        "roc_auc": roc_auc,
        "confusion_matrix": [[int(tn), int(fp)], [int(fn), int(tp)]],
        "false_alarm_rate": float(fp / (fp + tn)) if fp + tn else 0.0,
        "miss_rate": float(fn / (fn + tp)) if fn + tp else 0.0,
    }


def _aggregate_fold_metrics(fold_results: list[dict[str, Any]]) -> dict[str, Any]:
    keys = ("accuracy", "precision", "recall", "f1", "roc_auc", "false_alarm_rate", "miss_rate")
    aggregate: dict[str, Any] = {}
    for key in keys:
        values = [result[key] for result in fold_results if result[key] is not None]
        aggregate[key] = float(np.mean(values)) if values else None
    matrices = np.sum([np.asarray(result["confusion_matrix"]) for result in fold_results], axis=0)
    aggregate["confusion_matrix"] = matrices.astype(int).tolist()
    aggregate["folds"] = len(fold_results)
    return aggregate


def evaluate_models(
    cells: pd.DataFrame,
    seed: int = 42,
    n_splits: int = 5,
) -> dict[str, Any]:
    """Compare classifiers with GroupKFold splits over disjoint spatial blocks."""
    if len(cells) == 0:
        raise ValueError("cells must contain at least one row")
    if cells["landslide_label"].nunique() < 2:
        raise ValueError("spatial validation requires both landslide classes")
    groups = cells["spatial_block"].to_numpy()
    split_count = min(n_splits, np.unique(groups).size)
    if split_count < 2:
        raise ValueError("spatial validation requires at least two spatial blocks")

    features = cells.loc[:, FEATURE_COLUMNS]
    target = cells["landslide_label"].to_numpy()
    factories = _model_factories(seed)
    from sklearn.model_selection import GroupKFold

    metrics: dict[str, Any] = {}
    splitter = GroupKFold(n_splits=split_count)
    for model_name, factory in factories.items():
        fold_results = []
        for train_index, test_index in splitter.split(features, target, groups):
            model = factory()
            model.fit(features.iloc[train_index], target[train_index])
            scores = model.predict_proba(features.iloc[test_index])[:, 1]
            fold_results.append(_classification_metrics(target[test_index], scores))
        metrics[model_name] = _aggregate_fold_metrics(fold_results)
    return {
        "validation": "GroupKFold spatial-block cross-validation",
        "spatial_blocks": int(np.unique(groups).size),
        "folds": split_count,
        "threshold": 0.5,
        "metrics": metrics,
    }


def _zone_for_probability(probability: float) -> str:
    if probability < 0.25:
        return "Low"
    if probability < 0.5:
        return "Moderate"
    if probability < 0.75:
        return "High"
    return "Critical"


def make_zone_geojson(pilot: SyntheticPilot, model: Any) -> dict[str, Any]:
    """Predict every synthetic grid cell and export rectangular GeoJSON zones."""
    cells = pilot.cells
    probability = model.predict_proba(cells.loc[:, FEATURE_COLUMNS])[:, 1]
    west, south, east, north = pilot.bounds
    grid_size = int(np.sqrt(len(cells)))
    dx = (east - west) / (grid_size - 1)
    dy = (north - south) / (grid_size - 1)
    features = []
    for row, (cell, score) in enumerate(zip(cells.to_dict("records"), probability)):
        x0 = max(west, float(cell["longitude"]) - dx / 2)
        x1 = min(east, float(cell["longitude"]) + dx / 2)
        y0 = max(south, float(cell["latitude"]) - dy / 2)
        y1 = min(north, float(cell["latitude"]) + dy / 2)
        features.append(
            {
                "type": "Feature",
                "id": row,
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[x0, y0], [x1, y0], [x1, y1], [x0, y1], [x0, y0]]],
                },
                "properties": {
                    "region": pilot.region,
                    "zone": _zone_for_probability(float(score)),
                    "susceptibility_score": round(float(score), 6),
                    "data_source": pilot.source_label,
                    "synthetic": True,
                },
            }
        )
    return {
        "type": "FeatureCollection",
        "name": "TerraSafe synthetic susceptibility zones",
        "metadata": {
            "region": pilot.region,
            "data_source": pilot.source_label,
            "disclaimer": (
                "Synthetic demonstration output. Not for operational decisions or "
                "as a substitute for official IMD, NDMA, or GSI warnings."
            ),
        },
        "features": features,
    }


def train_and_export(
    pilot: SyntheticPilot,
    output_dir: Path,
    seed: int = 42,
    log_to_mlflow: bool = True,
) -> dict[str, Any]:
    """Evaluate all requested models, fit the leading model, and export results."""
    output_dir.mkdir(parents=True, exist_ok=True)
    evaluation = evaluate_models(pilot.cells, seed=seed)
    best_name = max(
        evaluation["metrics"],
        key=lambda name: evaluation["metrics"][name]["roc_auc"] or 0,
    )
    best_model = _model_factories(seed)[best_name]()
    best_model.fit(pilot.cells.loc[:, FEATURE_COLUMNS], pilot.cells["landslide_label"])
    zones = make_zone_geojson(pilot, best_model)
    result = {
        "region": pilot.region,
        "data_source": pilot.source_label,
        "sample_count": len(pilot.cells),
        "positive_samples": int(pilot.cells["landslide_label"].sum()),
        "best_model": best_name,
        **evaluation,
    }
    (output_dir / "metrics.json").write_text(
        json.dumps(result, indent=2), encoding="utf-8"
    )
    (output_dir / "susceptibility_zones.geojson").write_text(
        json.dumps(zones, indent=2), encoding="utf-8"
    )
    if log_to_mlflow:
        _log_to_mlflow(result)
    return result


def _log_to_mlflow(result: dict[str, Any]) -> None:
    try:
        import mlflow
    except ImportError:
        LOGGER.warning("MLflow is not installed; metrics were exported to metrics.json only.")
        return
    with mlflow.start_run(run_name="terrasafe-synthetic-susceptibility"):
        mlflow.set_tag("data_source", result["data_source"])
        mlflow.set_tag("region", result["region"])
        mlflow.set_tag("validation", result["validation"])
        mlflow.log_param("best_model", result["best_model"])
        mlflow.log_param("sample_count", result["sample_count"])
        for name, values in result["metrics"].items():
            for metric, value in values.items():
                if isinstance(value, (float, int)):
                    mlflow.log_metric(f"{name}.{metric}", value)
