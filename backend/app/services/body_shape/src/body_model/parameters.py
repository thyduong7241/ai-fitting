"""Convert physical measurements into normalized 2D body parameters."""

import math
from dataclasses import dataclass
from ..schemas.measurements import BodyMeasurements


@dataclass
class BodyParameters:
    """
    Normalized body parameters expressed relative to total height.
    All vertical positions (y) and half-widths (w) are in [0, 1] relative to height.
    """
    # Vertical landmarks (fraction of total height from top of head)
    y_head_top: float = 0.0
    y_chin: float = 0.130
    y_neck: float = 0.155
    y_shoulder: float = 0.180
    y_armpit: float = 0.230
    y_bust: float = 0.280
    y_waist: float = 0.400
    y_high_hip: float = 0.470
    y_hip: float = 0.520
    y_crotch: float = 0.540
    y_thigh: float = 0.620
    y_knee: float = 0.720
    y_calf: float = 0.830
    y_ankle: float = 0.940
    y_feet: float = 1.000

    # Arm vertical landmarks
    y_elbow: float = 0.380
    y_wrist: float = 0.550
    y_fingertips: float = 0.650

    # Normalized half-widths (fraction of total height from center line x=0)
    w_head: float = 0.048
    w_neck: float = 0.024
    w_shoulder: float = 0.115
    w_armpit: float = 0.095
    w_bust: float = 0.085
    w_waist: float = 0.065
    w_high_hip: float = 0.082
    w_hip: float = 0.092
    w_crotch_gap: float = 0.012
    w_thigh: float = 0.055
    w_knee: float = 0.038
    w_calf: float = 0.040
    w_ankle: float = 0.025
    w_foot: float = 0.032

    # Arm half-widths
    w_upper_arm: float = 0.025
    w_forearm: float = 0.022
    w_hand: float = 0.018


def calculate_parameters(meas: BodyMeasurements) -> BodyParameters:
    """
    Convert 3D/tape measurements to 2D normalized half-widths and vertical positions.
    Formula for converting circumference to half-width:
    width = circumference / pi (approximate cross section)
    half_width = width / 2 = circumference / (2 * pi)
    normalized_half_width = half_width / height
    """
    H = meas.height_cm
    params = BodyParameters()

    # If leg length is specified, adjust crotch and lower body landmarks
    if meas.leg_length_cm:
        leg_fraction = meas.leg_length_cm / H
        # Crotch y is 1.0 - leg_fraction
        y_crotch = max(0.48, min(0.60, 1.0 - leg_fraction))
        params.y_crotch = y_crotch
        params.y_hip = y_crotch - 0.025
        params.y_high_hip = y_crotch - 0.070
        params.y_waist = y_crotch - 0.140
        params.y_knee = y_crotch + (1.0 - y_crotch) * 0.40
        params.y_calf = y_crotch + (1.0 - y_crotch) * 0.65
        params.y_ankle = y_crotch + (1.0 - y_crotch) * 0.88

    # 1. Shoulder width:
    # shoulder_width_cm is a direct cross-body linear distance (biacromial diameter).
    # It directly sets half-width w_shoulder = (shoulder_width_cm / 2) / H.
    if meas.shoulder_width_cm:
        params.w_shoulder = (meas.shoulder_width_cm / 2.0) / H
    elif meas.shoulder_cm:
        # If user passed shoulder_cm as a linear width (< 60cm) or circumference
        if meas.shoulder_cm < 60:
            params.w_shoulder = (meas.shoulder_cm / 2.0) / H
        else:
            params.w_shoulder = (meas.shoulder_cm / 2.6 / 2.0) / H

    # 2. Circumference to Frontal 2D Half-Width Mapping:
    # Anthropometric cross-sections are ellipses where:
    #   Perimeter P ≈ π * [ 3(a+b) - sqrt((3a+b)(a+3b)) ] ≈ 2π * sqrt((a^2 + b^2)/2)
    # In frontal view, we observe semi-major axis 'a'.
    # Ratio r = a / b (transverse frontal diameter / anteroposterior depth):
    # - Bust / Thorax: r ≈ 1.35  => a ≈ 0.190 * P  (vs circular 0.159 * P) -> frontal factor ≈ 1.18
    # - Waist: r ≈ 1.25          => a ≈ 0.180 * P  -> frontal factor ≈ 1.14
    # - Hip / Pelvis: r ≈ 1.40   => a ≈ 0.198 * P  -> frontal factor ≈ 1.22
    #
    # Thus:
    # half_width_cm = a = (circumference / (2 * pi)) * frontal_ratio
    # normalized_half_width = half_width_cm / H

    BUST_FRONTAL_RATIO = 1.18
    WAIST_FRONTAL_RATIO = 1.14
    HIP_FRONTAL_RATIO = 1.22

    if meas.bust_cm:
        w_bust_cm = (meas.bust_cm / (2.0 * math.pi)) * BUST_FRONTAL_RATIO
        params.w_bust = w_bust_cm / H

    if meas.waist_cm:
        w_waist_cm = (meas.waist_cm / (2.0 * math.pi)) * WAIST_FRONTAL_RATIO
        params.w_waist = w_waist_cm / H

    if meas.hip_cm:
        w_hip_cm = (meas.hip_cm / (2.0 * math.pi)) * HIP_FRONTAL_RATIO
        params.w_hip = w_hip_cm / H
        # High hip is transition zone between waist and full hip
        params.w_high_hip = params.w_waist + (params.w_hip - params.w_waist) * 0.60
        # Upper thigh relates to hip width
        params.w_thigh = params.w_hip * 0.56

    # Neck is proportional to waist/torso width, clamped to aesthetic bounds
    params.w_neck = max(0.022, min(0.035, params.w_waist * 0.38))
    params.w_armpit = params.w_bust * 1.02

    # Arms length adjustment if provided
    if meas.arm_length_cm:
        arm_frac = meas.arm_length_cm / H
        params.y_wrist = params.y_shoulder + arm_frac
        params.y_elbow = params.y_shoulder + arm_frac * 0.52
        params.y_fingertips = params.y_wrist + 0.10

    # Ensure thigh/knee/ankle scale gently with hip & bust
    scale = (params.w_hip / 0.092)
    params.w_knee = 0.038 * (0.5 + 0.5 * scale)
    params.w_calf = 0.040 * (0.5 + 0.5 * scale)
    params.w_ankle = 0.025 * (0.6 + 0.4 * scale)

    return params
