"""
Hybrid 2-View Stereometry Measurement Engine implementation.
"""

from typing import Any, Dict, Optional
from app.engines.base import BaseMeasurementEngine
from app.engines.registry import registry
from app.models.vision import MeasurementResponse
from app.services.measurement.stereometry_engine import measure_body


class HybridStereometryEngine(BaseMeasurementEngine):
    @property
    def engine_id(self) -> str:
        return "hybrid_stereometry_2d"

    @property
    def name(self) -> str:
        return "Hybrid 2-View Stereometry Engine"

    @property
    def description(self) -> str:
        return "Stereometry 2-view (Front + Side) anthropometric measurement with P2M calibration, Ramanujan circumference, and body shape classification"

    @property
    def requires_gpu(self) -> bool:
        return False

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
        return measure_body(
            front_image_bytes=front_image,
            side_image_bytes=side_image,
            known_height_cm=known_height_cm,
            weight_kg=weight_kg,
            age=age,
            gender=gender,
            options=options,
        )


# Instantiate and register into global registry
default_measurement_engine = HybridStereometryEngine()
registry.register_measurement_engine(default_measurement_engine)
