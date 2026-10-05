from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd

from backend.app.ml.model_disagreement import assess_model_disagreement
from backend.app.ml.physics import infinite_slope_factor_of_safety
from backend.app.ml.synthetic_data import FEATURE_COLUMNS, generate_nilgiris_pilot

BACKEND_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MODEL_PATH = BACKEND_ROOT / "models" / "susceptibility.joblib"
PHYSICS_FIELDS = (
    "cohesion_kpa",
    "unit_weight_kn_m3",
    "soil_depth_m",
    "friction_angle_deg",
    "saturation_ratio",
)


class InferenceEngine:
    def __init__(self, model_path: Path | None = None, allow_demo_fallback: bool = True) -> None:
        self.model_path = model_path or DEFAULT_MODEL_PATH
        self.model_bundle: dict[str, Any] | None = None
        self.model: Any
        self.model_name: str
        self.feature_columns = tuple(FEATURE_COLUMNS)
        self.status: str
        self.synthetic: bool

        if self.model_path.is_file():
            loaded = joblib.load(self.model_path)
            if isinstance(loaded, dict) and "model" in loaded:
                self.model_bundle = loaded
                self.model = loaded["model"]
                self.feature_columns = tuple(loaded.get("feature_columns", FEATURE_COLUMNS))
                self.model_name = str(loaded.get("model_name", type(self.model).__name__))
                self.synthetic = bool(loaded.get("synthetic", False))
                self.status = "DEMO MODEL ARTIFACT" if self.synthetic else "EXPORTED MODEL"
            else:
                self.model = loaded
                self.model_name = type(loaded).__name__
                self.synthetic = False
                self.status = "EXPORTED MODEL — provenance metadata unavailable"
        elif allow_demo_fallback:
            self.model, self.model_bundle = self._fit_synthetic_logistic()
            self.model_name = "LogisticRegression"
            self.synthetic = True
            self.status = "DEMO — LogisticRegression fit on synthetic labels"
        else:
            raise FileNotFoundError(f"No exported model found at {self.model_path}")

    @staticmethod
    def _fit_synthetic_logistic() -> tuple[Any, dict[str, Any]]:
        from sklearn.linear_model import LogisticRegression
        from sklearn.pipeline import make_pipeline
        from sklearn.preprocessing import StandardScaler

        pilot = generate_nilgiris_pilot(grid_size=16, seed=42)
        model = make_pipeline(
            StandardScaler(),
            LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42),
        )
        model.fit(pilot.cells.loc[:, FEATURE_COLUMNS], pilot.cells["landslide_label"])
        return model, {
            "model": model,
            "model_name": "LogisticRegression",
            "feature_columns": list(FEATURE_COLUMNS),
            "synthetic": True,
            "data_source": pilot.source_label,
        }

    def predict(self, features: dict[str, float]) -> dict[str, Any]:
        missing = [name for name in self.feature_columns if name not in features]
        if missing:
            raise ValueError(f"missing model features: {', '.join(missing)}")
        values = [float(features[name]) for name in self.feature_columns]
        if not all(math.isfinite(value) for value in values):
            raise ValueError("model features must be finite numeric values")
        frame = pd.DataFrame([dict(zip(self.feature_columns, values))], columns=self.feature_columns)
        probability = float(self.model.predict_proba(frame)[0][1])
        if not math.isfinite(probability) or not 0 <= probability <= 1:
            raise ValueError("model returned an invalid probability")

        contributors = self._explain_linear_prediction(frame)
        if contributors:
            main_factor = contributors[0]["factor"].replace("_", " ")
            why = f"The model output is most influenced by {main_factor}; this is an association in the fitted model, not a causal finding."
        else:
            why = "Per-instance explanation is unavailable for this model adapter; do not infer causality from the score."

        component_models = (self.model_bundle or {}).get("models", {})
        component_probabilities = {
            name: float(component.predict_proba(frame)[0][1])
            for name, component in component_models.items()
        }
        if self.model_name not in component_probabilities:
            component_probabilities[self.model_name] = probability

        physics = self._physics_result(features)
        return {
            "probability": probability,
            "score": round(probability * 100, 1),
            "model": self.model_name,
            "status": self.status,
            "synthetic": self.synthetic,
            "uncertainty": {
                "available": False,
                "lower": None,
                "upper": None,
                "label": "PLACEHOLDER — no conformal uncertainty model is loaded",
            },
            "contributors": contributors,
            "explanation_method": "LogisticRegression coefficients; not SHAP",
            "why": why,
            "physics": physics,
            "hybrid_score": {
                "available": False,
                "status": "SCAFFOLD — calibration parameters are required",
            },
            "model_disagreement": assess_model_disagreement(component_probabilities),
        }

    def _explain_linear_prediction(self, frame: pd.DataFrame) -> list[dict[str, Any]]:
        named_steps = getattr(self.model, "named_steps", {})
        estimator = list(named_steps.values())[-1] if named_steps else self.model
        coefficients = getattr(estimator, "coef_", None)
        if coefficients is None:
            return []
        transformed = frame
        if named_steps:
            transformer_steps = list(named_steps.values())[:-1]
            for transformer in transformer_steps:
                if hasattr(transformer, "transform"):
                    transformed = transformer.transform(transformed)
        contributions = np.asarray(coefficients)[0] * np.asarray(transformed)[0]
        order = np.argsort(np.abs(contributions))[::-1][:4]
        return [
            {
                "factor": self.feature_columns[index],
                "contribution": float(contributions[index]),
                "direction": "INCREASE" if contributions[index] > 0 else "DECREASE",
                "method": "linear coefficient contribution",
            }
            for index in order
        ]

    @staticmethod
    def _physics_result(features: dict[str, float]) -> dict[str, Any]:
        if not all(field in features for field in PHYSICS_FIELDS) or "slope_deg" not in features:
            return {"available": False, "status": "SCAFFOLD — measured soil parameters are missing"}
        try:
            factor = infinite_slope_factor_of_safety(
                slope_deg=float(features["slope_deg"]),
                cohesion_kpa=float(features["cohesion_kpa"]),
                unit_weight_kn_m3=float(features["unit_weight_kn_m3"]),
                soil_depth_m=float(features["soil_depth_m"]),
                friction_angle_deg=float(features["friction_angle_deg"]),
                saturation_ratio=float(features["saturation_ratio"]),
            )
        except (TypeError, ValueError) as error:
            return {"available": False, "status": "INVALID INPUT", "error": str(error)}
        return {
            "available": True,
            "factor_of_safety": factor,
            "status": "SIMULATED physics calculation; soil parameters require site measurement",
        }


inference_engine = InferenceEngine()
