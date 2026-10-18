# Reproducibility guide

The notebooks are cleaned copies of the actual Colab source (outputs removed); they are not automatically runnable without authorization to the original private Google Drive data and private model checkpoints.

## Environment

- Observed Colab: TensorFlow **2.21.0**, OpenCV **5.0.0**, CPU-only in recorded runs.
- Python 3.10+ for packaged source/tests. Keras / TensorFlow version changes can affect training determinism and .keras load behavior.
- Avoid claiming identical seed means bit-identical behavior across CUDA, CPU, operating systems and different library versions.

## Exact preprocessing — the final locked C08

1. Open an image with Pillow, honor EXIF orientation and convert to RGB.
2. Pad/resize to **128×128** with `ImageOps.pad(..., method=Image.Resampling.LANCZOS, color=(0,0,0))`.
3. Convert RGB pixels to grayscale with `cv2.COLOR_RGB2GRAY`.
4. Apply `cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8)).apply(gray)`.
5. Convert to float32, divide by 255 and append a single channel (`128×128×1`).

**Do not use a generic PIL grayscale-resize pipeline**; it is not an exact match to this locked experiment. Source helper: [`../src/spinal_classifier/preprocessing.py`](../src/spinal_classifier/preprocessing.py).

## Models and checkpoints

Reference topology: Conv2D(32) → MaxPool → Conv2D(64) → MaxPool → Conv2D(128) → MaxPool → Flatten → Dense(128) → Dense(3 softmax); **4,287,491** trainable/total parameters at 128×128×1 input.

Training used Adam (3e-4), balanced class weights from training labels, batch size 16, max 40 epochs, ReduceLROnPlateau, EarlyStopping with val_loss patience 9. Stage 3F stored both loss- and accuracy-selected `.keras` archives. Locked choice: C08, seed 456, best-accuracy epoch 11 (tie broken by val_loss).

## Reproducing the final result vs rerunning the final test

For scientific integrity, reproduce training only with the original frozen split (readable only with authorized data) or use a new appropriately patient-disjoint/external dataset for new validation. **The published 51-image held-out test has already been used exactly once for model evaluation; it is not a fresh test for subsequent tuning.** The Stage 4 notebook remains as an auditable source record, not an invitation to rerank models.

Our public JSON contains only aggregate results. A private selection lock, checkpoints, hashed manifest and per-image scores remain in Google Drive and are intentionally excluded.
