import pytest
from app.models.vision import (
    QualityCheckRequest,
    QualityCheckResponse,
    QualityIssue,
    MeasurementRequest,
    MeasurementResponse,
    BodyMeasurements,
    EngineMetadata,
)


def test_quality_check_models():
    issue = QualityIssue(
        code="blurry",
        severity="error",
        message="Ảnh bị mờ rung tay",
        box=[0.1, 0.2, 0.8, 0.9],
    )
    assert issue.code == "blurry"
    assert issue.severity == "error"

    resp = QualityCheckResponse(
        isValid=False,
        confidenceScore=0.45,
        issues=[issue],
        blurScore=65.2,
        landmarksDetected=30,
        engineId="opencv_mediapipe",
    )
    assert resp.is_valid is False
    assert resp.confidence_score == 0.45
    assert len(resp.issues) == 1
    assert resp.engine_id == "opencv_mediapipe"
    # Test camelCase serialization
    data = resp.model_dump(by_alias=True)
    assert "isValid" in data
    assert "confidenceScore" in data
    assert "blurScore" in data


def test_measurement_models():
    measurements = BodyMeasurements(
        heightCm=175.0,
        weightKg=68.0,
        shoulderCm=43.5,
        chestCm=94.0,
        waistCm=78.0,
        hipsCm=95.0,
        armLengthCm=60.0,
        inseamCm=77.0,
    )
    assert measurements.height_cm == 175.0
    assert measurements.chest_cm == 94.0

    resp = MeasurementResponse(
        measurements=measurements,
        confidencePercent=92.5,
        method="hybrid_stereometry_2d",
        bodyShape="dong_ho_cat",
        smartFitNotes=["Ngực đầy đặn, eo thon"],
        engineId="hybrid_stereometry_2d",
    )
    assert resp.confidence_percent == 92.5
    assert resp.body_shape == "dong_ho_cat"
    assert len(resp.smart_fit_notes) == 1

    data = resp.model_dump(by_alias=True)
    assert "confidencePercent" in data
    assert "bodyShape" in data
    assert "smartFitNotes" in data


def test_engine_metadata():
    meta = EngineMetadata(
        engineId="hybrid_stereometry_2d",
        name="Hybrid 2-View Stereometry",
        engineType="measurement",
        description="2-view anthropometric measurement",
        requiresGpu=False,
        status="active",
    )
    assert meta.engine_id == "hybrid_stereometry_2d"
    assert meta.requires_gpu is False
