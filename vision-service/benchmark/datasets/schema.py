from typing import Dict, List, Literal, Optional
from pydantic import BaseModel, Field


class GroundTruthSubject(BaseModel):
    id: str
    gender: Literal["female", "male"]
    age: int
    height_cm: float
    weight_kg: float
    body_shape: str
    measurements: Dict[str, float] = Field(
        ...,
        description="Ground truth tape measurements in cm: shoulder, chest, waist, hips, arm_length, inseam",
    )
    front_image_path: str
    side_image_path: Optional[str] = None


class QualityTestCase(BaseModel):
    id: str
    image_path: str
    expected_valid: bool
    expected_issues: List[str] = Field(
        default_factory=list,
        description="Expected issue codes e.g. feet_cut_off, head_cut_off, blurry, bad_lighting, bad_pose",
    )
    description: str


class GroundTruthDataset(BaseModel):
    version: str = "1.0.0"
    measurement_subjects: List[GroundTruthSubject]
    quality_cases: List[QualityTestCase]
