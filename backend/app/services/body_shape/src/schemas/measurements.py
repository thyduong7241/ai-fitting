"""Input validation and data schema for Body Measurements."""

from dataclasses import dataclass
from typing import Optional, Literal, Dict, Any


VALID_MEASUREMENT_RANGES = {
    "height_cm": (100.0, 250.0),
    "weight_kg": (25.0, 300.0),
    "bust_cm": (50.0, 180.0),
    "waist_cm": (40.0, 180.0),
    "hip_cm": (50.0, 190.0),
    "shoulder_width_cm": (25.0, 120.0),
    "arm_length_cm": (30.0, 110.0),
    "leg_length_cm": (45.0, 140.0),
}


@dataclass
class BodyMeasurements:
    """
    Validated body measurements in centimeters and kilograms.
    
    Attributes:
        gender: "female" or "male". Defaults to "female".
        height_cm: Stature in centimeters (range: 100 - 250 cm). Defaults to 165.0.
        weight_kg: Body mass in kilograms (optional).
        shoulder_width_cm: Shoulder tip-to-tip linear width or outer shoulder span (optional).
        bust_cm: Chest/bust circumference in centimeters (optional).
        waist_cm: Waist circumference in centimeters (optional).
        hip_cm: Hip circumference in centimeters (optional).
        arm_length_cm: Shoulder-to-wrist linear arm length (optional).
        leg_length_cm: Crotch-to-floor/ankle leg length (optional).
    """
    gender: Literal["female", "male"] = "female"
    height_cm: float = 165.0
    weight_kg: Optional[float] = None
    shoulder_width_cm: Optional[float] = None
    bust_cm: Optional[float] = None
    waist_cm: Optional[float] = None
    hip_cm: Optional[float] = None
    arm_length_cm: Optional[float] = None
    leg_length_cm: Optional[float] = None

    def __post_init__(self):
        self.validate()
        self._apply_anthropometric_defaults()

    def validate(self):
        """Validate input ranges and types, raising clear ValueError on invalid inputs."""
        if self.gender not in ("female", "male"):
            raise ValueError(f"Invalid gender '{self.gender}'. Must be 'female' or 'male'.")

        for attr, (min_v, max_v) in VALID_MEASUREMENT_RANGES.items():
            val = getattr(self, attr, None)
            if val is not None:
                if not isinstance(val, (int, float)):
                    raise TypeError(f"Measurement '{attr}' must be a number, got {type(val).__name__}.")
                if val < min_v or val > max_v:
                    raise ValueError(f"Measurement '{attr}' ({val}) is outside valid physiological range [{min_v}, {max_v}].")

    def _apply_anthropometric_defaults(self):
        """
        Fill missing optional measurements using standard population averages
        proportional to height and gender.
        """
        # Shoulder normalization:
        # If passed as outer circumference/arc (> 55 cm), convert to linear biacromial width
        if self.shoulder_width_cm is not None and self.shoulder_width_cm > 55.0:
            self.shoulder_width_cm = self.shoulder_width_cm / 1.95

        if self.gender == "female":
            if self.bust_cm is None:
                self.bust_cm = self.height_cm * 0.52
            if self.waist_cm is None:
                self.waist_cm = self.height_cm * 0.40
            if self.hip_cm is None:
                self.hip_cm = self.height_cm * 0.55
            if self.shoulder_width_cm is None:
                self.shoulder_width_cm = self.height_cm * 0.225
            if self.leg_length_cm is None:
                self.leg_length_cm = self.height_cm * 0.48
            if self.arm_length_cm is None:
                self.arm_length_cm = self.height_cm * 0.33
        else:  # male
            if self.bust_cm is None:
                self.bust_cm = self.height_cm * 0.56
            if self.waist_cm is None:
                self.waist_cm = self.height_cm * 0.46
            if self.hip_cm is None:
                self.hip_cm = self.height_cm * 0.53
            if self.shoulder_width_cm is None:
                self.shoulder_width_cm = self.height_cm * 0.255
            if self.leg_length_cm is None:
                self.leg_length_cm = self.height_cm * 0.49
            if self.arm_length_cm is None:
                self.arm_length_cm = self.height_cm * 0.34

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BodyMeasurements":
        """Construct and validate BodyMeasurements from dictionary."""
        # Map alternate aliases if provided
        data_clean = dict(data)
        if "shoulder_width_cm" not in data_clean and "shoulder_cm" in data_clean:
            data_clean["shoulder_width_cm"] = data_clean["shoulder_cm"]
        return cls(**{k: v for k, v in data_clean.items() if hasattr(cls, k)})
