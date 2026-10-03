"""Configuration loader for Body Fit and Virtual Try-On."""

import os
from functools import lru_cache
from typing import Dict, Any
import yaml

DEFAULT_CONFIG_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../config/config.yaml")
)


@lru_cache(maxsize=1)
def load_config(config_path: str = DEFAULT_CONFIG_PATH) -> Dict[str, Any]:
    """Load and cache YAML configuration with safe fallback."""
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    # Minimal fallback configuration
    return {
        "paths": {
            "output_dir": "outputs",
            "assets_dir": "assets",
        },
        "anatomy": {
            "proportions": {
                "female": {"bust": 0.52, "waist": 0.40, "hip": 0.55, "shoulder": 0.225},
                "male": {"bust": 0.56, "waist": 0.46, "hip": 0.53, "shoulder": 0.255},
            }
        },
        "mesh_3d": {
            "radial_segments": 32,
            "height_slices": 60,
            "garment_offset_mm": 4.0,
        },
    }
