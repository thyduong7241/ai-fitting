from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from app.models.vision import EngineMetadata, QualityCheckResponse, MeasurementResponse


class BaseQualityGateEngine(ABC):
    @property
    @abstractmethod
    def engine_id(self) -> str:
        """Unique identifier of the quality gate engine: 'opencv_mediapipe'"""
        pass

    @property
    def name(self) -> str:
        return self.engine_id

    @property
    def description(self) -> str:
        return "Base Quality Gate Engine"

    @property
    def requires_gpu(self) -> bool:
        return False

    @abstractmethod
    async def evaluate(
        self,
        image_bytes: bytes,
        image_type: str = "front",
        options: Optional[Dict[str, Any]] = None,
    ) -> QualityCheckResponse:
        """
        Evaluate image quality (Blur, Cut-off, Occlusion, Person presence, Pose orientation, Lighting).
        """
        pass

    def get_metadata(self) -> EngineMetadata:
        return EngineMetadata(
            engine_id=self.engine_id,
            name=self.name,
            engine_type="quality",
            description=self.description,
            requires_gpu=self.requires_gpu,
            status="active",
        )


class BaseMeasurementEngine(ABC):
    @property
    @abstractmethod
    def engine_id(self) -> str:
        """Unique identifier of the measurement engine: 'hybrid_stereometry_2d'"""
        pass

    @property
    def name(self) -> str:
        return self.engine_id

    @property
    def description(self) -> str:
        return "Base Measurement Engine"

    @property
    def requires_gpu(self) -> bool:
        return False

    @abstractmethod
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
        """
        Extract 6 anthropometric measurements + Body shape classification + Smart fit notes.
        """
        pass

    def get_metadata(self) -> EngineMetadata:
        return EngineMetadata(
            engine_id=self.engine_id,
            name=self.name,
            engine_type="measurement",
            description=self.description,
            requires_gpu=self.requires_gpu,
            status="active",
        )
