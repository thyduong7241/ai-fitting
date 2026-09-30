from typing import Optional
from fastapi import APIRouter, File, Form, Query, Request, UploadFile
from app.models.fitting import QualityCheckRequest, QualityCheckResponse
from app.services.quality_check_service import forward_quality_check

router = APIRouter()


@router.post("", response_model=QualityCheckResponse, summary="Quality check via JSON or multipart")
async def check_quality(request: Request):
    """Quality check endpoint proxying to vision-service (supports JSON and multipart)."""
    content_type = request.headers.get("content-type", "")
    if "multipart/form-data" in content_type:
        form = await request.form()
        image = form.get("image")
        image_type = str(form.get("image_type", "front"))
        image_bytes = None
        if hasattr(image, "read"):
            image_bytes = await image.read()
        return await forward_quality_check(
            image_bytes=image_bytes,
            image_type=image_type,
        )
    else:
        body = await request.json()
        req_obj = QualityCheckRequest.model_validate(body)
        return await forward_quality_check(json_request=req_obj)


@router.post("/upload", response_model=QualityCheckResponse, summary="Upload image file directly for Quality Gate")
async def check_quality_upload(
    image: UploadFile = File(..., description="File ảnh toàn thân chụp từ camera/thiết bị (.jpg, .png)"),
    image_type: str = Form("front", description="Loại ảnh: 'front' (chính diện) hoặc 'side' (nghiêng)"),
):
    """Upload trực tiếp file ảnh để kiểm tra chất lượng (Swagger UI File Picker)."""
    image_bytes = await image.read()
    return await forward_quality_check(
        image_bytes=image_bytes,
        image_type=image_type,
    )

