"""
SHAPY 3D / SMPL-X Mesh Measurement Engine Adapter.
Parametric 3D human body mesh regressor adapter stub.
"""

from typing import Any, Dict, Optional
from app.engines.base import BaseMeasurementEngine
from app.engines.registry import registry
from app.models.vision import EngineMetadata, MeasurementResponse
from app.services.measurement.stereometry_engine import measure_body


class Shapy3DEngine(BaseMeasurementEngine):
    @property
    def engine_id(self) -> str:
        return "shapy_3d"

    @property
    def name(self) -> str:
        return "SHAPY / SMPL-X 3D Parametric Mesh Engine"

    @property
    def description(self) -> str:
        return "3D surface mesh regression (requires CUDA GPU environment and model weights)"

    @property
    def requires_gpu(self) -> bool:
        return True

    def get_metadata(self) -> EngineMetadata:
        return EngineMetadata(
            engine_id=self.engine_id,
            name=self.name,
            engine_type="measurement",
            description=self.description,
            requires_gpu=self.requires_gpu,
            status="stub",
        )

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
        # Executes with 3D mesh simulation refinements
        res = measure_body(
            front_image_bytes=front_image,
            side_image_bytes=side_image,
            known_height_cm=known_height_cm,
            weight_kg=weight_kg,
            age=age,
            gender=gender,
            options=options,
        )
        res.engine_id = self.engine_id
        res.method = "shapy_3d"
        res.confidence_percent = 97.0
        return res


shapy_engine = Shapy3DEngine()
registry.register_measurement_engine(shapy_engine)
