from typing import Optional
from fastapi import APIRouter, File, Form, Query, Request, UploadFile
from app.models.fitting import MeasurementRequest, MeasurementResponse
from app.services.anthropometric_service import forward_measurement

router = APIRouter()


@router.post("", response_model=MeasurementResponse, summary="Extract measurements via JSON or multipart")
async def measure_body(
    request: Request,
    engine: Optional[str] = Query(None),
):
    """Body measurement endpoint proxying to vision-service (supports JSON and multipart)."""
    content_type = request.headers.get("content-type", "")
    if "multipart/form-data" in content_type:
        form = await request.form()
        front_img = form.get("front_image")
        side_img = form.get("side_image")
        front_bytes = await front_img.read() if hasattr(front_img, "read") else None
        side_bytes = await side_img.read() if hasattr(side_img, "read") else None

        height_val = form.get("height_cm")
        weight_val = form.get("weight_kg")
        height_cm = float(str(height_val)) if height_val else None
        weight_kg = float(str(weight_val)) if weight_val else None
        age_val = form.get("age")
        age = int(str(age_val)) if age_val else 25
        gender = str(form.get("gender", "male"))

        return await forward_measurement(
            front_image_bytes=front_bytes,
            side_image_bytes=side_bytes,
            known_height_cm=height_cm,
            weight_kg=weight_kg,
            age=age,
            gender=gender,
            engine=engine,
        )
    else:
        body = await request.json()
        req_obj = MeasurementRequest.model_validate(body)
        return await forward_measurement(
            engine=engine,
            json_request=req_obj,
        )


@router.post("/upload", response_model=MeasurementResponse, summary="Upload photos directly to measure body")
async def measure_body_upload(
    front_image: UploadFile = File(..., description="Ảnh chụp chính diện toàn thân (Front)"),
    side_image: Optional[UploadFile] = File(None, description="Ảnh chụp nghiêng 90 độ (Side - tuỳ chọn)"),
    height_cm: float = Form(..., description="Chiều cao thực tế (cm), ví dụ: 165"),
    weight_kg: float = Form(..., description="Cân nặng thực tế (kg), ví dụ: 58"),
    gender: str = Form("female", description="Giới tính ('female' hoặc 'male')"),
    age: int = Form(24, description="Độ tuổi, ví dụ: 24"),
    engine: Optional[str] = Query(None, description="Tùy chọn engine đo: 'hybrid_stereometry_2d'"),
):
    """Upload trực tiếp file ảnh để đo kích thước cơ thể (Swagger UI File Picker)."""
    front_bytes = await front_image.read()
    side_bytes = await side_image.read() if side_image else None

    return await forward_measurement(
        front_image_bytes=front_bytes,
        side_image_bytes=side_bytes,
        known_height_cm=height_cm,
        weight_kg=weight_kg,
        age=age,
        gender=gender,
        engine=engine,
    )

