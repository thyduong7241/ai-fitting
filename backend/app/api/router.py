from fastapi import APIRouter

from app.api.endpoints import auth, llm, vectordb, quality_check, measure, fit_intelligence, body_shape

api_router = APIRouter()

# Include sub-routers for different API endpoints
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(llm.router, prefix="/llm", tags=["LLM Services"])
api_router.include_router(vectordb.router, prefix="/vectordb", tags=["Vector Database"])
api_router.include_router(quality_check.router, prefix="/v1/quality-check", tags=["Quality Gate"])
api_router.include_router(measure.router, prefix="/v1/measure", tags=["Body Measurement"])
api_router.include_router(fit_intelligence.router, prefix="/v1/fit-intelligence", tags=["Fit Intelligence & Size Recommendation"])
api_router.include_router(body_shape.router, prefix="/v1/body-shape", tags=["Realistic 3D Body Studio"])
