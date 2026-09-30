"""
Linear bone distance extraction:
- Bi-acromial Shoulder Width (with 1.10 deltoid muscle compensation)
- 3-joint Arm Length (Shoulder -> Elbow -> Wrist)
- Inseam Leg Length (Perineum / Crotch -> Knee -> Ankle)
"""

from typing import List, Tuple
from app.core.mediapipe_detector import LandmarkPoint
from app.services.measurement.p2m_calibrator import landmark_distance_cm


def measure_shoulder_width(
    landmarks: List[LandmarkPoint],
    scale_cm_per_pixel: float,
    image_width: int,
    image_height: int,
) -> float:
    """
    Bi-acromial shoulder width (Landmarks 11 & 12).
    Includes 1.10 multiplier to account for lateral deltoid muscle curvature.
    """
    left_shoulder = landmarks[11]
    right_shoulder = landmarks[12]
    dist_raw = landmark_distance_cm(
        left_shoulder, right_shoulder, scale_cm_per_pixel, image_width, image_height
    )
    # Deltoid muscle padding (10%)
    shoulder_cm = dist_raw * 1.10
    return round(shoulder_cm, 1)


def measure_arm_length(
    landmarks: List[LandmarkPoint],
    scale_cm_per_pixel: float,
    image_width: int,
    image_height: int,
) -> float:
    """
    3-joint arm length: Shoulder (11) -> Elbow (13) -> Wrist (15).
    """
    # Average left and right arm for symmetry stability
    left_upper = landmark_distance_cm(landmarks[11], landmarks[13], scale_cm_per_pixel, image_width, image_height)
    left_lower = landmark_distance_cm(landmarks[13], landmarks[15], scale_cm_per_pixel, image_width, image_height)

    right_upper = landmark_distance_cm(landmarks[12], landmarks[14], scale_cm_per_pixel, image_width, image_height)
    right_lower = landmark_distance_cm(landmarks[14], landmarks[16], scale_cm_per_pixel, image_width, image_height)

    left_arm = left_upper + left_lower
    right_arm = right_upper + right_lower
    avg_arm = (left_arm + right_arm) / 2.0
    return round(avg_arm, 1)


def measure_inseam(
    landmarks: List[LandmarkPoint],
    scale_cm_per_pixel: float,
    image_width: int,
    image_height: int,
) -> float:
    """
    Inseam leg length from crotch level to medial malleolus ankle.
    """
    # Crotch approximate: midpoint between hips (23, 24)
    hip_y = (landmarks[23].y + landmarks[24].y) / 2.0
    hip_x = (landmarks[23].x + landmarks[24].x) / 2.0
    crotch = LandmarkPoint(hip_x, hip_y, 0.0, 1.0)

    # Knee (25) -> Ankle (27)
    left_thigh = landmark_distance_cm(crotch, landmarks[25], scale_cm_per_pixel, image_width, image_height)
    left_calf = landmark_distance_cm(landmarks[25], landmarks[27], scale_cm_per_pixel, image_width, image_height)

    right_thigh = landmark_distance_cm(crotch, landmarks[26], scale_cm_per_pixel, image_width, image_height)
    right_calf = landmark_distance_cm(landmarks[26], landmarks[28], scale_cm_per_pixel, image_width, image_height)

    avg_inseam = ((left_thigh + left_calf) + (right_thigh + right_calf)) / 2.0
    return round(avg_inseam, 1)
