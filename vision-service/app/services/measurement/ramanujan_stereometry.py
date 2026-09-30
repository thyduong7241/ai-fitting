"""
Higher-order Ramanujan ellipse circumference approximation for 2-view stereometry.
Calculates circumference from semi-major axis (a) and semi-minor axis (b).
"""

import math


def ramanujan_circumference(a: float, b: float) -> float:
    """
    Ramanujan's second approximation formula for ellipse circumference:
    C ~ pi * [ 3(a + b) - sqrt( (3a + b)(a + 3b) ) ]
    Accurate to within 0.05% across wide eccentricities.
    """
    if a <= 0 or b <= 0:
        return 0.0

    term1 = 3.0 * (a + b)
    term2 = math.sqrt((3.0 * a + b) * (a + 3.0 * b))
    c = math.pi * (term1 - term2)
    return max(0.0, c)
