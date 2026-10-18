import numpy as np
from PIL import Image, ImageOps
import cv2
from spinal_classifier.preprocessing import preprocess_locked_c08


def test_locked_pipeline_matches_independent_reference(tmp_path):
    # All pixel data are artificially generated in-memory; no medical images.
    y, x = np.mgrid[0:70, 0:96]
    synthetic = np.stack(((x * 2 + y) % 256, (x + y * 3) % 256,
                          (x * 4 + y * 7) % 256), axis=-1).astype(np.uint8)
    src = tmp_path / "synthetic.bmp"
    Image.fromarray(synthetic, "RGB").save(src)

    got = preprocess_locked_c08(src)
    with Image.open(src) as f:
        ref_rgb = ImageOps.pad(ImageOps.exif_transpose(f).convert('RGB'), (128, 128),
                               method=Image.Resampling.LANCZOS, color=(0, 0, 0))
    expected_gray = cv2.cvtColor(np.asarray(ref_rgb, dtype=np.uint8), cv2.COLOR_RGB2GRAY)
    expected = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8)).apply(expected_gray)
    np.testing.assert_array_equal(got, expected[..., None].astype(np.float32) / 255.0)
    assert got.shape == (128, 128, 1)
    assert got.dtype == np.float32
    assert 0 <= got.min() <= got.max() <= 1


def test_deterministic_preprocessing(tmp_path):
    src = tmp_path / 'test.png'
    Image.fromarray(np.full((40, 80, 3), 110, dtype=np.uint8), 'RGB').save(src)
    np.testing.assert_array_equal(preprocess_locked_c08(src), preprocess_locked_c08(src))
