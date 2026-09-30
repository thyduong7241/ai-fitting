import pytest
from typing import Any, Dict, Optional
from app.engines.base import BaseMeasurementEngine, BaseQualityGateEngine
from app.engines.registry import EngineRegistry
from app.models.vision import QualityCheckResponse, MeasurementResponse, BodyMeasurements


class MockQualityEngine(BaseQualityGateEngine):
    @property
    def engine_id(self) -> str:
        return "mock_quality"

    async def evaluate(
        self,
        image_bytes: bytes,
        image_type: str = "front",
        options: Optional[Dict[str, Any]] = None,
    ) -> QualityCheckResponse:
        return QualityCheckResponse(
            is_valid=True,
            confidence_score=0.99,
            issues=[],
            blur_score=150.0,
            landmarks_detected=33,
            engine_id=self.engine_id,
        )


class MockMeasurementEngine(BaseMeasurementEngine):
    @property
    def engine_id(self) -> str:
        return "mock_measurement"

    async def measure(
        self,
        front_image: bytes,
        side_image: Optional[bytes],
        known_height_cm: float,
        weight_kg: float,
        age: int,
        gender: str,
        options: Optional[Dict[str, Any]] = None,
    ) -> MeasurementResponse:
        return MeasurementResponse(
            measurements=BodyMeasurements(
                height_cm=known_height_cm,
                weight_kg=weight_kg,
                shoulder_cm=44.0,
                chest_cm=95.0,
                waist_cm=80.0,
                hips_cm=96.0,
                arm_length_cm=60.0,
                inseam_cm=78.0,
            ),
            confidence_percent=95.0,
            method="hybrid_stereometry_2d",
            engine_id=self.engine_id,
        )


def test_registry_registration_and_lookup():
    reg = EngineRegistry()
    q_engine = MockQualityEngine()
    m_engine = MockMeasurementEngine()

    reg.register_quality_engine(q_engine)
    reg.register_measurement_engine(m_engine)

    assert reg.get_quality_engine("mock_quality") is q_engine
    assert reg.get_measurement_engine("mock_measurement") is m_engine


def test_registry_fallback_error_on_unknown():
    reg = EngineRegistry()
    with pytest.raises(ValueError, match="not found"):
        reg.get_quality_engine("non_existent_quality_engine")

    with pytest.raises(ValueError, match="not found"):
        reg.get_measurement_engine("non_existent_measurement_engine")


def test_registry_list_engines():
    reg = EngineRegistry()
    reg.register_quality_engine(MockQualityEngine())
    reg.register_measurement_engine(MockMeasurementEngine())

    catalog = reg.list_engines()
    assert len(catalog.quality_engines) == 1
    assert catalog.quality_engines[0].engine_id == "mock_quality"
    assert len(catalog.measurement_engines) == 1
    assert catalog.measurement_engines[0].engine_id == "mock_measurement"
