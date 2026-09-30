import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SERVICE_NAME: str = "vision-service"
    PORT: int = 8002
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Pluggable Engine Selection
    DEFAULT_QUALITY_ENGINE: str = os.getenv("VISION_QUALITY_ENGINE", "opencv_mediapipe")
    DEFAULT_MEASUREMENT_ENGINE: str = os.getenv("VISION_MEASUREMENT_ENGINE", "hybrid_stereometry_2d")
    
    # CORS Origins
    CORS_ORIGINS: List[str] = [
        "http://localhost:2000",
        "http://127.0.0.1:2000",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://backend:8000",
    ]

    class Config:
        case_sensitive = True


settings = Settings()
