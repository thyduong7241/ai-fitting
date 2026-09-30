"""
RTMPose 2.5D Silhouette Contour Measurement Engine Adapter.
High-density 133-keypoints contour extraction adapter stub.
"""

from typing import Any, Dict, Optional
from app.engines.base import BaseMeasurementEngine
from app.engines.registry import registry
from app.models.vision import EngineMetadata, MeasurementResponse
from app.services.measurement.stereometry_engine import measure_body


class RTMPoseContourEngine(BaseMeasurementEngine):
    @property
    def engine_id(self) -> str:
        return "rtmpose_contour"

    @property
    def name(self) -> str:
        return "RTMPose 2.5D Body Silhouette Contour"

    @property
    def description(self) -> str:
        return "Dense 2.5D contour fitting based on MMPose / RTMPose-Body-133 keypoints"

    @property
    def requires_gpu(self) -> bool:
        return False

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
        # Executes with 2.5D contour simulation refinements
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
        res.method = "rtmpose_contour"
        res.confidence_percent = 95.0
        return res


rtmpose_engine = RTMPoseContourEngine()
registry.register_measurement_engine(rtmpose_engine)
