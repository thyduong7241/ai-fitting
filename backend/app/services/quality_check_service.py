"""
Quality Check Gateway Service in Backend.
Communicates with vision-service (port 8002) via HTTP with circuit breaker & timeout protection.
"""

from typing import Optional
import httpx
from fastapi import HTTPException
from app.core.config import settings
from app.models.fitting import QualityCheckRequest, QualityCheckResponse


async def forward_quality_check(
    image_bytes: Optional[bytes] = None,
    image_type: str = "front",
    json_request: Optional[QualityCheckRequest] = None,
) -> QualityCheckResponse:
    target_url = f"{settings.VISION_SERVICE_URL.rstrip('/')}/api/v1/quality-check"

    try:
        async with httpx.AsyncClient(timeout=4.0) as client:
            if image_bytes is not None:
                files = {"image": ("upload.jpg", image_bytes, "image/jpeg")}
                data = {"image_type": image_type}
                resp = await client.post(target_url, files=files, data=data)
            elif json_request is not None:
                resp = await client.post(target_url, json=json_request.model_dump(by_alias=True))
            else:
                raise HTTPException(status_code=400, detail="Missing image data")

            if resp.status_code == 200:
                return QualityCheckResponse.model_validate(resp.json())
            else:
                raise HTTPException(
                    status_code=resp.status_code,
                    detail=f"Vision Service Quality Gate error: {resp.text}",
                )
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="Vision Service Quality Gate timed out (>4s). Please retry.",
        )
    except httpx.ConnectError:
        # Graceful degradation / Service unavailable
        raise HTTPException(
            status_code=503,
            detail="Vision Service is currently unavailable at port 8002.",
        )
