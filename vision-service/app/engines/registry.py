from typing import Callable, Dict, Optional, Type
from app.core.config import settings
from app.engines.base import BaseMeasurementEngine, BaseQualityGateEngine
from app.models.vision import EngineListResponse


class EngineRegistry:
    def __init__(self):
        self._quality_engines: Dict[str, BaseQualityGateEngine] = {}
        self._measurement_engines: Dict[str, BaseMeasurementEngine] = {}

    def register_quality_engine(self, engine: BaseQualityGateEngine):
        self._quality_engines[engine.engine_id] = engine

    def register_measurement_engine(self, engine: BaseMeasurementEngine):
        self._measurement_engines[engine.engine_id] = engine

    def get_quality_engine(self, engine_id: Optional[str] = None) -> BaseQualityGateEngine:
        target_id = engine_id or settings.DEFAULT_QUALITY_ENGINE
        if target_id not in self._quality_engines:
            available = list(self._quality_engines.keys())
            raise ValueError(
                f"Quality engine '{target_id}' not found. Available engines: {available}"
            )
        return self._quality_engines[target_id]

    def get_measurement_engine(self, engine_id: Optional[str] = None) -> BaseMeasurementEngine:
        target_id = engine_id or settings.DEFAULT_MEASUREMENT_ENGINE
        if target_id not in self._measurement_engines:
            available = list(self._measurement_engines.keys())
            raise ValueError(
                f"Measurement engine '{target_id}' not found. Available engines: {available}"
            )
        return self._measurement_engines[target_id]

    def list_engines(self) -> EngineListResponse:
        return EngineListResponse(
            quality_engines=[e.get_metadata() for e in self._quality_engines.values()],
            measurement_engines=[e.get_metadata() for e in self._measurement_engines.values()],
            default_quality_engine=settings.DEFAULT_QUALITY_ENGINE,
            default_measurement_engine=settings.DEFAULT_MEASUREMENT_ENGINE,
        )

    def clear(self):
        self._quality_engines.clear()
        self._measurement_engines.clear()


registry = EngineRegistry()
