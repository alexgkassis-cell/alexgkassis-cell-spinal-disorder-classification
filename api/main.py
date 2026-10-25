"""FastAPI service for the single *locked* C08 checkpoint.

All uploaded bytes remain in memory. The service deliberately does not save,
cache, log, or return images or filenames. Never expose directly to the public
without HTTPS, authentication, rate limiting, and privacy review.
"""
from __future__ import annotations

from contextlib import asynccontextmanager
import hashlib
import os
from pathlib import Path
from threading import Lock
import secrets
from typing import Any

import numpy as np
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from spinal_classifier.preprocessing import preprocess_locked_c08_bytes

MAX_FILE_BYTES = 8 * 1024 * 1024
LABELS = ("Normal", "Scoliosis", "Spondylolisthesis")
DISCLAIMER = "Educational research output only. Not a diagnosis or a medical device. Model scores are not calibrated probabilities."


def load_locked_checkpoint() -> Any | None:
    """Only load a locally configured, trusted checkpoint; never user-supplied."""
    raw_path = os.environ.get("SPINAL_MODEL_PATH", "").strip()
    if not raw_path:
        return None
    model_path = Path(raw_path).expanduser()
    if not model_path.is_file():
        raise RuntimeError("SPINAL_MODEL_PATH does not exist")

    expected_sha = os.environ.get("SPINAL_MODEL_SHA256", "").strip().lower()
    if expected_sha:
        actual_sha = hashlib.sha256(model_path.read_bytes()).hexdigest()
        if actual_sha != expected_sha:
            raise RuntimeError("Model SHA-256 differs from the original private Stage 4 lock")

    try:
        import tensorflow as tf
    except ImportError as exc:
        raise RuntimeError("Install the project with the [inference] extra") from exc

    # File comes only from the trusted private checkpoint produced by Stage 3F.
    model = tf.keras.models.load_model(str(model_path), compile=False, safe_mode=True)
    if tuple(model.input_shape[1:]) != (128, 128, 1):
        raise RuntimeError("Checkpoint input shape is not the locked C08 shape")
    if tuple(model.output_shape[1:]) != (3,):
        raise RuntimeError("Checkpoint output shape is not three classes")
    if model.count_params() != 4_287_491:
        raise RuntimeError("Checkpoint parameter count is not the locked C08 architecture")
    return model


def create_app(model_override: Any | None = None) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Production: require a strong shared server-to-server token even if
        # inference is temporarily disabled while the private model is uploaded.
        require_auth = os.environ.get("SPINAL_REQUIRE_TOKEN", "0") == "1"
        token = os.environ.get("SPINAL_API_TOKEN", "")
        if require_auth and len(token) < 32:
            raise RuntimeError("Production requires SPINAL_API_TOKEN (32+ characters)")
        app.state.model = model_override if model_override is not None else load_locked_checkpoint()
        app.state.prediction_lock = Lock()
        yield
        app.state.model = None

    app = FastAPI(
        title="SpineLab local research API", version="1.0.0",
        docs_url=None, redoc_url=None, openapi_url=None,
        lifespan=lifespan,
    )

    @app.middleware("http")
    async def add_privacy_headers(request, call_next):
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        return response

    @app.get("/health")
    def health():
        return {
            "status": "ready" if app.state.model is not None else "model_unavailable",
            "model_loaded": app.state.model is not None,
            "candidate": "C08", "model_seed": 456,
            "research_only": True,
        }

    @app.post("/predict")
    async def predict(request: Request):
        # Authenticate before consuming any image bytes. Next.js stores the
        # token server-side; no browser or GitHub file ever receives it.
        configured_token = os.environ.get("SPINAL_API_TOKEN", "")
        require_auth = os.environ.get("SPINAL_REQUIRE_TOKEN", "0") == "1"
        if require_auth or configured_token:
            supplied_auth = request.headers.get("authorization", "")
            expected_auth = f"Bearer {configured_token}"
            if not configured_token or not secrets.compare_digest(supplied_auth, expected_auth):
                raise HTTPException(status_code=401, detail="Unauthorized inference request")
        model = app.state.model
        if model is None:
            raise HTTPException(status_code=503, detail="Private C08 checkpoint is not configured on the API server")
        # Binary image body, not multipart: FastAPI never spools sensitive images to disk.
        content_type = request.headers.get("content-type", "").split(";")[0].strip().lower()
        if content_type not in ("image/jpeg", "image/png"):
            raise HTTPException(status_code=415, detail="Upload a JPEG or PNG image")
        raw_length = request.headers.get("content-length")
        if raw_length and int(raw_length) > MAX_FILE_BYTES:
            raise HTTPException(status_code=413, detail="Image must be between 1 byte and 8 MiB")
        data_parts = []
        total = 0
        async for part in request.stream():
            total += len(part)
            if total > MAX_FILE_BYTES:
                raise HTTPException(status_code=413, detail="Image must be between 1 byte and 8 MiB")
            data_parts.append(part)
        if total == 0:
            raise HTTPException(status_code=413, detail="Image must be between 1 byte and 8 MiB")
        data = b"".join(data_parts)
        try:
            array = preprocess_locked_c08_bytes(data)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        except Exception as exc:
            raise HTTPException(status_code=422, detail="Cannot decode this image") from exc

        with app.state.prediction_lock:
            # Direct call avoids Keras predict's data-loader overhead for one image.
            output = model(array[None, ...], training=False)
            if hasattr(output, "numpy"):
                output = output.numpy()
        scores = np.asarray(output, dtype=np.float64)
        if scores.shape != (1, 3) or not np.isfinite(scores).all():
            raise HTTPException(status_code=500, detail="Model output validation failed")
        vector = scores[0]
        if np.any(vector < 0) or not np.isclose(vector.sum(), 1.0, atol=1e-4):
            raise HTTPException(status_code=500, detail="Model output validation failed")
        probabilities = {name: float(value) for name, value in zip(LABELS, vector)}
        return {
            "label": LABELS[int(np.argmax(vector))],
            "scores": probabilities,
            "preprocessing": "128x128 grayscale + CLAHE (clip 3.0; tiles 8x8)",
            "model": "C08 / seed 456 / epoch 11",
            "research_only": True,
            "notice": DISCLAIMER,
        }

    return app


app = create_app()
