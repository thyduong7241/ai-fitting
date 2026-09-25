"""
Pydantic Schemas for AI Precision Fit Pipeline
API Request / Response models matching Frontend & Database contracts (OpenAPI 3.0).
Supports bidirectional camelCase & snake_case serialization via Pydantic v2 alias generator.
"""

from typing import Any, Dict, Generic, List, Literal, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

T = TypeVar("T")


# ==============================================================================
# Base Model with CamelCase & SnakeCase Interoperability
# ==============================================================================
class CamelModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True
    )


# ==============================================================================
# Common Enums & Types
# ==============================================================================
GenderType = Literal["female", "male"]
FitPreferenceType = Literal["slim", "regular", "relaxed"]
BrandType = Literal["zara", "uniqlo", "hm", "pullandbear", "stradivarius"]
CategoryType = Literal["jacket", "coat", "blazer", "puffer", "dress", "shirt", "pants"]
SizeLabelType = Literal["XS", "S", "M", "L", "XL", "XXL"]
FabricStretchType = Literal["none", "low", "medium", "high"]


# ==============================================================================
# 0. Profile & Database Models (/api/v1/profiles)
# ==============================================================================
class UserProfile(CamelModel):
    id: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    name: str
    gender: GenderType
    fit_preference: FitPreferenceType
    height_cm: float = Field(..., ge=100.0, le=250.0)
    weight_kg: float = Field(..., ge=30.0, le=200.0)
    chest_cm: Optional[float] = Field(None, ge=50.0, le=160.0)
    waist_cm: Optional[float] = Field(None, ge=40.0, le=150.0)
    hips_cm: Optional[float] = Field(None, ge=50.0, le=160.0)
    shoulder_cm: Optional[float] = Field(None, ge=25.0, le=70.0)
    front_image_url: Optional[str] = None
    side_image_url: Optional[str] = None
    is_verified: bool = False
    is_default: bool = False
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class CreateFitProfileRequest(CamelModel):
    name: str
    gender: GenderType
    fit_preference: FitPreferenceType
    height_cm: float = Field(..., ge=100.0, le=250.0)
    weight_kg: float = Field(..., ge=30.0, le=200.0)
    chest_cm: Optional[float] = None
    waist_cm: Optional[float] = None
    hips_cm: Optional[float] = None
    shoulder_cm: Optional[float] = None
    front_image_url: Optional[str] = None
    side_image_url: Optional[str] = None
    is_default: bool = False


class UpdateFitProfileRequest(CamelModel):
    name: Optional[str] = None
    gender: Optional[GenderType] = None
    fit_preference: Optional[FitPreferenceType] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    chest_cm: Optional[float] = None
    waist_cm: Optional[float] = None
    hips_cm: Optional[float] = None
    shoulder_cm: Optional[float] = None
    front_image_url: Optional[str] = None
    side_image_url: Optional[str] = None
    is_verified: Optional[bool] = None
    is_default: Optional[bool] = None


class Garment(CamelModel):
    id: str
    sku: str
    name: str
    brand: BrandType
    category: CategoryType
    gender: Literal["female", "male", "unisex"]
    image_url: str
    fabric_stretch: FabricStretchType
    price: Optional[float] = None
    description: Optional[str] = None
    available_sizes: Optional[List[SizeLabelType]] = None


class GarmentSizeChart(CamelModel):
    id: str
    garment_id: str
    size: SizeLabelType
    chest_min: Optional[float] = None
    chest_max: Optional[float] = None
    waist_min: Optional[float] = None
    waist_max: Optional[float] = None
    hips_min: Optional[float] = None
    hips_max: Optional[float] = None
    shoulder_width: Optional[float] = None
    garment_length: Optional[float] = None


class GarmentDetail(Garment):
    size_charts: List[GarmentSizeChart]


# ==============================================================================
# 0.1 Pagination, Error & Response Standards
# ==============================================================================
class PaginationMetadata(CamelModel):
    page: int = Field(..., ge=1)
    page_size: int = Field(..., ge=1, le=100)
    total_items: int = Field(..., ge=0)
    total_pages: int = Field(..., ge=0)


class PaginatedResponse(CamelModel, Generic[T]):
    data: List[T]
    pagination: PaginationMetadata


class FitProfilesListResponse(CamelModel):
    data: List[UserProfile]
    total: int


class ErrorDetail(CamelModel):
    code: str
    message: str
    details: Optional[Any] = None


