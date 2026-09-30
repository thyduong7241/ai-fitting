import pytest
import numpy as np
from app.services.quality_gate import evaluate_quality
from benchmark.datasets.generate_fixtures import create_synthetic_person_image


def test_head_cut_off_detection():
    import cv2
    img = create_synthetic_person_image(cut_head=True)
    _, encoded = cv2.imencode(".jpg", img)

    resp = evaluate_quality(encoded.tobytes(), image_type="front")
    assert resp.is_valid is False
    assert any(iss.code == "head_cut_off" for iss in resp.issues)
    head_issue = next(iss for iss in resp.issues if iss.code == "head_cut_off")
    assert head_issue.box is not None


def test_feet_cut_off_detection():
    import cv2
    img = create_synthetic_person_image(cut_feet=True)
    _, encoded = cv2.imencode(".jpg", img)

    resp = evaluate_quality(encoded.tobytes(), image_type="front")
    assert resp.is_valid is False
    assert any(iss.code == "feet_cut_off" for iss in resp.issues)
    feet_issue = next(iss for iss in resp.issues if iss.code == "feet_cut_off")
    assert feet_issue.box is not None
