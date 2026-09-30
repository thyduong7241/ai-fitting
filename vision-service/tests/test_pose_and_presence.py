import pytest
import numpy as np
from app.core.mediapipe_detector import MediaPipePoseDetector
from app.services.quality_gate import evaluate_quality


def test_detector_singleton():
    d1 = MediaPipePoseDetector()
    d2 = MediaPipePoseDetector()
    assert d1 is d2


def test_no_person_detection():
    # Empty plain image without person
    blank_img = np.full((1000, 700, 3), 200, dtype=np.uint8)
    import cv2
    _, encoded = cv2.imencode(".jpg", blank_img)
    
    resp = evaluate_quality(encoded.tobytes(), image_type="front")
    assert resp.is_valid is False
    assert any(iss.code == "no_person" for iss in resp.issues)


def test_low_resolution_gate():
    # Tiny thumbnail 400x300
    tiny_img = np.zeros((400, 300, 3), dtype=np.uint8)
    import cv2
    _, encoded = cv2.imencode(".jpg", tiny_img)

    resp = evaluate_quality(encoded.tobytes(), image_type="front")
    assert resp.is_valid is False
    assert any(iss.code == "low_resolution" for iss in resp.issues)
