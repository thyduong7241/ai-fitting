"""
Anthropometric prior calibration:
Adjusts 2D stereometry semi-axes according to age, BMI, and gender physiological priors.
"""


def calculate_bmi(height_cm: float, weight_kg: float) -> float:
    height_m = height_cm / 100.0
    return round(weight_kg / (height_m * height_m), 1)


def get_prior_factors(
    age: int,
    bmi: float,
    gender: str,
) -> dict:
    """
    Compute physiological adjustment factors.
    - Post-25 visceral adiposity (waist)
    - BMI deviation from normal baseline (21.5 for women, 22.5 for men)
    - Gender pelvic & bust distribution
    """
    baseline_bmi = 21.5 if gender == "female" else 22.5
    bmi_delta = bmi - baseline_bmi

    # Waist factor: increases with age > 25 and higher BMI
    age_waist_drift = max(0, age - 25) * 0.0025
    bmi_waist_drift = bmi_delta * 0.010
    k_waist = 1.0 + age_waist_drift + bmi_waist_drift

    # Chest factor: pectoral volume vs bust volume
    k_chest = 1.0 + (bmi_delta * 0.008)
    if gender == "female":
        k_chest *= 1.04

    # Hips factor: gynoid fat distribution in females
    k_hips = 1.0 + (bmi_delta * 0.009)
    if gender == "female":
        k_hips *= 1.06

    return {
        "k_waist": max(0.85, min(1.35, k_waist)),
        "k_chest": max(0.85, min(1.35, k_chest)),
        "k_hips": max(0.85, min(1.35, k_hips)),
    }
