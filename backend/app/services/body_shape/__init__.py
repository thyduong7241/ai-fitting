"""
Body Fit Module — Realistic Parametric 3D Body Studio.
"""

import sys
import os

# Add package root to sys.path so submodule imports work cleanly
_pkg_root = os.path.dirname(os.path.abspath(__file__))
if _pkg_root not in sys.path:
    sys.path.insert(0, _pkg_root)

from src.pipeline import generate_body
from src.schemas.measurements import BodyMeasurements
from src.body_model.parameters import BodyParameters, calculate_parameters
from src.generator.renderer import BodyRenderer
from src.body_model.mesh3d import ParametricBody3D
from src.body_model.deformation_engine import AnthropometricDeformationEngine
from src.body_model.body_analyzer import BodyAnalyzer
from src.config_loader import load_config

__all__ = [
    "generate_body",
    "BodyMeasurements",
    "BodyParameters",
    "calculate_parameters",
    "BodyRenderer",
    "ParametricBody3D",
    "AnthropometricDeformationEngine",
    "BodyAnalyzer",
    "load_config"
]
