from io import BytesIO
import numpy as np
from PIL import Image
from spinal_classifier.preprocessing import preprocess_locked_c08, preprocess_locked_c08_bytes


def test_file_and_bytes_preprocessing_identical(tmp_path):
    rng = np.random.default_rng(123)
    pixels = rng.integers(0, 256, size=(160, 220, 3), dtype=np.uint8)
    image = Image.fromarray(pixels, mode="RGB")
    buffer = BytesIO()
    image.save(buffer, format="JPEG")
    raw = buffer.getvalue()
    source = tmp_path / "synthetic.jpg"
    source.write_bytes(raw)
    from_file = preprocess_locked_c08(source)
    from_bytes = preprocess_locked_c08_bytes(raw)
    np.testing.assert_array_equal(from_file, from_bytes)
    assert from_file.shape == (128, 128, 1)
