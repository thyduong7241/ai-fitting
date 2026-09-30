import pytest
from app.services.anthropometric_service import fallback_bmi_measurements
from app.models.fitting import MeasurementResponse


def test_fallback_bmi_measurements():
    res = fallback_bmi_measurements(height_cm=175.0, weight_kg=68.0, gender="male")
    assert isinstance(res, MeasurementResponse)
    assert res.measurements.height_cm == 175.0
    assert res.measurements.weight_kg == 68.0
    assert res.measurements.shoulder_cm is not None
    assert res.measurements.chest_cm is not None
    assert res.measurements.waist_cm is not None
    assert res.measurements.hips_cm is not None
    assert res.confidence_percent == 75.0
    assert res.method == "anthropometric_hybrid"
    assert len(res.smart_fit_notes) > 0
