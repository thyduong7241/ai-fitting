import io
import pytest
from fastapi.testclient import TestClient
from app.main import app
from benchmark.datasets.generate_fixtures import create_synthetic_person_image


client = TestClient(app)


def test_measure_endpoint_multipart():
    import cv2
    img = create_synthetic_person_image()
    _, encoded = cv2.imencode(".jpg", img)

    files = {
        "front_image": ("front.jpg", io.BytesIO(encoded.tobytes()), "image/jpeg"),
    }
    data = {
        "height_cm": "175.0",
        "weight_kg": "68.0",
        "age": "28",
        "gender": "male",
    }
    resp = client.post("/api/v1/measure", files=files, data=data)
    assert resp.status_code == 200
    res_json = resp.json()

    assert "measurements" in res_json
    measurements = res_json["measurements"]
    assert measurements["heightCm"] == 175.0
    assert measurements["weightKg"] == 68.0
    assert measurements["shoulderCm"] is not None
    assert measurements["chestCm"] is not None
    assert measurements["waistCm"] is not None
    assert measurements["hipsCm"] is not None
    assert "bodyShape" in res_json
    assert "smartFitNotes" in res_json
    assert len(res_json["smartFitNotes"]) > 0
