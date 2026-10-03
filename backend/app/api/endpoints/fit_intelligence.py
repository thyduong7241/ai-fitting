"""
Endpoints for Fit Intelligence (Size recommendation, explanation copywriting, and size comparison).
Centralized from external_services/body-fitting.
"""

import os
import json
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.services.body_fitting.fit_engine import FitMLEngine
from app.services.body_fitting.explanation_engine import ExplanationEngine

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PRODUCTS_FILE = os.path.join(BASE_DIR, "services", "body_fitting", "data", "products.json")
PRODUCTS_DB: Dict[str, Dict[str, Any]] = {}


def load_products():
    global PRODUCTS_DB
    if os.path.exists(PRODUCTS_FILE):
        try:
            with open(PRODUCTS_FILE, "r", encoding="utf-8") as f:
                items = json.load(f)
                PRODUCTS_DB = {item["id"]: item for item in items}
        except Exception as e:
            print(f"[Fit Router] Error loading products: {e}")


load_products()
FitMLEngine.load_model()


class UserMeasurementsInput(BaseModel):
    height: float = Field(default=165.0, description="Chiều cao cơ thể (cm)", json_schema_extra={"example": 165.0})
    weight: float = Field(default=56.0, description="Cân nặng cơ thể (kg)", json_schema_extra={"example": 56.0})
    shoulder: float = Field(default=39.0, description="Rộng vai (cm)", json_schema_extra={"example": 39.0})
    bust: float = Field(default=86.0, description="Vòng ngực (cm)", json_schema_extra={"example": 86.0})
    waist: float = Field(default=70.0, description="Vòng eo (cm)", json_schema_extra={"example": 70.0})
    hip: float = Field(default=92.0, description="Vòng hông (cm)", json_schema_extra={"example": 92.0})


class RecommendFitRequest(BaseModel):
    product_id: Optional[str] = Field(
        default="uniqlo_jk_01",
        description="Mã định danh áo khoác trong catalog (VD: uniqlo_jk_01, zara_jk_01, hm_jk_01)",
        json_schema_extra={"example": "uniqlo_jk_01"}
    )
    measurements: UserMeasurementsInput = Field(
        default_factory=UserMeasurementsInput,
        description="Số đo cơ thể người dùng"
    )
    fit_preference: Optional[str] = Field(
        default="regular",
        description="Sở thích phom mặc: 'regular' (Vừa vặn) | 'tight' (Ôm gọn) | 'loose' (Thoải mái/Rộng)",
        json_schema_extra={"example": "regular"}
    )


class CompareSizesInputRequest(BaseModel):
    product_id: Optional[str] = Field(
        default="uniqlo_jk_01",
        description="Mã sản phẩm muốn so sánh size",
        json_schema_extra={"example": "uniqlo_jk_01"}
    )
    size_a: str = Field(default="M", description="Size chính cần so sánh (size được đề xuất)", json_schema_extra={"example": "M"})
    size_b: str = Field(default="L", description="Size phụ muốn đem ra so sánh", json_schema_extra={"example": "L"})
    measurements: Optional[UserMeasurementsInput] = Field(
        default_factory=UserMeasurementsInput,
        description="Số đo cơ thể người dùng"
    )


