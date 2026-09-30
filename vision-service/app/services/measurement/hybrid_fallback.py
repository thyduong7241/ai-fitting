"""
Hybrid fallback depth estimation when side-view photo is missing.
Reconstructs anatomical depth semi-axis from front-width and BMI priors.
"""

from typing import Dict


def estimate_missing_depths(
    a_chest: float,
    a_waist: float,
    a_hips: float,
    prior_factors: Dict[str, float],
    gender: str,
) -> Dict[str, float]:
    """
    Estimate semi-minor axis (b) from front semi-major axis (a) and anatomical ratios.
    """
    # Standard anatomical depth-to-width ratios in adults
    # Chest depth: ~70-75% of width
    # Waist depth: ~65-72% of width
    # Hips depth: ~80-88% of width
    base_b_chest = a_chest * (0.74 if gender == "female" else 0.70)
    base_b_waist = a_waist * (0.68 if gender == "female" else 0.72)
    base_b_hips = a_hips * (0.86 if gender == "female" else 0.82)

    return {
        "b_chest": base_b_chest * prior_factors["k_chest"],
        "b_waist": base_b_waist * prior_factors["k_waist"],
        "b_hips": base_b_hips * prior_factors["k_hips"],
    }
