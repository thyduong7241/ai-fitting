"""High-level public interface for the Body Fit feature."""

from typing import Optional, Union, Dict, Any, Literal
from PIL import Image

from .schemas.measurements import BodyMeasurements
from .body_model.parameters import BodyParameters, calculate_parameters
from .generator.renderer import BodyRenderer


def generate_body(
    height_cm: Union[float, Dict[str, Any]] = 165.0,
    weight_kg: Optional[float] = None,
    shoulder_width_cm: Optional[float] = None,
    bust_cm: Optional[float] = None,
    waist_cm: Optional[float] = None,
    hip_cm: Optional[float] = None,
    arm_length_cm: Optional[float] = None,
    leg_length_cm: Optional[float] = None,
    gender: Literal["female", "male"] = "female",
    seed: Optional[int] = 42,
    output_path: Optional[str] = None,
    width: int = 600,
    height: int = 1000,
    reference_height_cm: Optional[float] = None,
    return_3d: bool = False,
    **kwargs
) -> Union[Image.Image, Dict[str, Any]]:
    """
    Generate a 2D or 3D full-body human illustration / mesh whose proportions reflect input measurements.
    """
    # 0. Handle dictionary passed as first argument
    if isinstance(height_cm, dict):
        data = dict(height_cm)
        gender = data.get("gender", gender)
        weight_kg = data.get("weight_kg", weight_kg)
        shoulder_width_cm = data.get("shoulder_width_cm", data.get("shoulder_cm", shoulder_width_cm))
        bust_cm = data.get("bust_cm", bust_cm)
        waist_cm = data.get("waist_cm", waist_cm)
        hip_cm = data.get("hip_cm", hip_cm)
        arm_length_cm = data.get("arm_length_cm", arm_length_cm)
        leg_length_cm = data.get("leg_length_cm", leg_length_cm)
        height_val = float(data.get("height_cm", data.get("height", 165.0)))
    else:
        height_val = float(height_cm)

    # 1. Validation & Anthropometric Defaulting
    meas = BodyMeasurements(
        gender=gender,
        height_cm=height_val,
        weight_kg=float(weight_kg) if weight_kg is not None else None,
        shoulder_width_cm=float(shoulder_width_cm) if shoulder_width_cm is not None else None,
        bust_cm=float(bust_cm) if bust_cm is not None else None,
        waist_cm=float(waist_cm) if waist_cm is not None else None,
        hip_cm=float(hip_cm) if hip_cm is not None else None,
        arm_length_cm=float(arm_length_cm) if arm_length_cm is not None else None,
        leg_length_cm=float(leg_length_cm) if leg_length_cm is not None else None,
    )

    # 2. 3D Body Mesh Construction
    from .body_model.mesh3d import ParametricBody3D
    body_3d = ParametricBody3D(meas)

    if return_3d:
        mesh = body_3d.get_mesh()
        return {
            "body": {
                "num_vertices": len(mesh.vertices),
                "num_faces": len(mesh.faces),
                "vertices": mesh.vertices.tolist(),
                "faces": mesh.faces.tolist(),
            },
            "landmarks": body_3d.get_landmarks_3d(),
            "measurement_tapes": body_3d.get_measurement_tapes(),
            "analysis": body_3d.get_analysis()
        }

    # 3. 2D Rendering
    renderer = BodyRenderer(image_size=(width, height), seed=seed)
    params = calculate_parameters(meas)
    img = renderer.render(
        params=params,
        height_cm=meas.height_cm,
        reference_height_cm=reference_height_cm
    )

    if output_path:
        import os
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        img.save(output_path, "PNG")

    return img
