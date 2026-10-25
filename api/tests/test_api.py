"""Offline API tests with an intentionally fake model, never a fake website result."""
from io import BytesIO
import numpy as np
from PIL import Image
from fastapi.testclient import TestClient
from api.main import create_app


class FakeModel:
    def __call__(self, image, training=False):
        assert image.shape == (1, 128, 128, 1)
        assert image.dtype == np.float32
        assert 0 <= image.min() <= image.max() <= 1
        return np.array([[0.1, 0.8, 0.1]], dtype=np.float32)


def synthetic_png():
    image = Image.new("RGB", (240, 180), (82, 92, 103))
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def test_health_without_checkpoint():
    with TestClient(create_app()) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["model_loaded"] is False
        assert response.headers["Cache-Control"] == "no-store"
        unavailable = client.post("/predict", content=synthetic_png(), headers={"content-type": "image/png"})
        assert unavailable.status_code == 503


def test_predict_in_memory():
    with TestClient(create_app(model_override=FakeModel())) as client:
        reply = client.post("/predict", content=synthetic_png(), headers={"content-type": "image/png"})
        assert reply.status_code == 200, reply.text
        assert reply.json()["label"] == "Scoliosis"
        assert reply.json()["research_only"] is True
        assert "scan.png" not in reply.text
        assert reply.json()["scores"]["Scoliosis"] > 0.79


def test_invalid_file_type():
    with TestClient(create_app(model_override=FakeModel())) as client:
        response = client.post("/predict", content=b"hello", headers={"content-type": "text/plain"})
        assert response.status_code == 415


def test_truncated_image():
    with TestClient(create_app(model_override=FakeModel())) as client:
        response = client.post("/predict", content=b"not a jpeg", headers={"content-type": "image/jpeg"})
        assert response.status_code == 422


def test_too_large():
    with TestClient(create_app(model_override=FakeModel())) as client:
        response = client.post("/predict", content=b"a" * (8 * 1024 * 1024 + 1), headers={"content-type": "image/png"})
        assert response.status_code == 413


def test_production_bearer_auth(monkeypatch):
    token = "a-mock-server-secret-with-sufficient-length-000000000000"
    monkeypatch.setenv("SPINAL_REQUIRE_TOKEN", "1")
    monkeypatch.setenv("SPINAL_API_TOKEN", token)
    with TestClient(create_app(model_override=FakeModel())) as client:
        no_auth = client.post("/predict", content=synthetic_png(), headers={"content-type": "image/png"})
        assert no_auth.status_code == 401
        wrong = client.post("/predict", content=synthetic_png(), headers={"content-type": "image/png", "Authorization": "Bearer incorrect"})
        assert wrong.status_code == 401
        authorized = client.post("/predict", content=synthetic_png(), headers={"content-type": "image/png", "Authorization": f"Bearer {token}"})
        assert authorized.status_code == 200
        assert authorized.json()["label"] == "Scoliosis"


def test_production_requires_strong_token(monkeypatch):
    import pytest
    monkeypatch.setenv("SPINAL_REQUIRE_TOKEN", "1")
    monkeypatch.setenv("SPINAL_API_TOKEN", "weak")
    with pytest.raises(RuntimeError, match=r"32\+ characters"):
        with TestClient(create_app(model_override=FakeModel())):
            pass
