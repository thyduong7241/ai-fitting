"""2D spline interpolation and geometry generation for body contours."""

import numpy as np
from typing import List, Tuple
from ..body_model.parameters import BodyParameters


def catmull_rom_spline(control_points: List[Tuple[float, float]], num_samples: int = 20) -> List[Tuple[float, float]]:
    """
    Interpolate a set of 2D control points using a cubic Catmull-Rom spline.
    Guarantees the curve smoothly passes through all control points.
    """
    if len(control_points) < 2:
        return list(control_points)
    if len(control_points) == 2:
        pts = []
        for i in range(num_samples):
            t = i / (num_samples - 1)
            x = (1 - t) * control_points[0][0] + t * control_points[1][0]
            y = (1 - t) * control_points[0][1] + t * control_points[1][1]
            pts.append((x, y))
        return pts

    # Duplicate end points to handle boundaries naturally
    pts = [control_points[0]] + list(control_points) + [control_points[-1]]
    curve = []

    for i in range(1, len(pts) - 2):
        p0 = np.array(pts[i - 1])
        p1 = np.array(pts[i])
        p2 = np.array(pts[i + 1])
        p3 = np.array(pts[i + 2])

        for j in range(num_samples if i < len(pts) - 3 else num_samples + 1):
            t = j / num_samples
            t2 = t * t
            t3 = t2 * t

            # Standard Catmull-Rom matrix blending
            pos = 0.5 * (
                (2 * p1) +
                (-p0 + p2) * t +
                (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 +
                (-p0 + 3 * p1 - 3 * p2 + p3) * t3
            )
            curve.append((float(pos[0]), float(pos[1])))

    return curve


def generate_torso_contour(params: BodyParameters, center_x: float, top_y: float, total_height: float) -> List[Tuple[float, float]]:
    """
    Build control points and spline curve for the head and torso.
    Returns closed polygon coordinates in pixel space.
    """
    H = total_height
    c_x = center_x

    # Smooth oval head control points
    # (x, y) relative to center_x, top_y
    right_points = [
        # Head top (slight rounded curve, not a pointy tip)
        (c_x, top_y + params.y_head_top * H),
        (c_x + params.w_head * 0.7 * H, top_y + (params.y_head_top + 0.02) * H),
        (c_x + params.w_head * H, top_y + (params.y_head_top + params.y_chin) * 0.45 * H),
        (c_x + params.w_head * 0.9 * H, top_y + (params.y_head_top + params.y_chin) * 0.75 * H),
        # Chin/Jaw
        (c_x + params.w_neck * 1.3 * H, top_y + params.y_chin * H),
        # Neck
        (c_x + params.w_neck * H, top_y + params.y_neck * H),
        # Shoulder
        (c_x + params.w_shoulder * H, top_y + params.y_shoulder * H),
        # Armpit
        (c_x + params.w_armpit * H, top_y + params.y_armpit * H),
        # Bust
        (c_x + params.w_bust * H, top_y + params.y_bust * H),
        # Waist
        (c_x + params.w_waist * H, top_y + params.y_waist * H),
        # High hip
        (c_x + params.w_high_hip * H, top_y + params.y_high_hip * H),
        # Hip
        (c_x + params.w_hip * H, top_y + params.y_hip * H),
        # Lower pelvis
        (c_x + params.w_hip * 0.65 * H, top_y + (params.y_hip + params.y_crotch) * 0.5 * H),
        # Crotch center
        (c_x, top_y + params.y_crotch * H),
    ]

    # Generate smooth curve along right side
    right_curve = catmull_rom_spline(right_points, num_samples=16)

    # Mirror for left side
    left_curve = [(2 * c_x - x, y) for (x, y) in reversed(right_curve)]

    return right_curve + left_curve


def generate_leg_contour(params: BodyParameters, center_x: float, top_y: float, total_height: float, side: str = "right") -> List[Tuple[float, float]]:
    """
    Generate polygon for a single leg (left or right).
    """
    H = total_height
    sign = 1.0 if side == "right" else -1.0
    c_x = center_x

    # Leg axis offset from center
    leg_axis_w = params.w_hip * 0.48

    outer_points = [
        (c_x + sign * (leg_axis_w + params.w_thigh * 0.9) * H, top_y + (params.y_crotch - 0.02) * H),
        (c_x + sign * (leg_axis_w + params.w_thigh * 0.8) * H, top_y + params.y_thigh * H),
        (c_x + sign * (leg_axis_w + params.w_knee * 0.65) * H, top_y + params.y_knee * H),
        (c_x + sign * (leg_axis_w + params.w_calf * 0.7) * H, top_y + params.y_calf * H),
        (c_x + sign * (leg_axis_w + params.w_ankle * 0.6) * H, top_y + params.y_ankle * H),
        (c_x + sign * (leg_axis_w + params.w_foot * 0.75) * H, top_y + params.y_feet * H),
        # Foot bottom
        (c_x + sign * (leg_axis_w - params.w_foot * 0.4) * H, top_y + params.y_feet * H),
    ]

    inner_points = [
        (c_x + sign * (leg_axis_w - params.w_ankle * 0.5) * H, top_y + params.y_ankle * H),
        (c_x + sign * (leg_axis_w - params.w_calf * 0.5) * H, top_y + params.y_calf * H),
        (c_x + sign * (leg_axis_w - params.w_knee * 0.5) * H, top_y + params.y_knee * H),
        (c_x + sign * (leg_axis_w - params.w_thigh * 0.55) * H, top_y + params.y_thigh * H),
        (c_x + sign * (params.w_crotch_gap * 0.6) * H, top_y + params.y_crotch * H),
    ]

    outer_curve = catmull_rom_spline(outer_points, num_samples=14)
    inner_curve = catmull_rom_spline(inner_points, num_samples=14)

    return outer_curve + inner_curve


def generate_arm_contour(params: BodyParameters, center_x: float, top_y: float, total_height: float, side: str = "right") -> List[Tuple[float, float]]:
    """
    Generate polygon for an arm resting naturally beside the torso.
    """
    H = total_height
    sign = 1.0 if side == "right" else -1.0
    c_x = center_x

    # Shoulder anchor point
    shoulder_pt_x = c_x + sign * params.w_shoulder * H
    shoulder_pt_y = top_y + params.y_shoulder * H

    # Torso clearance: arms hang alongside the body contours
    upper_arm_x = c_x + sign * (max(params.w_shoulder * 0.92, params.w_bust * 1.05) + params.w_upper_arm * 0.8) * H
    elbow_x = c_x + sign * (params.w_waist + params.w_upper_arm * 1.1) * H
    wrist_x = c_x + sign * (params.w_hip * 0.95 + params.w_forearm * 1.0) * H
    hand_x = c_x + sign * (params.w_thigh * 0.9 + params.w_hip * 0.45) * H

    y_wrist = params.y_crotch + 0.02
    y_fingertips = y_wrist + 0.08

    outer_points = [
        (shoulder_pt_x, shoulder_pt_y),
        (upper_arm_x + sign * params.w_upper_arm * 0.5 * H, top_y + (params.y_shoulder + params.y_elbow) * 0.5 * H),
        (elbow_x + sign * params.w_upper_arm * 0.4 * H, top_y + params.y_elbow * H),
        (wrist_x + sign * params.w_forearm * 0.35 * H, top_y + y_wrist * H),
        (hand_x + sign * params.w_hand * 0.3 * H, top_y + y_fingertips * H),
        (hand_x, top_y + y_fingertips * H),
    ]

    inner_points = [
        (hand_x - sign * params.w_hand * 0.3 * H, top_y + y_wrist * H),
        (wrist_x - sign * params.w_forearm * 0.35 * H, top_y + (y_wrist - 0.04) * H),
        (elbow_x - sign * params.w_upper_arm * 0.4 * H, top_y + params.y_elbow * H),
        (c_x + sign * params.w_armpit * H, top_y + params.y_armpit * H),
    ]

    outer_curve = catmull_rom_spline(outer_points, num_samples=12)
    inner_curve = catmull_rom_spline(inner_points, num_samples=12)

    return outer_curve + inner_curve