class ErrorResponse(CamelModel):
    error: ErrorDetail


# ==============================================================================
# 1. Quality Check API (/api/v1/quality-check)
# ==============================================================================
class QualityIssue(CamelModel):
    code: Literal["feet_cut_off", "head_cut_off", "blurry", "bad_lighting", "multi_person", "no_person", "bad_pose"]
    severity: Literal["error", "warning"]
    message: str = Field(..., description="Mô tả lỗi hiển thị cho người dùng (tiếng Việt)")
    box: Optional[List[float]] = Field(None, description="Bounding box vùng lỗi [ymin, xmin, ymax, xmax] normalized")


class QualityCheckRequest(CamelModel):
    image_base64: Optional[str] = None
    image_url: Optional[str] = None


class QualityCheckResponse(CamelModel):
    is_valid: bool
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    issues: List[QualityIssue] = []
    blur_score: float = Field(..., description="Laplacian variance score")
    landmarks_detected: int = Field(..., description="Số lượng landmarks nhận diện được (tối đa 33)")


# ==============================================================================
# 2. Body Measurement API (/api/v1/measure)
# ==============================================================================
class BodyMeasurements(CamelModel):
    height_cm: float = Field(..., ge=100.0, le=250.0)
    weight_kg: float = Field(..., ge=30.0, le=200.0)
    shoulder_cm: Optional[float] = Field(None, ge=25.0, le=70.0)
    chest_cm: Optional[float] = Field(None, ge=50.0, le=160.0)
    waist_cm: Optional[float] = Field(None, ge=40.0, le=150.0)
    hips_cm: Optional[float] = Field(None, ge=50.0, le=160.0)


class MeasurementRequest(CamelModel):
    front_image_url: Optional[str] = None
    side_image_url: Optional[str] = None
    known_height_cm: Optional[float] = None
    gender: GenderType


class MeasurementResponse(CamelModel):
    measurements: BodyMeasurements
    confidence_percent: float = Field(..., ge=0.0, le=100.0)
    method: Literal["ai_vision", "anthropometric_hybrid"]


# ==============================================================================
# 3. Size Recommendation API (/api/v1/size-recommend)
# ==============================================================================
class PartFitEvaluation(CamelModel):
    part: Literal["shoulder", "chest", "waist", "hips", "length"]
    part_label: str = Field(..., description="Tên vị trí (Vai, Ngực, Eo, Hông, Dài áo)")
    status: Literal["perfect", "slightly_tight", "slightly_loose", "too_tight", "too_loose"]
    status_label: str = Field(..., description="Trạng thái trực quan: 'Vừa vặn', 'Hơi ôm', 'Hơi rộng'...")
    diff_cm: float = Field(..., description="Độ chênh lệch so với số đo người dùng (cm)")


class SizeComparisonItem(CamelModel):
    fit_score: float = Field(..., ge=0.0, le=1.0)
    badge_label: str = Field(..., description="'Vừa vặn chuẩn', 'Hơi ôm', 'Hơi rộng'...")
    description: str = Field(..., description="Giải thích ngắn gọn")


class SizeRecommendRequest(CamelModel):
    garment_id: str
    profile_id: Optional[str] = None
    fit_preference_override: Optional[FitPreferenceType] = None
    gender: Optional[GenderType] = None
    fit_preference: Optional[FitPreferenceType] = None
    measurements: Optional[BodyMeasurements] = None


class SizeRecommendResponse(CamelModel):
    recommended_size: SizeLabelType
    confidence_percent: int = Field(..., ge=0, le=100)
    fit_preference_label: str
    summary_explanation: str
    breakdown: List[PartFitEvaluation]
    size_comparisons: Dict[str, SizeComparisonItem]


# ==============================================================================
# 4. Virtual Try-On API (/api/v1/tryon)
# ==============================================================================
class CreateTryOnJobRequest(CamelModel):
    profile_id: str
    garment_id: str
    person_image_url: Optional[str] = None
    garment_image_url: Optional[str] = None


TryOnJobRequest = CreateTryOnJobRequest


class TryOnJob(CamelModel):
    job_id: str
    profile_id: Optional[str] = None
    garment_id: Optional[str] = None
    status: Literal["queued", "processing", "completed", "failed"]
    result_image_url: Optional[str] = None
    error_message: Optional[str] = None
    estimated_seconds: int = 15
    created_at: Optional[str] = None


TryOnJobResponse = TryOnJob
