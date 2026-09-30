"""
Anthropometric Gateway Service in Backend.
Communicates with vision-service (port 8002) via HTTP with fallback logic.
"""

from typing import Optional
import httpx
from fastapi import HTTPException
from app.core.config import settings
from app.models.fitting import (
    BodyMeasurements,
    MeasurementRequest,
    MeasurementResponse,
)


def classify_fallback_shape(shoulder: float, chest: float, waist: float, hips: float, gender: str) -> str:
    whr = waist / hips if hips > 0 else 0.8
    if gender == "female":
        if whr >= 0.85 or waist >= chest - 3.0:
            return "qua_tao"
        if whr <= 0.75 and abs(chest - hips) <= 6.0 and (chest - waist) >= 15.0:
            return "dong_ho_cat"
        if hips >= chest + 5.0 and whr <= 0.82:
            return "qua_le"
        if chest >= hips + 5.0 or shoulder >= (hips * 0.44):
            return "tam_giac_nguoc"
        return "chu_nhat"
    else:
        if waist > chest and waist > hips:
            return "oval"
        if hips >= chest or (waist >= chest and waist <= hips):
            return "tam_giac"
        if chest >= waist + 15.0 and (waist / (chest if chest > 0 else 1)) <= 0.80 and shoulder >= 44.0:
            return "tam_giac_nguoc"
        if chest >= waist + 6.0 and chest >= hips - 2.0:
            return "hinh_thang"
        return "chu_nhat"


def fallback_bmi_measurements(
    height_cm: float,
    weight_kg: float,
    gender: str,
) -> MeasurementResponse:
    """Fallback standard anthropometric estimation if vision-service is unreachable."""
    height_m = height_cm / 100.0
    bmi = weight_kg / (height_m * height_m)
    
    # Statistical baseline estimates
    shoulder_cm = round(height_cm * (0.245 if gender == "male" else 0.230), 1)
    waist_cm = round(height_cm * 0.45 + (bmi - 22.0) * 1.5, 1)
    chest_cm = round(waist_cm + (14.0 if gender == "male" else 18.0), 1)
    hips_cm = round(waist_cm + (15.0 if gender == "male" else 24.0), 1)
    arm_length_cm = round(height_cm * 0.34, 1)
    inseam_cm = round(height_cm * 0.44, 1)

    shape = classify_fallback_shape(shoulder_cm, chest_cm, waist_cm, hips_cm, gender)

    return MeasurementResponse(
        measurements=BodyMeasurements(
            height_cm=height_cm,
            weight_kg=weight_kg,
            shoulder_cm=shoulder_cm,
            chest_cm=chest_cm,
            waist_cm=waist_cm,
            hips_cm=hips_cm,
            arm_length_cm=arm_length_cm,
            inseam_cm=inseam_cm,
        ),
        confidence_percent=75.0,
        method="anthropometric_hybrid",
        body_shape=shape,
        smart_fit_notes=["Số đo ước tính từ chiều cao và cân nặng (chế độ dự phòng khi Vision Service bảo trì)."],
    )


async def forward_measurement(
    front_image_bytes: Optional[bytes] = None,
    side_image_bytes: Optional[bytes] = None,
    known_height_cm: Optional[float] = None,
    weight_kg: Optional[float] = None,
    age: int = 25,
    gender: str = "male",
    engine: Optional[str] = None,
    json_request: Optional[MeasurementRequest] = None,
) -> MeasurementResponse:
    target_url = f"{settings.VISION_SERVICE_URL.rstrip('/')}/api/v1/measure"
    params = {"engine": engine} if engine else {}

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            if front_image_bytes is not None:
                files = {"front_image": ("front.jpg", front_image_bytes, "image/jpeg")}
                if side_image_bytes:
                    files["side_image"] = ("side.jpg", side_image_bytes, "image/jpeg")
                data = {
                    "height_cm": str(known_height_cm),
                    "weight_kg": str(weight_kg),
                    "age": str(age),
                    "gender": gender,
                }
                resp = await client.post(target_url, files=files, data=data, params=params)
            elif json_request is not None:
                resp = await client.post(
                    target_url,
                    json=json_request.model_dump(by_alias=True),
                    params=params,
                )
            else:
                raise HTTPException(status_code=400, detail="Missing measurement data")

            if resp.status_code == 200:
                return MeasurementResponse.model_validate(resp.json())
            else:
                raise HTTPException(
                    status_code=resp.status_code,
                    detail=f"Vision Service Measurement error: {resp.text}",
                )
    except (httpx.TimeoutException, httpx.ConnectError):
        # Fallback to BMI baseline estimation if vision service is offline
        h = known_height_cm or (json_request.known_height_cm if json_request else 170.0)
        w = weight_kg or (json_request.weight_kg if json_request else 65.0)
        g = gender or (json_request.gender if json_request else "male")
        return fallback_bmi_measurements(h, w, g)
