"""
Pydantic Schemas for Vision Service
API Request / Response models matching backend contracts & OpenAPI 3.0 specification.
Supports bidirectional camelCase & snake_case serialization via Pydantic v2 alias generator.
"""

from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )


# Common Enums & Types
GenderType = Literal["female", "male"]
BodyShapeType = Literal[
    "dong_ho_cat",       # Hourglass (Nữ)
    "qua_le",            # Pear (Nữ)
    "qua_tao",           # Apple (Nữ)
    "chu_nhat",          # Rectangle (Nữ/Nam)
    "tam_giac_nguoc",    # Inverted Triangle (Nữ/Nam)
    "hinh_thang",        # Trapezoid (Nam)
    "tam_giac",          # Triangle (Nam)
    "oval",              # Oval (Nam)
]


# ==============================================================================
# Quality Gate Schemas (/api/v1/quality-check)
# ==============================================================================
class QualityIssue(CamelModel):
    code: Literal[
        "feet_cut_off",
        "head_cut_off",
        "blurry",
        "bad_lighting",
        "multi_person",
        "no_person",
        "bad_pose",
        "body_occluded",
        "low_resolution",
    ]
    severity: Literal["error", "warning"]
    message: str = Field(..., description="Mô tả lỗi hiển thị cho người dùng (tiếng Việt)")
    box: Optional[List[float]] = Field(None, description="Bounding box vùng lỗi [ymin, xmin, ymax, xmax] normalized")


class QualityCheckRequest(CamelModel):
    image_base64: Optional[str] = None
    image_url: Optional[str] = None
    image_type: Literal["front", "side"] = "front"


class QualityCheckResponse(CamelModel):
    is_valid: bool
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    issues: List[QualityIssue] = []
    blur_score: float = Field(..., description="Laplacian variance score")
    landmarks_detected: int = Field(..., description="Số lượng landmarks nhận diện được (tối đa 33)")
    engine_id: str = "opencv_mediapipe"
    latency_ms: Optional[float] = None


# ==============================================================================
# Body Measurement Schemas (/api/v1/measure)
# ==============================================================================
class BodyMeasurements(CamelModel):
    height_cm: float = Field(..., ge=100.0, le=250.0)
    weight_kg: float = Field(..., ge=30.0, le=200.0)
    shoulder_cm: Optional[float] = Field(None, ge=25.0, le=70.0)
    chest_cm: Optional[float] = Field(None, ge=50.0, le=160.0)
    waist_cm: Optional[float] = Field(None, ge=40.0, le=150.0)
    hips_cm: Optional[float] = Field(None, ge=50.0, le=160.0)
    arm_length_cm: Optional[float] = Field(None, ge=30.0, le=100.0)
    inseam_cm: Optional[float] = Field(None, ge=40.0, le=120.0)


class MeasurementRequest(CamelModel):
    front_image_url: Optional[str] = None
    front_image_base64: Optional[str] = None
    side_image_url: Optional[str] = None
    side_image_base64: Optional[str] = None
    known_height_cm: float = Field(..., ge=100.0, le=250.0)
    weight_kg: float = Field(..., ge=30.0, le=200.0)
    age: Optional[int] = Field(25, ge=10, le=100)
    gender: GenderType
    engine: Optional[str] = None


class MeasurementResponse(CamelModel):
    measurements: BodyMeasurements
    confidence_percent: float = Field(..., ge=0.0, le=100.0)
    method: Literal["ai_vision", "anthropometric_hybrid", "hybrid_stereometry_2d", "rtmpose_contour", "shapy_3d"] = "hybrid_stereometry_2d"
    body_shape: Optional[str] = None
    smart_fit_notes: List[str] = []
    engine_id: str = "hybrid_stereometry_2d"
    metrics: Optional[Dict[str, Any]] = None
    latency_ms: Optional[float] = None


# ==============================================================================
# Engine Registry & Metadata Schemas
# ==============================================================================
class EngineMetadata(CamelModel):
    engine_id: str
    name: str
    engine_type: Literal["quality", "measurement"]
    description: str
    requires_gpu: bool = False
    status: Literal["active", "stub", "deprecated"] = "active"


class EngineListResponse(CamelModel):
    quality_engines: List[EngineMetadata]
    measurement_engines: List[EngineMetadata]
    default_quality_engine: str
    default_measurement_engine: str


# ==============================================================================
# Benchmark Schemas
# ==============================================================================
class BenchmarkMetricItem(CamelModel):
    mae: float
    rmse: float
    mape: float
    tolerance_rate_3cm: float


class BenchmarkResultResponse(CamelModel):
    engine_id: str
    timestamp: str
    sample_count: int
    quality_f1_score: Optional[float] = None
    quality_blur_accuracy: Optional[float] = None
    measurement_metrics: Optional[Dict[str, BenchmarkMetricItem]] = None
    p95_latency_ms: float
    passed_ratchet: bool
