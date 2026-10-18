import pytest


def test_reference_architecture_when_tensorflow_available():
    tf = pytest.importorskip('tensorflow')
    from spinal_classifier.architecture import make_reference_cnn
    model = make_reference_cnn()
    assert model.count_params() == 4_287_491
    assert tuple(model.input_shape[1:]) == (128, 128, 1)
    assert tuple(model.output_shape[1:]) == (3,)
