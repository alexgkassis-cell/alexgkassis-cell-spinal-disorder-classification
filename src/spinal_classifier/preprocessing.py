"""Exact frozen C08 preprocessing for both CLI and web uploads.

Keep these steps and their order unchanged: EXIF transpose, RGB conversion,
LANCZOS pad to 128x128, RGB-to-gray, CLAHE clip 3.0 / 8x8, float32 / 255.
"""
from __future__ import annotations
from io import BytesIO
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageOps, UnidentifiedImageError

MAX_IMAGE_PIXELS = 12_000_000
ALLOWED_IMAGE_FORMATS = {"JPEG", "PNG"}


def _preprocess_open_image(opened: Image.Image) -> np.ndarray:
    rgb_image = ImageOps.exif_transpose(opened).convert("RGB")
    resized = ImageOps.pad(
        rgb_image, (128, 128), method=Image.Resampling.LANCZOS,
        color=(0, 0, 0),
    )
    rgb = np.asarray(resized, dtype=np.uint8)
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    enhanced = cv2.createCLAHE(
        clipLimit=3.0, tileGridSize=(8, 8)
    ).apply(gray)
    return enhanced[..., None].astype(np.float32) / 255.0


def _validate_image(opened: Image.Image) -> None:
    if opened.format not in ALLOWED_IMAGE_FORMATS:
        raise ValueError("Only actual JPEG and PNG images are supported")
    width, height = opened.size
    if width < 1 or height < 1 or width * height > MAX_IMAGE_PIXELS:
        raise ValueError("Image resolution is too large")


def preprocess_locked_c08(path: str | Path) -> np.ndarray:
    """For authorized local images (same operation sequence as Stage 4)."""
    with Image.open(path) as opened:
        return _preprocess_open_image(opened)


def preprocess_locked_c08_bytes(data: bytes) -> np.ndarray:
    """For memory-only web inference; validate format/size then preprocess."""
    try:
        with Image.open(BytesIO(data)) as opened:
            _validate_image(opened)
            return _preprocess_open_image(opened)
    except (UnidentifiedImageError, OSError) as exc:
        raise ValueError("The uploaded file is not a readable JPEG or PNG") from exc
