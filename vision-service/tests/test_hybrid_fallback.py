import pytest
from app.services.measurement.hybrid_fallback import estimate_missing_depths
from app.services.measurement.anthropometric_prior import get_prior_factors


def test_missing_depths_estimation():
    priors = get_prior_factors(age=28, bmi=22.2, gender="male")
    depths = estimate_missing_depths(
        a_chest=18.0,
        a_waist=15.0,
        a_hips=18.5,
        prior_factors=priors,
        gender="male",
    )
    assert depths["b_chest"] > 0
    assert depths["b_waist"] > 0
    assert depths["b_hips"] > 0
    # Anatomical check: chest depth should be smaller than front half-width
    assert depths["b_chest"] < 18.0
