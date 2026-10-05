"""Feature-distribution drift checks and retraining due policy."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Mapping

import numpy as np
import pandas as pd


def population_stability_index(
    reference: Any,
    current: Any,
    *,
    bins: int = 10,
    smoothing: float = 1e-6,
) -> float:
    """Compute PSI using reference quantile bins and smoothed frequencies."""
    ref = np.asarray(reference, dtype=float)
    new = np.asarray(current, dtype=float)
    if ref.ndim != 1 or new.ndim != 1 or ref.size == 0 or new.size == 0:
        raise ValueError("reference and current must be non-empty one-dimensional arrays")
    if not np.isfinite(ref).all() or not np.isfinite(new).all():
        raise ValueError("drift inputs must contain only finite values")
    if bins < 2 or smoothing <= 0:
        raise ValueError("bins must be at least 2 and smoothing positive")
    edges = np.unique(np.quantile(ref, np.linspace(0, 1, bins + 1)))
    if edges.size < 2:
        edges = np.array([ref[0] - 0.5, ref[0] + 0.5])
    edges[0] = -np.inf
    edges[-1] = np.inf
    ref_counts, _ = np.histogram(ref, bins=edges)
    new_counts, _ = np.histogram(new, bins=edges)
    ref_share = (ref_counts + smoothing) / (ref.size + smoothing * len(ref_counts))
    new_share = (new_counts + smoothing) / (new.size + smoothing * len(new_counts))
    return float(np.sum((new_share - ref_share) * np.log(new_share / ref_share)))


def dataset_drift_report(
    reference: pd.DataFrame,
    current: pd.DataFrame,
    *,
    threshold: float = 0.2,
) -> dict[str, Any]:
    """Report PSI per shared numeric feature; mismatched feature sets are errors."""
    if threshold <= 0:
        raise ValueError("threshold must be positive")
    if set(reference.columns) != set(current.columns):
        raise ValueError("reference and current feature columns must match exactly")
    scores = {
        name: population_stability_index(reference[name], current[name])
        for name in reference.columns
    }
    return {
        "method": "population_stability_index",
        "threshold": threshold,
        "feature_psi": scores,
        "drift_detected": any(score >= threshold for score in scores.values()),
    }


def retraining_recommendation(
    last_trained_at: str | datetime,
    drift_report: Mapping[str, Any],
    *,
    interval_days: int = 30,
    now: str | datetime | None = None,
) -> dict[str, Any]:
    """Decide whether the scheduled caller should enqueue a retraining run."""
    if interval_days < 1:
        raise ValueError("interval_days must be positive")
    current = _as_utc(now or datetime.now(timezone.utc))
    last = _as_utc(last_trained_at)
    due_by_time = current >= last + timedelta(days=interval_days)
    due_by_drift = bool(drift_report.get("drift_detected"))
    reasons = []
    if due_by_time:
        reasons.append(f"scheduled interval of {interval_days} days elapsed")
    if due_by_drift:
        reasons.append("population stability threshold exceeded")
    return {
        "retraining_recommended": due_by_time or due_by_drift,
        "reasons": reasons,
        "action": "enqueue_with_operator_review" if reasons else "no_action",
    }


def _as_utc(value: str | datetime) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00")) if isinstance(value, str) else value
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)
