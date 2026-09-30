import base64
from typing import Optional
import httpx
from fastapi import APIRouter, File, Form, HTTPException, Query, Request, UploadFile

from app.engines.registry import registry
from app.models.vision import MeasurementRequest, MeasurementResponse

from app.core.image_loader import load_image_bytes

router = APIRouter(tags=["Body Measurement"])


@router.post("/measure", response_model=MeasurementResponse)
async def measure_body_endpoint(
    raw_req: Request,
    engine: Optional[str] = Query(None, description="Measurement engine identifier"),
):
    """
    Extract 6 anthropometric measurements + Body shape + Smart Fit Notes.
    Accepts multipart form-data or JSON payload.
    """
    raw_front = None
    raw_side = None
    known_height = None
    known_weight = None
    user_age = 25
    user_gender = "male"
    request_data: Optional[MeasurementRequest] = None

    content_type = raw_req.headers.get("content-type", "")
    if "multipart/form-data" in content_type:
        form = await raw_req.form()
        front_img = form.get("front_image")
        side_img = form.get("side_image")
        if hasattr(front_img, "read"):
            raw_front = await front_img.read()
        if hasattr(side_img, "read"):
            raw_side = await side_img.read()

        h_val = form.get("height_cm")
        w_val = form.get("weight_kg")
        known_height = float(str(h_val)) if h_val else None
        known_weight = float(str(w_val)) if w_val else None
        a_val = form.get("age")
        user_age = int(str(a_val)) if a_val else 25
        user_gender = str(form.get("gender", "male"))
    else:
        try:
            body = await raw_req.json()
            request_data = MeasurementRequest.model_validate(body)
            known_height = request_data.known_height_cm
            known_weight = request_data.weight_kg
            user_age = request_data.age or 25
            user_gender = request_data.gender or "male"
            if request_data.engine:
                engine = request_data.engine
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSON payload: {e}")

    is_mock_request = bool(
        request_data and (
            (request_data.front_image_url and "mock" in request_data.front_image_url.lower())
            or request_data.engine == "fixture"
        )
    )
    fallback_front = "sub_01_front.jpg" if is_mock_request else None
    fallback_side = "sub_01_side.jpg" if is_mock_request else None

    front_bytes = load_image_bytes(
        raw_bytes=raw_front,
        image_base64=request_data.front_image_base64 if request_data else None,
        image_url=request_data.front_image_url if request_data else None,
        fallback_fixture=fallback_front,
    )
    side_bytes = load_image_bytes(
        raw_bytes=raw_side,
        image_base64=request_data.side_image_base64 if request_data else None,
        image_url=request_data.side_image_url if request_data else None,
        fallback_fixture=fallback_side,
    )

    if not front_bytes:
        raise HTTPException(
            status_code=400,
            detail="Missing front image. Please provide front_image file or front_image_base64 / front_image_url.",
        )

    if not known_height or not known_weight:
        raise HTTPException(
            status_code=400,
            detail="Missing height_cm or weight_kg. Both are required for metric calibration.",
        )

    try:
        m_engine = registry.get_measurement_engine(engine)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        result = await m_engine.measure(
            front_image=front_bytes,
            side_image=side_bytes,
            known_height_cm=known_height,
            weight_kg=known_weight,
            age=user_age,
            gender=user_gender,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Measurement error: {str(e)}")
