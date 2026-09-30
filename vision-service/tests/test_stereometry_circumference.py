import pytest
from app.services.measurement.ramanujan_stereometry import ramanujan_circumference
from app.services.measurement.anthropometric_prior import calculate_bmi, get_prior_factors


def test_ramanujan_circle():
    # If a = b = 10, circumference of circle = 2 * pi * 10 = ~62.83
    circ = ramanujan_circumference(10.0, 10.0)
    assert abs(circ - 62.83) < 0.1


def test_ramanujan_ellipse():
    # Semi-axes a = 18cm (width 36cm), b = 12cm (depth 24cm)
    circ = ramanujan_circumference(18.0, 12.0)
    assert 94.0 <= circ <= 97.0


def test_anthropometric_prior_factors():
    bmi_normal = calculate_bmi(175.0, 68.0)
    assert 21.0 <= bmi_normal <= 23.0

    # Young adult vs older adult waist factor
    factors_young = get_prior_factors(age=20, bmi=22.0, gender="male")
    factors_mature = get_prior_factors(age=45, bmi=27.0, gender="male")

    assert factors_mature["k_waist"] > factors_young["k_waist"]
