import pytest
from app.core.mediapipe_detector import LandmarkPoint
from app.services.measurement.p2m_calibrator import calculate_p2m_scale, landmark_distance_cm
from app.services.measurement.linear_bones import (
    measure_shoulder_width,
    measure_arm_length,
    measure_inseam,
)


def create_mock_landmarks_175cm():
    # Synthetic landmarks for 175cm person on 1280x720 canvas
    # crown ~0.08, heels ~0.96 -> span = 0.88 * 1280 = 1126.4px
    # P2M = 175 / 1126.4 = ~0.1553 cm/pixel
    lms = []
    for i in range(33):
        if i == 0:  # Nose
            lms.append(LandmarkPoint(0.5, 0.12, 0.0, 0.99))
        elif i in (7, 8):  # Ears
            lms.append(LandmarkPoint(0.46 if i == 7 else 0.54, 0.12, 0.0, 0.99))
        elif i in (11, 12):  # Shoulders (dist ~ 254px * 0.1553 = 39.5cm * 1.10 = 43.5cm)
            lms.append(LandmarkPoint(0.32 if i == 11 else 0.68, 0.22, 0.0, 0.99))
        elif i in (13, 14):  # Elbows
            lms.append(LandmarkPoint(0.28 if i == 13 else 0.72, 0.38, 0.0, 0.99))
        elif i in (15, 16):  # Wrists
            lms.append(LandmarkPoint(0.26 if i == 15 else 0.74, 0.55, 0.0, 0.99))
        elif i in (23, 24):  # Hips
            lms.append(LandmarkPoint(0.40 if i == 23 else 0.60, 0.48, 0.0, 0.99))
        elif i in (25, 26):  # Knees
            lms.append(LandmarkPoint(0.43 if i == 25 else 0.57, 0.72, 0.0, 0.99))
        elif i in (27, 28):  # Ankles
            lms.append(LandmarkPoint(0.44 if i == 27 else 0.56, 0.94, 0.0, 0.99))
        elif i in (29, 30, 31, 32):  # Feet/Heels
            lms.append(LandmarkPoint(0.44 if i % 2 == 1 else 0.56, 0.96, 0.0, 0.99))
        else:
            lms.append(LandmarkPoint(0.5, 0.5, 0.0, 0.9))
    return lms


def test_p2m_scale_calculation():
    lms = create_mock_landmarks_175cm()
    scale = calculate_p2m_scale(lms, 1280, 720, 175.0)
    assert 0.14 <= scale <= 0.17


def test_linear_bones_measurements():
    lms = create_mock_landmarks_175cm()
    scale = calculate_p2m_scale(lms, 1280, 720, 175.0)

    shoulder = measure_shoulder_width(lms, scale, 720, 1280)
    assert 40.0 <= shoulder <= 46.0

    arm = measure_arm_length(lms, scale, 720, 1280)
    assert 55.0 <= arm <= 65.0

    inseam = measure_inseam(lms, scale, 720, 1280)
    assert 72.0 <= inseam <= 80.0
