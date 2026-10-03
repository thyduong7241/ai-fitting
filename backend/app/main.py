from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.router import api_router
from app.core.config import settings

app = FastAPI(
    title="AI Precision Fit API",
    description="API for AI Precision Fit & Virtual Try-On",
    version="1.0.0",
)


# Custom middleware to handle OPTIONS requests properly
class OptionsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method == "OPTIONS":
            return Response(status_code=200)
        return await call_next(request)


# Add OPTIONS middleware first
app.add_middleware(OptionsMiddleware)

# Set up CORS - Expanded configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:2000",
        "http://127.0.0.1:2000",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        *settings.CORS_ORIGINS,
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=[
        "Content-Type",
        "Authorization",
        "Accept",
        "Origin",
        "X-Requested-With",
        "X-CSRF-Token",
        "X-Session-ID",
        "Idempotency-Key",
    ],
    expose_headers=["Content-Type", "Authorization", "X-Session-ID"],
    max_age=600,  # 10 minutes cache for preflight requests
)

# Include API router
app.include_router(api_router, prefix="/api")

# Static files for 3D Body Studio
import os
from fastapi.staticfiles import StaticFiles

body_static_dir = os.path.join(os.path.dirname(__file__), "services", "body_shape", "src", "api", "static")
if os.path.exists(body_static_dir):
    app.mount("/static/body_shape", StaticFiles(directory=body_static_dir), name="body_shape_static")


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "online", "environment": settings.ENVIRONMENT, "version": "0.1.0"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.ENVIRONMENT == "development")