@router.get("/health", summary="Health check cho Fit Intelligence")
def fit_health():
    return {
        "status": "healthy",
        "engine": "FitMLEngine & ExplanationEngine",
        "products_indexed": len(PRODUCTS_DB),
        "supported_brands": ["Zara", "Uniqlo", "H&M", "Stradivarius", "Pull&Bear"],
        "gemini_api_configured": bool(os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"))
    }


@router.get("/products", summary="Danh sách sản phẩm thời trang (Jackets & Outerwear)")
def list_products(
    brand: Optional[str] = Query(None, description="Zara, Uniqlo, H&M, Stradivarius, Pull&Bear"),
    category: Optional[str] = Query(None, description="phao, dạ, bomber, da, denim, blazer..."),
    gender: Optional[str] = Query(None, description="Nữ, Nam, Unisex"),
    fit_cut: Optional[str] = Query(None, description="regular, slim, oversized"),
    q: Optional[str] = Query(None, description="Từ khóa tìm kiếm")
):
    results = list(PRODUCTS_DB.values())
    if brand:
        results = [p for p in results if p.get("brand", "").lower() == brand.lower()]
    if category:
        results = [p for p in results if category.lower() in p.get("category", "").lower()]
    if gender:
        results = [p for p in results if p.get("gender", "").lower() == gender.lower()]
    if fit_cut:
        results = [p for p in results if p.get("fit_cut", "").lower() == fit_cut.lower()]
    if q:
        query = q.lower()
        results = [p for p in results if query in p.get("product_name", "").lower() or query in p.get("description", "").lower()]

    return {
        "total": len(results),
        "products": results
    }


@router.get("/products/{product_id}", summary="Chi tiết sản phẩm và size chart")
def get_product_detail(product_id: str):
    if product_id not in PRODUCTS_DB:
        raise HTTPException(status_code=404, detail=f"Sản phẩm mã '{product_id}' không tồn tại")
    return PRODUCTS_DB[product_id]


@router.post("/recommend", summary="Đề xuất size áo khoác & giải thích chi tiết (Model 1 & 2)")
def recommend_fit(req: RecommendFitRequest):
    product = PRODUCTS_DB.get(req.product_id) if req.product_id else None
    if not product:
        if PRODUCTS_DB:
            product = next(iter(PRODUCTS_DB.values()))
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Product database empty")

    user_meas_dict = req.measurements.model_dump() if hasattr(req.measurements, "model_dump") else req.measurements.dict()

    fit_result = FitMLEngine.recommend(
        user_meas=user_meas_dict,
        garment=product,
        preference=req.fit_preference or "regular"
    )

    explanation = ExplanationEngine.generate(
        fit_result=fit_result,
        user_meas=user_meas_dict,
        garment=product,
        preference=req.fit_preference or "regular"
    )

    return {
        "product_id": product.get("id"),
        "product_name": product.get("product_name"),
        "brand": product.get("brand"),
        "category": product.get("category"),
        "price_vnd": product.get("price_vnd"),
        "local_image_path": product.get("local_image_path"),
        "recommended_size": fit_result["recommended_size"],
        "alternative_size": fit_result.get("alternative_size", "L"),
        "confidence": fit_result["confidence"],
        "confidence_label": f"Độ tin cậy {fit_result['confidence']}% · Vừa vặn",
        "headline": explanation["headline"],
        "why_text": explanation["why_text"],
        "zones": fit_result["zones"],
        "details": explanation["details"],
        "advisory": explanation["advisory"],
        "comparison": explanation["comparison"],
        "calculation_info": explanation["calculation_info"],
        "ml_probabilities": fit_result.get("ml_probabilities", {}),
        "model_metadata": fit_result.get("model_metadata", {})
    }


@router.post("/compare-sizes", summary="So sánh 2 size áo trực quan (Figma S07)")
def compare_sizes(req: CompareSizesInputRequest):
    product = PRODUCTS_DB.get(req.product_id)
    if not product:
        if PRODUCTS_DB:
            product = next(iter(PRODUCTS_DB.values()))
        else:
            raise HTTPException(status_code=404, detail="Sản phẩm không tồn tại")

    user_meas_dict = req.measurements.model_dump() if hasattr(req.measurements, "model_dump") else req.measurements.dict() if req.measurements else {
        "height": 165.0, "weight": 56.0, "shoulder": 39.0, "bust": 86.0, "waist": 70.0, "hip": 92.0
    }

    return ExplanationEngine.compare_two_sizes(
        garment=product,
        user_meas=user_meas_dict,
        size_a=req.size_a,
        size_b=req.size_b
    )
