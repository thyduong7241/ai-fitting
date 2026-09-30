import base64
from typing import Optional
import httpx
from fastapi import APIRouter, File, Form, HTTPException, Query, Request, UploadFile

from app.engines.registry import registry
from app.models.vision import QualityCheckRequest, QualityCheckResponse
from app.core.image_loader import load_image_bytes

router = APIRouter(tags=["Quality Gate"])


@router.post("/quality-check", response_model=QualityCheckResponse)
async def check_image_quality(
    raw_req: Request,
    engine: Optional[str] = Query(None, description="Quality engine identifier"),
):
    """
    Quality Gate endpoint:
    Accepts image via multipart form upload or JSON (base64/URL).
    """
    raw_upload = None
    image_type = "front"
    request_data: Optional[QualityCheckRequest] = None

    content_type = raw_req.headers.get("content-type", "")
    if "multipart/form-data" in content_type:
        form = await raw_req.form()
        image = form.get("image")
        if hasattr(image, "read"):
            raw_upload = await image.read()
        image_type = str(form.get("image_type", "front"))
    else:
        try:
            body = await raw_req.json()
            request_data = QualityCheckRequest.model_validate(body)
            image_type = request_data.image_type
        except Exception:
            pass

    image_bytes = load_image_bytes(
        raw_bytes=raw_upload,
        image_base64=request_data.image_base64 if request_data else None,
        image_url=request_data.image_url if request_data else None,
        fallback_fixture="qc_01.jpg",
    )

    if not image_bytes:
        raise HTTPException(
            status_code=400,
            detail="Missing image. Please provide a file upload or image_base64 / image_url.",
        )

    try:
        q_engine = registry.get_quality_engine(engine)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    result = await q_engine.evaluate(image_bytes=image_bytes, image_type=image_type)
    return result
