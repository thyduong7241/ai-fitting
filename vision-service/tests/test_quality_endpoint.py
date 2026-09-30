import io
import pytest
from fastapi.testclient import TestClient
from app.main import app
from benchmark.datasets.generate_fixtures import create_synthetic_person_image


client = TestClient(app)


def test_health_check_endpoint():
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert data["service"] == "vision-service"


def test_quality_check_endpoint_multipart():
    import cv2
    img = create_synthetic_person_image()
    _, encoded = cv2.imencode(".jpg", img)

    files = {"image": ("test.jpg", io.BytesIO(encoded.tobytes()), "image/jpeg")}
    resp = client.post("/api/v1/quality-check", files=files, data={"image_type": "front"})
    assert resp.status_code == 200
    data = resp.json()
    assert "isValid" in data
    assert "confidenceScore" in data
    assert "blurScore" in data
