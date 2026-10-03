from .geometry import (
    catmull_rom_spline,
    generate_torso_contour,
    generate_leg_contour,
    generate_arm_contour
)
from .renderer import BodyRenderer

__all__ = [
    "catmull_rom_spline",
    "generate_torso_contour",
    "generate_leg_contour",
    "generate_arm_contour",
    "BodyRenderer"
]
