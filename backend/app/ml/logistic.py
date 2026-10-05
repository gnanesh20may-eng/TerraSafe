"""Small NumPy-only binary logistic regression fallback."""

from __future__ import annotations

from typing import Any

import numpy as np


class NumpyLogisticRegression:
    """Deterministic L2-regularized logistic classifier without native sklearn DLLs."""

    def __init__(
        self,
        *,
        max_iter: int = 1000,
        learning_rate: float = 0.1,
        regularization: float = 1e-3,
        class_weight: str | None = "balanced",
    ) -> None:
        if max_iter < 1 or learning_rate <= 0 or regularization < 0:
            raise ValueError("iteration count, learning rate, or regularization is invalid")
        if class_weight not in {None, "balanced"}:
            raise ValueError("class_weight must be None or 'balanced'")
        self.max_iter = max_iter
        self.learning_rate = learning_rate
        self.regularization = regularization
        self.class_weight = class_weight

    @property
    def named_steps(self) -> dict[str, Any]:
        return {"standardscaler": self, "logisticregression": self}

    def fit(self, features: Any, target: Any) -> NumpyLogisticRegression:
        matrix = np.asarray(features, dtype=float)
        labels = np.asarray(target)
        if matrix.ndim != 2 or matrix.shape[0] != labels.shape[0] or matrix.shape[0] == 0:
            raise ValueError("features and target must have matching non-empty rows")
        if not np.isfinite(matrix).all():
            raise ValueError("features must contain only finite values")
        self.classes_, encoded = np.unique(labels, return_inverse=True)
        if len(self.classes_) != 2:
            raise ValueError("binary logistic regression requires exactly two classes")
        self.mean_ = matrix.mean(axis=0)
        self.scale_ = matrix.std(axis=0)
        self.scale_[self.scale_ == 0] = 1.0
        standardized = (matrix - self.mean_) / self.scale_
        design = np.column_stack((np.ones(len(matrix)), standardized))
        weights = np.ones(len(matrix), dtype=float)
        if self.class_weight == "balanced":
            counts = np.bincount(encoded, minlength=2)
            weights = len(encoded) / (2 * counts[encoded])

        coefficients = np.zeros(design.shape[1], dtype=float)
        total_weight = weights.sum()
        for _ in range(self.max_iter):
            probabilities = _sigmoid(design @ coefficients)
            gradient = design.T @ ((probabilities - encoded) * weights) / total_weight
            gradient[1:] += self.regularization * coefficients[1:]
            update = self.learning_rate * gradient
            coefficients -= update
            if np.linalg.norm(update, ord=2) < 1e-8:
                break

        self.intercept_ = np.asarray([coefficients[0]])
        self.coef_ = coefficients[1:].reshape(1, -1)
        return self

    def predict_proba(self, features: Any) -> np.ndarray:
        if not hasattr(self, "coef_"):
            raise ValueError("model must be fitted before prediction")
        matrix = np.asarray(features, dtype=float)
        if matrix.ndim != 2 or matrix.shape[1] != self.coef_.shape[1]:
            raise ValueError("features must have the same number of columns as training data")
        if not np.isfinite(matrix).all():
            raise ValueError("features must contain only finite values")
        standardized = (matrix - self.mean_) / self.scale_
        positive = _sigmoid(standardized @ self.coef_[0] + self.intercept_[0])
        return np.column_stack((1 - positive, positive))


def _sigmoid(values: np.ndarray) -> np.ndarray:
    clipped = np.clip(values, -40, 40)
    return 1 / (1 + np.exp(-clipped))
