"""
OpenCV + MediaPipe Single-Pass Quality Gate Engine.
"""

from typing import Any, Dict, Optional
from app.engines.base import BaseQualityGateEngine
from app.engines.registry import registry
from app.models.vision import QualityCheckResponse
from app.services.quality_gate import evaluate_quality


class OpenCVMediaPipeQualityEngine(BaseQualityGateEngine):
    @property
    def engine_id(self) -> str:
        return "opencv_mediapipe"

    @property
    def name(self) -> str:
        return "OpenCV + MediaPipe Single-Pass Quality Gate"

    @property
    def description(self) -> str:
        return "Single-pass CPU quality evaluator with ROI blur, lighting, cutoff, and pose orientation checks (<30ms)"

    @property
    def requires_gpu(self) -> bool:
        return False

    async def evaluate(
        self,
        image_bytes: bytes,
        image_type: str = "front",
        options: Optional[Dict[str, Any]] = None,
    ) -> QualityCheckResponse:
        return evaluate_quality(image_bytes=image_bytes, image_type=image_type)


# Instantiate and register into global registry
default_quality_engine = OpenCVMediaPipeQualityEngine()
registry.register_quality_engine(default_quality_engine)
