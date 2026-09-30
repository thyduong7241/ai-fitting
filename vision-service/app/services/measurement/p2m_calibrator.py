"""
Pixel-to-Metric (P2M) Calibrator.
Computes metric scale (cm/pixel) from known user height and vertical landmark span.
"""

import math
from typing import List, Tuple
from app.core.mediapipe_detector import LandmarkPoint


def calculate_p2m_scale(
    landmarks: List[LandmarkPoint],
    image_height: int,
    image_width: int,
    known_height_cm: float,
) -> float:
    """
    Calculate cm per pixel scale.
    """
    nose = landmarks[0]
    left_ear, right_ear = landmarks[7], landmarks[8]
    ear_y = (left_ear.y + right_ear.y) / 2.0
    head_height_est = max(0.04, abs(ear_y - nose.y) * 2.2)
    crown_y = max(0.0, nose.y - head_height_est)

    # Heels (29, 30) or Ankles (27, 28)
    heel_y = (landmarks[29].y + landmarks[30].y) / 2.0
    if heel_y < 0.80:
        # Fallback to ankles if heels are occluded
        heel_y = (landmarks[27].y + landmarks[28].y) / 2.0 + 0.04

    pixel_height = abs(heel_y - crown_y) * image_height
    if pixel_height < 100:
        pixel_height = image_height * 0.88  # Safe fallback estimate

    scale_cm_per_pixel = known_height_cm / pixel_height
    return scale_cm_per_pixel


def landmark_distance_cm(
    pt1: LandmarkPoint,
    pt2: LandmarkPoint,
    scale_cm_per_pixel: float,
    image_width: int,
    image_height: int,
) -> float:
    """Euclidean distance between two landmarks in centimeters."""
    dx = (pt1.x - pt2.x) * image_width
    dy = (pt1.y - pt2.y) * image_height
    dist_pixels = math.sqrt(dx * dx + dy * dy)
    return dist_pixels * scale_cm_per_pixel
