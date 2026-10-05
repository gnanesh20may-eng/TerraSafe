"""Optional ONNX export for a fitted scikit-learn-compatible classifier."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Sequence


def export_classifier_to_onnx(
    model: Any,
    feature_names: Sequence[str],
    output_path: Path,
    *,
    target_opset: int = 17,
) -> Path:
    """Convert a fitted lightweight sklearn classifier to a float-input ONNX file."""
    if not feature_names or any(not name for name in feature_names):
        raise ValueError("feature_names must contain non-empty names")
    if output_path.suffix.lower() != ".onnx":
        raise ValueError("output_path must use the .onnx extension")
    if target_opset < 12:
        raise ValueError("target_opset must be at least 12")
    try:
        from skl2onnx import convert_sklearn
        from skl2onnx.common.data_types import FloatTensorType
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "Install ONNX export dependencies with `python -m pip install skl2onnx`."
        ) from exc
    except ImportError as exc:
        raise RuntimeError(f"Unable to load ONNX conversion dependencies: {exc}") from exc

    converted = convert_sklearn(
        model,
        initial_types=[("features", FloatTensorType([None, len(feature_names)]))],
        target_opset=target_opset,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(converted.SerializeToString())
    return output_path
