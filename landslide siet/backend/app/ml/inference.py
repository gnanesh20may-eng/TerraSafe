from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from backend.app.ml.physics import infinite_slope_factor, rainfall_id_trigger
from backend.app.ml.susceptibility import _model_factories
from backend.app.ml.synthetic_data import FEATURE_COLUMNS, generate_nilgiris_pilot

LOGGER = logging.getLogger(__name__)
MODEL_PATH = Path(__file__).resolve().parents[2] / "models" / "susceptibility.joblib"


class SusceptibilityInference:
    def __init__(self, model_path: Path = MODEL_PATH):
        self.model_path = model_path
        self._model: Any | None = None
        self.model_status = "SCAFFOLD"

    def _load_model(self):
        if self._model is not None:
            return self._model
        if self.model_path.exists():
            try:
                import joblib

                self._model = joblib.load(self.model_path)
                self.model_status = "EXPORTED_MODEL"
                return self._model
            except Exception as exc:
                LOGGER.warning("Could not load exported model; using synthetic logistic fallback: %s", exc)
        pilot = generate_nilgiris_pilot(grid_size=24, seed=42)
        self._model = _model_factories(42)["LogisticRegression"]()
        self._model.fit(pilot.cells.loc[:, FEATURE_COLUMNS], pilot.cells["landslide_label"])
        self.model_status = "DEMO_SYNTHETIC_LOGISTIC"
        return self._model

    def predict(self, values: dict[str, float]) -> dict[str, Any]:
        missing = sorted(set(FEATURE_COLUMNS) - set(values))
        if missing:
            raise ValueError(f"missing model features: {', '.join(missing)}")
        row = pd.DataFrame([{column: values[column] for column in FEATURE_COLUMNS}])
        model = self._load_model()
        probability = float(model.predict_proba(row)[0, 1])
        try:
            classifier = model.named_steps["logisticregression"]
            scaled = model.named_steps["standardscaler"].transform(row)[0]
            contributions = np.abs(scaled * classifier.coef_[0])
            top_factors = [FEATURE_COLUMNS[index] for index in np.argsort(contributions)[::-1][:3]]
        except (AttributeError, KeyError):
            top_factors = ["model features"]

        slope = min(89.0, max(0.1, float(values["slope_deg"])))
        cohesion = max(0.1, float(values["soil_clay_fraction"]) * 10)
        rain = max(0.0, float(values.get("rainfall_24h_mm", 0.0)))
        safety_factor = infinite_slope_factor(slope, cohesion, 18.0, 1.5, 30.0, min(1.0, rain / 200))
        physics_risk = min(1.0, max(0.0, 1.5 - safety_factor))
        rainfall_trigger = rainfall_id_trigger(rain, 24.0, 1.0)
        hybrid_probability = min(1.0, max(0.0, 0.6 * probability + 0.2 * physics_risk + 0.2 * rainfall_trigger["normalized_trigger"]))
        return {
            "probability": probability,
            "hybrid_probability": hybrid_probability,
            "model_status": self.model_status,
            "uncertainty_band": {
                "lower": max(0.0, hybrid_probability - 0.15),
                "upper": min(1.0, hybrid_probability + 0.15),
                "status": "PLACEHOLDER: fixed-width band; no conformal model is loaded",
            },
            "physics": {"infinite_slope_factor_of_safety": safety_factor, "status": "ILLUSTRATIVE; not geotechnically calibrated"},
            "rainfall_trigger": rainfall_trigger,
            "top_factors": top_factors,
            "why": f"The demonstration score is influenced most by {', '.join(top_factors)}; verify local conditions and official guidance.",
            "model_disagreement": abs(hybrid_probability - probability) >= 0.25,
            "synthetic_training_data": self.model_status == "DEMO_SYNTHETIC_LOGISTIC",
        }