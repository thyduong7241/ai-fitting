import pytest
import numpy as np
from app.services.quality_gate import evaluate_quality
from benchmark.datasets.generate_fixtures import create_synthetic_person_image


def test_blurry_detection():
    import cv2
    img = create_synthetic_person_image(blur=True)
    _, encoded = cv2.imencode(".jpg", img)

    resp = evaluate_quality(encoded.tobytes(), image_type="front")
    assert resp.is_valid is False
    assert any(iss.code == "blurry" for iss in resp.issues)
    assert resp.blur_score < 75.0


def test_bad_lighting_detection():
    import cv2
    dark_img = create_synthetic_person_image(dark=True)
    _, encoded_dark = cv2.imencode(".jpg", dark_img)
    resp_dark = evaluate_quality(encoded_dark.tobytes(), image_type="front")
    assert resp_dark.is_valid is False
    assert any(iss.code == "bad_lighting" for iss in resp_dark.issues)

    bright_img = create_synthetic_person_image(overexposed=True)
    _, encoded_bright = cv2.imencode(".jpg", bright_img)
    resp_bright = evaluate_quality(encoded_bright.tobytes(), image_type="front")
    assert resp_bright.is_valid is False
    assert any(iss.code == "bad_lighting" for iss in resp_bright.issues)


def test_valid_image():
    import cv2
    img = create_synthetic_person_image()
    _, encoded = cv2.imencode(".jpg", img)

    resp = evaluate_quality(encoded.tobytes(), image_type="front")
    assert resp.is_valid is True
    assert len(resp.issues) == 0
    assert resp.confidence_score >= 0.90
    assert resp.blur_score >= 75.0
