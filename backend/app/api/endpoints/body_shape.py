"""
Endpoints for 3D Parametric Human Body Generation and Anthropometric Analysis.
Centralized from external_services/body-shape.
"""

import os
import time
from typing import Optional, Literal
from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
import trimesh

from app.services.body_shape.src.config_loader import load_config
from app.services.body_shape.src.schemas.measurements import BodyMeasurements
from app.services.body_shape.src.body_model.mesh3d import ParametricBody3D

router = APIRouter()
config = load_config()

STATIC_INDEX_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "services",
    "body_shape",
    "src",
    "api",
    "static",
    "index.html"
)


@router.get("/studio", response_class=HTMLResponse, summary="Giao diện trực quan 3D Body Studio")
def serve_studio_ui():
    """Phục vụ giao diện tương tác 3D Web Studio."""
    if os.path.exists(STATIC_INDEX_PATH):
        with open(STATIC_INDEX_PATH, "r", encoding="utf-8") as f:
            content = f.read()
            # Cập nhật API route trong JS sang prefix /api/v1/body-shape
            content = content.replace("'/api/v1/body/generate'", "'/api/v1/body-shape/generate'")
            content = content.replace("'/api/v1/body/export/obj'", "'/api/v1/body-shape/export/obj'")
            content = content.replace("'/static/models/'", "'/static/body_shape/models/'")
            return HTMLResponse(content=content)
    return HTMLResponse("<h2>3D Body Studio index.html not found</h2>", status_code=404)


class Body3DGenerationRequest(BaseModel):
    gender: Literal["female", "male"] = Field(default="female", description="Gender of the human avatar")
    height_cm: float = Field(default=165.0, ge=100.0, le=250.0, description="Height in cm")
    weight_kg: Optional[float] = Field(default=58.0, ge=25.0, le=300.0, description="Weight in kg")
    shoulder_width_cm: Optional[float] = Field(default=None, description="Biacromial shoulder width in cm")
    bust_cm: Optional[float] = Field(default=None, description="Bust / Chest circumference in cm")
    waist_cm: Optional[float] = Field(default=None, description="Waist circumference in cm")
    hip_cm: Optional[float] = Field(default=None, description="Hip circumference in cm")
    arm_length_cm: Optional[float] = Field(default=None, description="Arm length in cm")
    leg_length_cm: Optional[float] = Field(default=None, description="Leg inseam length in cm")
    skin_tone: Optional[str] = Field(default="natural", description="Skin tone: fair, natural, tan, deep")

    model_config = {
        "json_schema_extra": {
            "example": {
                "gender": "female",
                "height_cm": 168.0,
                "weight_kg": 56.0,
                "shoulder_width_cm": 38.0,
                "bust_cm": 88.0,
                "waist_cm": 64.0,
                "hip_cm": 92.0,
                "skin_tone": "natural"
            }
        }
    }


def _clean_measurements(req: Body3DGenerationRequest) -> BodyMeasurements:
    def clean_num(val):
        return float(val) if (val is not None and val > 0) else None

    return BodyMeasurements(
        gender=req.gender,
        height_cm=float(req.height_cm) if (req.height_cm and req.height_cm >= 100) else 165.0,
        weight_kg=clean_num(req.weight_kg),
        shoulder_width_cm=clean_num(req.shoulder_width_cm),
        bust_cm=clean_num(req.bust_cm),
        waist_cm=clean_num(req.waist_cm),
        hip_cm=clean_num(req.hip_cm),
        arm_length_cm=clean_num(req.arm_length_cm),
        leg_length_cm=clean_num(req.leg_length_cm),
    )


@router.get("/health", summary="Health check cho Realistic 3D Body Studio")
def body_health_check():
    return {
        "status": "online",
        "service": "Realistic 3D Body Studio",
        "engine": "Anatomical Base Mesh + Anthropometric Deformation Engine (NumPy + Trimesh)"
    }


@router.post("/generate", summary="Sinh 3D mesh và thông số giải phẫu theo số đo người dùng")
def generate_body(req: Body3DGenerationRequest):
    t0 = time.time()
    try:
        meas = _clean_measurements(req)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Lỗi số đo không hợp lệ: {str(e)}")

    skin_tone = req.skin_tone or "natural"
    body_3d = ParametricBody3D(meas, config=config, skin_tone=skin_tone)
    body_mesh = body_3d.get_mesh()

    elapsed_ms = round((time.time() - t0) * 1000, 2)

    return {
        "execution_time_ms": elapsed_ms,
        "body_mesh": {
            "vertices": body_mesh.vertices.tolist(),
            "faces": body_mesh.faces.tolist(),
            "normals": body_mesh.vertex_normals.tolist(),
            "colors": body_mesh.visual.vertex_colors[:, :3].tolist() if hasattr(body_mesh.visual, "vertex_colors") else [],
            "uvs": body_3d.uvs.tolist() if getattr(body_3d, "uvs", None) is not None else [],
            "texture_url": f"/static/body_shape/models/{meas.gender}_texture.png",
            "num_vertices": len(body_mesh.vertices),
            "num_faces": len(body_mesh.faces),
            "color": body_3d.skin_color,
        },
        "measurement_tapes": body_3d.get_measurement_tapes(),
        "landmarks": body_3d.get_landmarks_3d(),
        "analysis": body_3d.get_analysis(),
        "measurements_used": {
            "gender": meas.gender,
            "height_cm": meas.height_cm,
            "weight_kg": meas.weight_kg,
            "bust_cm": round(meas.bust_cm, 1) if meas.bust_cm else None,
            "waist_cm": round(meas.waist_cm, 1) if meas.waist_cm else None,
            "hip_cm": round(meas.hip_cm, 1) if meas.hip_cm else None,
            "shoulder_width_cm": round(meas.shoulder_width_cm, 1) if meas.shoulder_width_cm else None,
        }
    }


@router.post("/export/obj", summary="Xuất file 3D mesh định dạng Wavefront .OBJ")
def export_obj(req: Body3DGenerationRequest):
    meas = _clean_measurements(req)
    body_3d = ParametricBody3D(meas, config=config, skin_tone=req.skin_tone or "natural")
    body_mesh = body_3d.get_mesh()

    obj_data = trimesh.exchange.obj.export_obj(body_mesh)
    filename = f"human_body_{meas.gender}_{int(meas.height_cm)}cm.obj"

    return Response(
        content=obj_data,
        media_type="model/obj",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
