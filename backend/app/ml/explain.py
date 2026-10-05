"""Per-zone SHAP explanations, constrained counterfactuals, and text fallback."""

from __future__ import annotations

from typing import Any, Mapping

import numpy as np
import pandas as pd


def explain_with_shap(
    model: Any,
    observations: pd.DataFrame,
    background: pd.DataFrame | None = None,
) -> dict[str, Any]:
    """Compute per-row contributions or explicitly report SHAP unavailable."""
    if observations.empty:
        raise ValueError("observations must contain at least one row")
    try:
        import shap
    except (ModuleNotFoundError, ImportError) as exc:
        return {
            "method": "unavailable",
            "contributions": [],
            "message": f"SHAP could not be loaded ({exc}); no feature-level SHAP claim is made.",
        }
    explainer = shap.Explainer(model, background)
    explanation = explainer(observations)
    values = np.asarray(explanation.values)
    if values.ndim == 3:
        values = values[:, :, 1] if values.shape[2] > 1 else values[:, :, 0]
    if values.ndim == 1:
        values = values.reshape(1, -1)
    contributions = [
        [
            {"feature": name, "value": float(row[name]), "contribution": float(value)}
            for name, value in zip(observations.columns, values[index])
        ]
        for index, (_, row) in enumerate(observations.iterrows())
    ]
    return {
        "method": "SHAP",
        "output_scale": "model-native; interpret with model type",
        "contributions": contributions,
    }


def constrained_counterfactuals(
    model: Any,
    observation: pd.DataFrame,
    feature_bounds: Mapping[str, tuple[float, float]],
    *,
    target_probability: float = 0.25,
    max_suggestions: int = 3,
) -> dict[str, Any]:
    """Probe one-feature changes within supplied plausible ranges."""
    if len(observation) != 1:
        raise ValueError("observation must have exactly one row")
    if not 0 < target_probability < 1 or max_suggestions < 1:
        raise ValueError("target_probability must be in (0, 1) and max_suggestions positive")
    current = observation.copy()
    current_score = float(model.predict_proba(current)[0, 1])
    suggestions = []
    for feature, bounds in feature_bounds.items():
        if feature not in current.columns:
            raise ValueError(f"feature_bounds contains unknown feature {feature!r}")
        lower, upper = map(float, bounds)
        if not np.isfinite([lower, upper]).all() or lower > upper:
            raise ValueError(f"invalid bounds for feature {feature!r}")
        original = float(current.iloc[0][feature])
        candidates = sorted(
            {lower, upper, min(upper, max(lower, (lower + upper) / 2))}
        )
        for candidate in candidates:
            if candidate == original:
                continue
            changed = current.copy()
            changed.loc[:, feature] = candidate
            after = float(model.predict_proba(changed)[0, 1])
            if after < current_score:
                suggestions.append(
                    {
                        "feature": feature,
                        "from": original,
                        "to": candidate,
                        "score_after": after,
                        "score_reduction": current_score - after,
                    }
                )
    suggestions.sort(
        key=lambda item: (-item["score_reduction"], item["feature"], item["to"])
    )
    selected = suggestions[:max_suggestions]
    return {
        "current_score": current_score,
        "target_probability": target_probability,
        "target_reached_by_single_change": any(
            item["score_after"] <= target_probability for item in selected
        ),
        "suggestions": selected,
        "message": (
            "Counterfactuals are model sensitivity scenarios, not causal effects "
            "or recommended interventions."
        ),
    }


def plain_language_risk_explanation(risk: Mapping[str, Any]) -> str:
    """Generate a deterministic, non-AI explanation from risk components."""
    level = str(risk.get("risk_level", "unknown"))
    reasons = risk.get("reasons") or []
    if not reasons:
        reasons = ["There are not enough supplied measurements to explain the score."]
    return f"Current modeled risk is {level}. " + " ".join(str(reason) for reason in reasons)
