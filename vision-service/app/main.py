from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.v1.quality_check import router as quality_router
from app.api.v1.measure import router as measure_router
from app.core.config import settings
from app.engines.registry import registry
from app.models.vision import EngineListResponse

# Register engines into registry
from app.engines.quality_gate import default_quality_engine
from app.engines.hybrid_stereometry import default_measurement_engine
from app.engines.rtmpose_contour import rtmpose_engine
from app.engines.shapy_3d import shapy_engine

app = FastAPI(
    title="AI Precision Fit — Vision Service",
    description="Dedicated microservice for Quality Gate, Body Measurement & Quantitative Benchmark",
    version="1.0.0",
)


class OptionsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method == "OPTIONS":
            return Response(status_code=200)
        return await call_next(request)


app.add_middleware(OptionsMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["Content-Type"],
    max_age=600,
)

# Include Routers
app.include_router(quality_router, prefix="/api/v1")
app.include_router(measure_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": settings.SERVICE_NAME}


@app.get("/api/v1/engines", response_model=EngineListResponse)
async def list_engines():
    return registry.list_engines()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PORT, reload=settings.ENVIRONMENT == "development")
