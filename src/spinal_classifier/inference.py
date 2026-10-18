"""Run a *research-only* local prediction with a PRIVATE trusted C08 model.

Do not load arbitrary/untrusted .keras files; loading ML archives may execute code.
Nothing is uploaded or written to disk by this CLI.
"""
import argparse
import json
from pathlib import Path
import numpy as np
from .preprocessing import preprocess_locked_c08

LABELS = ("Normal", "Scoliosis", "Spondylolisthesis")


def predict_one(image_path: str | Path, model_path: str | Path) -> dict:
    try:
        import tensorflow as tf
    except ImportError as exc:
        raise RuntimeError("Install TensorFlow: pip install -e '.[inference]'") from exc
    model = tf.keras.models.load_model(str(model_path), compile=False)
    if tuple(model.input_shape[1:]) != (128, 128, 1) or tuple(model.output_shape[1:]) != (3,):
        raise ValueError("Unexpected model input/output shape; refusing to predict")
    if model.count_params() != 4_287_491:
        raise ValueError("Unexpected model architecture/parameter count")
    sample = preprocess_locked_c08(image_path)
    scores = np.asarray(model.predict(sample[None, ...], verbose=0)[0], dtype=float)
    if scores.shape != (3,) or not np.isfinite(scores).all() or not np.isclose(scores.sum(), 1, atol=1e-4):
        raise ValueError("Unexpected model output")
    return {
        "experimental_label": LABELS[int(np.argmax(scores))],
        "scores_not_calibrated": {label: float(p) for label, p in zip(LABELS, scores)},
        "warning": "Research-only prediction, not a diagnosis. Not clinically validated.",
    }


def main():
    parser = argparse.ArgumentParser(description="Non-diagnostic C08 local image classification")
    parser.add_argument("--model", required=True, type=Path, help="Private trusted .keras checkpoint")
    parser.add_argument("--image", required=True, type=Path, help="Locally authorized X-ray file")
    args = parser.parse_args()
    print(json.dumps(predict_one(args.image, args.model), indent=2))


if __name__ == "__main__":
    main()
