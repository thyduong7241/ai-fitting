"""
Hybrid 2-View Stereometry Measurement Engine.
Integrates P2M calibration, linear bones, Ramanujan circumference, priors, and smart fit notes.
"""

import time
from typing import Any, Dict, Optional
import numpy as np

try:
    import cv2
except ImportError:
    cv2 = None

from app.core.mediapipe_detector import detector, PoseDetectionResult
from app.models.vision import BodyMeasurements, MeasurementResponse
from app.services.measurement.p2m_calibrator import calculate_p2m_scale
from app.services.measurement.linear_bones import (
    measure_shoulder_width,
    measure_arm_length,
    measure_inseam,
)
from app.services.measurement.ramanujan_stereometry import ramanujan_circumference
from app.services.measurement.anthropometric_prior import calculate_bmi, get_prior_factors
from app.services.measurement.hybrid_fallback import estimate_missing_depths
from app.services.measurement.smart_fit_notes import classify_body_shape, generate_smart_fit_notes


def decode_image_bytes(image_bytes: bytes) -> Optional[np.ndarray]:
    if cv2 is not None:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img_bgr is not None:
            return cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    return np.zeros((1280, 720, 3), dtype=np.uint8)


def extract_slice_width_px(
    img_rgb: Optional[np.ndarray],
    y_norm: float,
    cx_norm: float,
    min_half_w_px: float,
    max_half_w_px: float,
) -> Optional[float]:
    """
    Extracts body silhouette width at a given normalized height y_norm using horizontal gradient.
    """
    if cv2 is None or img_rgb is None:
        return None
    h, w = img_rgb.shape[:2]
    y = int(np.clip(y_norm * h, 0, h - 1))
    cx = int(np.clip(cx_norm * w, 0, w - 1))

    try:
        gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        sobel_x = cv2.Sobel(blurred, cv2.CV_32F, 1, 0, ksize=3)
        abs_sobel = np.abs(sobel_x[y, :])

        search_min = max(4, int(min_half_w_px))
        search_max = min(w // 2, int(max_half_w_px))

        # Scan left from cx
        left_edge = None
        l_start = max(0, cx - search_max)
        l_end = max(0, cx - search_min)
        if l_end > l_start:
            l_seg = abs_sobel[l_start:l_end]
            if len(l_seg) > 0 and np.max(l_seg) > 12:
                left_edge = cx - (l_start + int(np.argmax(l_seg)))

        # Scan right from cx
        right_edge = None
        r_start = min(w - 1, cx + search_min)
        r_end = min(w - 1, cx + search_max)
        if r_end > r_start:
            r_seg = abs_sobel[r_start:r_end]
            if len(r_seg) > 0 and np.max(r_seg) > 12:
                right_edge = (r_start + int(np.argmax(r_seg))) - cx

        if left_edge and right_edge:
            return float(left_edge + right_edge)
        elif left_edge:
            return float(left_edge * 2.0)
        elif right_edge:
            return float(right_edge * 2.0)
    except Exception:
        pass
    return None


def measure_body(
    front_image_bytes: bytes,
    side_image_bytes: Optional[bytes],
    known_height_cm: float,
    weight_kg: float,
    age: int = 25,
    gender: str = "male",
    options: Optional[Dict[str, Any]] = None,
) -> MeasurementResponse:
    t0 = time.perf_counter()

    # 1. Decode images
    front_img = decode_image_bytes(front_image_bytes)
    h_f, w_f = front_img.shape[:2]

    # 2. Extract Pose landmarks from front image
    front_pose: PoseDetectionResult = detector.detect(front_img)
    if not front_pose.has_person:
        raise ValueError("Cannot detect body landmarks from front image. Please check quality.")

    f_lms = front_pose.landmarks

    # 3. P2M Scale Calibration
    p2m_scale = calculate_p2m_scale(f_lms, h_f, w_f, known_height_cm)

    # 4. Measure linear bones
    shoulder_cm = measure_shoulder_width(f_lms, p2m_scale, w_f, h_f)
    arm_length_cm = measure_arm_length(f_lms, p2m_scale, w_f, h_f)
    inseam_cm = measure_inseam(f_lms, p2m_scale, w_f, h_f)

    # 5. Extract front slice horizontal semi-axes (a = width / 2)
    shoulder_w_px = abs(f_lms[11].x - f_lms[12].x) * w_f
    hip_w_px = abs(f_lms[23].x - f_lms[24].x) * w_f

    a_shoulder = (shoulder_w_px * p2m_scale) / 2.0
    bmi = calculate_bmi(known_height_cm, weight_kg)
    prior_factors = get_prior_factors(age, bmi, gender)

    # Torso landmark geometry
    y_shoulder_norm = (f_lms[11].y + f_lms[12].y) / 2.0
    y_hip_norm = (f_lms[23].y + f_lms[24].y) / 2.0
    torso_h_norm = max(0.15, y_hip_norm - y_shoulder_norm)
    cx_norm = (f_lms[11].x + f_lms[12].x) / 2.0

    # Dynamic slice sampling on front image
    y_chest_norm = y_shoulder_norm + 0.22 * torso_h_norm
    y_waist_norm = y_shoulder_norm + 0.62 * torso_h_norm
    y_hips_norm = y_hip_norm + 0.12 * torso_h_norm

    min_hw = shoulder_w_px * 0.25
    max_hw = shoulder_w_px * 0.95

    w_chest_px = extract_slice_width_px(front_img, y_chest_norm, cx_norm, min_hw, max_hw)
    w_waist_px = extract_slice_width_px(front_img, y_waist_norm, cx_norm, min_hw * 0.8, max_hw)
    w_hips_px = extract_slice_width_px(front_img, y_hips_norm, cx_norm, min_hw, max_hw * 1.2)

    # Calculate actual front semi-axis (a), incorporating measured silhouette + BMI prior
    bmi_waist_mod = min(0.15, max(-0.10, (bmi - 21.0) * 0.012))
    waist_baseline_ratio = (0.78 + bmi_waist_mod) if gender == "female" else (0.84 + bmi_waist_mod)

    if w_chest_px and 0.7 * shoulder_w_px <= w_chest_px <= 1.4 * shoulder_w_px:
        a_chest = (w_chest_px * p2m_scale) / 2.0
    else:
        a_chest = a_shoulder * (0.94 if gender == "female" else 0.98)

    if w_waist_px and 0.5 * shoulder_w_px <= w_waist_px <= 1.3 * shoulder_w_px:
        a_waist = (w_waist_px * p2m_scale) / 2.0
    else:
        a_waist = a_chest * waist_baseline_ratio

    if w_hips_px and 0.7 * hip_w_px <= w_hips_px <= 2.0 * hip_w_px:
        a_hips = (w_hips_px * p2m_scale) / 2.0
    else:
        a_hips = (hip_w_px * p2m_scale * (1.32 if gender == "female" else 1.20)) / 2.0

    # 6. Extract or estimate side depth semi-axes (b = depth / 2)
    method = "hybrid_stereometry_2d"
    is_dual_view = False
    s_lms = None

    if side_image_bytes:
        side_img = decode_image_bytes(side_image_bytes)
        h_s, w_s = side_img.shape[:2]
        side_pose: PoseDetectionResult = detector.detect(side_img)
        if side_pose.has_person:
            p2m_side = calculate_p2m_scale(side_pose.landmarks, h_s, w_s, known_height_cm)
            s_lms = side_pose.landmarks
            is_dual_view = True

            # Extract depth from side silhouette
            s_y_sh = (s_lms[11].y + s_lms[12].y) / 2.0
            s_y_hp = (s_lms[23].y + s_lms[24].y) / 2.0
            s_torso_h = max(0.15, s_y_hp - s_y_sh)
            s_cx = (s_lms[11].x + s_lms[23].x) / 2.0

            side_chest_px = extract_slice_width_px(side_img, s_y_sh + 0.22 * s_torso_h, s_cx, 10, w_s * 0.35)
            side_waist_px = extract_slice_width_px(side_img, s_y_sh + 0.62 * s_torso_h, s_cx, 10, w_s * 0.35)
            side_hips_px = extract_slice_width_px(side_img, s_y_hp + 0.12 * s_torso_h, s_cx, 10, w_s * 0.40)

            b_chest = (side_chest_px * p2m_side / 2.0) if side_chest_px else (a_chest * 0.74 * prior_factors["k_chest"])
            b_waist = (side_waist_px * p2m_side / 2.0) if side_waist_px else (a_waist * 0.70 * prior_factors["k_waist"])
            b_hips = (side_hips_px * p2m_side / 2.0) if side_hips_px else (a_hips * 0.85 * prior_factors["k_hips"])
        else:
            depths = estimate_missing_depths(a_chest, a_waist, a_hips, prior_factors, gender)
            b_chest, b_waist, b_hips = depths["b_chest"], depths["b_waist"], depths["b_hips"]
    else:
        # Fallback to single-view hybrid regression
        depths = estimate_missing_depths(a_chest, a_waist, a_hips, prior_factors, gender)
        b_chest, b_waist, b_hips = depths["b_chest"], depths["b_waist"], depths["b_hips"]
        method = "hybrid_stereometry_2d"

    # 7. Circumference calculation via Ramanujan formula
    chest_cm = round(ramanujan_circumference(a_chest, b_chest), 1)
    waist_cm = round(ramanujan_circumference(a_waist, b_waist), 1)
    hips_cm = round(ramanujan_circumference(a_hips, b_hips), 1)
    whr = round(waist_cm / hips_cm, 2) if hips_cm > 0 else 0.8

    # 8. Benchmark-Calibrated Confidence Score Calculation
    # Baseline from quantitative benchmark (FINAL_BENCHMARK_REPORT.md):
    # - Dual-view: 93.3% pass rate (MAE 1.72cm)
    # - Single-view fallback: 87.5% (MAE 2.30cm)
    benchmark_base = 93.3 if is_dual_view else 87.5
    key_indices = [0, 11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28]
    vis_list = [f_lms[i].visibility for i in key_indices if i < len(f_lms)]
    avg_vis_front = sum(vis_list) / len(vis_list) if vis_list else 0.90
    landmark_factor = (avg_vis_front - 0.90) * 10.0

    side_factor = 0.0
    avg_vis_side = 0.0
    if is_dual_view and s_lms:
        side_indices = [11, 12, 23, 24, 27, 28]
        side_vis = [s_lms[i].visibility for i in side_indices if i < len(s_lms)]
        avg_vis_side = sum(side_vis) / len(side_vis) if side_vis else 0.85
        side_factor = (avg_vis_side - 0.85) * 6.0

    s_h_ratio = shoulder_cm / known_height_cm if known_height_cm > 0 else 0.24
    i_h_ratio = inseam_cm / known_height_cm if known_height_cm > 0 else 0.45
    coherence_bonus = 1.0 if (0.20 <= s_h_ratio <= 0.28 and 0.38 <= i_h_ratio <= 0.52 and 0.65 <= whr <= 1.15) else 0.0

    raw_confidence = benchmark_base + landmark_factor + side_factor + coherence_bonus
    confidence = max(84.0, min(96.5, raw_confidence)) if is_dual_view else max(75.0, min(89.0, raw_confidence))
    confidence = round(confidence, 1)

    measurements = BodyMeasurements(
        height_cm=known_height_cm,
        weight_kg=weight_kg,
        shoulder_cm=shoulder_cm,
        chest_cm=chest_cm,
        waist_cm=waist_cm,
        hips_cm=hips_cm,
        arm_length_cm=arm_length_cm,
        inseam_cm=inseam_cm,
    )

    # 9. Body Shape Classification & Smart Fit Notes
    body_shape = classify_body_shape(shoulder_cm, chest_cm, waist_cm, hips_cm, gender)
    smart_fit_notes = generate_smart_fit_notes(body_shape, measurements, gender, bmi)

    dt_ms = (time.perf_counter() - t0) * 1000

    return MeasurementResponse(
        measurements=measurements,
        confidence_percent=confidence,
        method=method,
        body_shape=body_shape,
        smart_fit_notes=smart_fit_notes,
        engine_id="hybrid_stereometry_2d",
        metrics={
            "bmi": bmi,
            "whr": whr,
            "p2m_scale": round(p2m_scale, 4),
            "benchmark_baseline": benchmark_base,
            "landmark_visibility_pct": round(avg_vis_front * 100, 1),
            "side_visibility_pct": round(avg_vis_side * 100, 1) if is_dual_view else None,
            "is_dual_view": is_dual_view,
            "expected_mae_cm": 1.7 if is_dual_view else 2.3,
        },
        latency_ms=round(dt_ms, 2),
    )
