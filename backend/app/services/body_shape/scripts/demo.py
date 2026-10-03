"""
Reference demo script showcasing the Body Fit module interface.
Generates outputs/demo/reference_body.png using exact specification.
"""

import os
import sys

# Ensure parent of body_fit is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from body_fit import generate_body


def main():
    output_file = "outputs/demo/reference_body.png"
    os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)

    print("Generating reference body illustration...")
    image = generate_body(
        height_cm=165,
        weight_kg=65,
        shoulder_width_cm=74,
        bust_cm=86,
        waist_cm=85,
        hip_cm=92,
        gender="female",
        seed=42,
        output_path=output_file
    )

    print(f"Success! Reference body saved to: {output_file} (size: {image.size})")


if __name__ == "__main__":
    main()
