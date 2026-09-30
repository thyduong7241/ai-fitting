"""
Single-Pass Quality Gate Service for Vision Pipeline.
Evaluates 6 verification layers in < 30ms on CPU:
1. Resolution Gate (H >= 800, W >= 600)
2. Person Presence Check
3. Edge Cut-Off (Crown & Heel / Toe)
4. Keypoint Visibility Occlusion Check
5. Pose Orientation Check (Front / Side alignment)
6. Fast OpenCV ROI Blur & Lighting Variance
"""

import time
from typing import List, Optional, Tuple
import numpy as np

try:
    import cv2
except ImportError:
    cv2 = None

from app.core.mediapipe_detector import detector, PoseDetectionResult
from app.models.vision import QualityCheckResponse, QualityIssue


def evaluate_quality(
    image_bytes: bytes,
    image_type: str = "front",
) -> QualityCheckResponse:
    t0 = time.perf_counter()
    issues: List[QualityIssue] = []

    # 0. Decode image bytes to NumPy RGB
    if cv2 is not None:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img_bgr is None:
            return QualityCheckResponse(
                is_valid=False,
                confidence_score=0.0,
                issues=[QualityIssue(code="blurry", severity="error", message="Không thể giải mã dữ liệu ảnh")],
                blur_score=0.0,
                landmarks_detected=0,
                engine_id="opencv_mediapipe",
                latency_ms=0.0,
            )
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    else:
        # Fallback dummy RGB
        img_rgb = np.zeros((1280, 720, 3), dtype=np.uint8)

    h, w = img_rgb.shape[:2]

    # 1. Resolution Gate
    if h < 800 or w < 600:
        issues.append(
            QualityIssue(
                code="low_resolution",
                severity="error",
                message=f"Độ phân giải ảnh ({w}x{h}) quá thấp. Yêu cầu tối thiểu 600x800 pixel.",
            )
        )

    # 2. MediaPipe Pose Landmarker Single-Pass
    pose_res: PoseDetectionResult = detector.detect(img_rgb)
    landmarks = pose_res.landmarks
    landmarks_count = len(landmarks) if landmarks else 0

    if not pose_res.has_person:
        issues.append(
            QualityIssue(
                code="no_person",
                severity="error",
                message="Không phát hiện người trong khung hình. Vui lòng chụp rõ toàn thân.",
            )
        )
        dt_ms = (time.perf_counter() - t0) * 1000
        return QualityCheckResponse(
            is_valid=False,
            confidence_score=0.0,
            issues=issues,
            blur_score=0.0,
            landmarks_detected=0,
            engine_id="opencv_mediapipe",
            latency_ms=round(dt_ms, 2),
        )

    # 3. Edge Cut-Off Check (Crown & Feet)
    # Head crown estimation using robust nose-to-shoulder proportion
    nose = landmarks[0]
    left_shoulder, right_shoulder = landmarks[11], landmarks[12]
    mid_shoulder_y = (left_shoulder.y + right_shoulder.y) / 2.0
    head_span = max(0.05, mid_shoulder_y - nose.y)
    crown_y = nose.y - (head_span * 0.55)

    if crown_y <= 0.005 or nose.y <= 0.05:
        issues.append(
            QualityIssue(
                code="head_cut_off",
                severity="error",
                message="Đỉnh đầu bị chạm mép hoặc cắt ngoài khung hình. Vui lòng lùi ra xa.",
                box=[0.0, max(0.0, nose.x - 0.2), min(1.0, nose.y + 0.1), min(1.0, nose.x + 0.2)],
            )
        )

    # Feet cut-off: Only strictly enforced for front image (Side view uses P2M scale calibrated from Front)
    if image_type == "front":
        # 27/28: Ankles, 29/30: Heels, 31/32: Foot indices (toes)
        feet_indices = [27, 28, 29, 30, 31, 32]
        max_feet_y = max(landmarks[idx].y for idx in feet_indices)
        # Check primary foot visibility (ankles 27, 28 and toes 31, 32)
        primary_feet_indices = [27, 28, 31, 32]
        min_primary_vis = min(landmarks[idx].visibility for idx in primary_feet_indices)
        avg_feet_vis = sum(landmarks[idx].visibility for idx in feet_indices) / len(feet_indices)

        # Trigger cut-off only if feet touch border (y >= 0.985) or feet are genuinely occluded/invisible
        if max_feet_y >= 0.985 or (min_primary_vis < 0.25 and avg_feet_vis < 0.35):
            issues.append(
                QualityIssue(
                    code="feet_cut_off",
                    severity="error",
                    message="Bàn chân bị cắt hoặc chạm mép dưới ảnh. Vui lòng đứng lùi lại.",
                    box=[0.85, 0.2, 1.0, 0.8],
                )
            )

    # 4. Keypoint Visibility Occlusion Check
    # Only applicable to front view (Side view inherently has opposite arm/leg occluded)
    if image_type == "front":
        core_indices = [11, 12, 23, 24, 25, 26]
        low_vis_count = sum(1 for idx in core_indices if landmarks[idx].visibility < 0.60)
        if low_vis_count >= 2:
            issues.append(
                QualityIssue(
                    code="body_occluded",
                    severity="error",
                    message="Các điểm cơ thể (vai, eo, hông) bị vật thể che khuất (túi xách, điện thoại...).",
                )
            )

    # 5. Pose Orientation Check
    left_shoulder, right_shoulder = landmarks[11], landmarks[12]
    shoulder_z_diff = abs(left_shoulder.z - right_shoulder.z)
    shoulder_pixel_width = abs(left_shoulder.x - right_shoulder.x) * w

    if image_type == "front":
        # Check if standing rotated > 25°
        if shoulder_z_diff > 0.20:
            issues.append(
                QualityIssue(
                    code="bad_pose",
                    severity="error",
                    message="Tư thế đang bị xoay chéo. Vui lòng đứng thẳng trực diện máy ảnh.",
                )
            )
    elif image_type == "side":
        # In 90° side profile, shoulder horizontal projection should be significantly smaller
        if shoulder_pixel_width > 0.32 * w:
            issues.append(
                QualityIssue(
                    code="bad_pose",
                    severity="warning",
                    message="Góc chụp nghiêng chưa đúng 90 độ. Vui lòng xoay ngang người.",
                )
            )

    # 6. Fast OpenCV ROI Blur & Lighting Check
    # Crop Torso ROI (Shoulders to Knees) to eliminate background noise
    ymin_roi = max(0, int(min(left_shoulder.y, right_shoulder.y) * h))
    ymax_roi = min(h, int(max(landmarks[25].y, landmarks[26].y) * h))

    if image_type == "side":
        # In side view, both shoulders collapse to almost same x; use torso landmarks (11, 12, 23, 24) + padding
        torso_xs = [landmarks[i].x for i in [11, 12, 23, 24] if i < len(landmarks)]
        min_tx = min(torso_xs) if torso_xs else left_shoulder.x
        max_tx = max(torso_xs) if torso_xs else right_shoulder.x
        xmin_roi = max(0, int((min_tx - 0.12) * w))
        xmax_roi = min(w, int((max_tx + 0.12) * w))
    else:
        xmin_roi = max(0, int(min(left_shoulder.x, right_shoulder.x) * w) - 20)
        xmax_roi = min(w, int(max(left_shoulder.x, right_shoulder.x) * w) + 20)

    if ymax_roi > ymin_roi + 20 and xmax_roi > xmin_roi + 20:
        torso_roi = img_rgb[ymin_roi:ymax_roi, xmin_roi:xmax_roi]
    else:
        torso_roi = img_rgb

    if cv2 is not None:
        gray_roi = cv2.cvtColor(torso_roi, cv2.COLOR_RGB2GRAY)
        blur_score = float(cv2.Laplacian(gray_roi, cv2.CV_64F).var())
        mean_intensity = float(gray_roi.mean())
    else:
        blur_score = 120.0
        mean_intensity = 128.0

    # User-Friendly Thresholds: phone photos in normal room lighting pass smoothly
    min_blur = 20.0 if image_type == "side" else 35.0
    if blur_score < min_blur:
        issues.append(
            QualityIssue(
                code="blurry",
                severity="error",
                message=f"Ảnh bị mờ hoặc rung tay (độ nét {blur_score:.1f} < {min_blur:.0f}). Vui lòng giữ chắc máy ảnh.",
            )
        )

    if mean_intensity < 25.0:
        issues.append(
            QualityIssue(
                code="bad_lighting",
                severity="error",
                message="Ảnh quá tối hoặc thiếu sáng. Vui lòng bật đèn hoặc đứng nơi sáng hơn.",
            )
        )
    elif mean_intensity > 235.0:
        issues.append(
            QualityIssue(
                code="bad_lighting",
                severity="error",
                message="Ảnh bị cháy sáng quá mức. Vui lòng tránh ngược sáng.",
            )
        )

    # Compute validation & confidence
    has_errors = any(iss.severity == "error" for iss in issues)
    is_valid = not has_errors
    confidence = 0.98 if is_valid else max(0.1, 0.98 - (len(issues) * 0.25))

    dt_ms = (time.perf_counter() - t0) * 1000

    return QualityCheckResponse(
        is_valid=is_valid,
        confidence_score=round(confidence, 2),
        issues=issues,
        blur_score=round(blur_score, 1),
        landmarks_detected=landmarks_count,
        engine_id="opencv_mediapipe",
        latency_ms=round(dt_ms, 2),
    )
