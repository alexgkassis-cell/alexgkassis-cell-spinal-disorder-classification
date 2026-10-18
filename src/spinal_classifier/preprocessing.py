"""Exact Stage 3F/4 grayscale+CLAHE preprocessing for locked C08.

Do not change operation order: EXIF transpose, RGB conversion, LANCZOS pad,
OpenCV RGB-to-gray conversion, CLAHE, float32 scaling, channel append.
"""
from pathlib import Path
import numpy as np
import cv2
from PIL import Image, ImageOps


def preprocess_locked_c08(path: str | Path) -> np.ndarray:
    """Return a 128 x 128 x 1 float32 image in [0, 1] for the locked model."""
    with Image.open(path) as opened:
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
