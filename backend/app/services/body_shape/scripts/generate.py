"""CLI tool to generate a body illustration from JSON input or arguments."""

import argparse
import json
import sys
import os

# Add parent directory to path so imports work smoothly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.pipeline import generate_body
from src.schemas.measurements import BodyMeasurements


def main():
    parser = argparse.ArgumentParser(description="Generate 2D body illustration from body measurements.")
    parser.add_argument("--json", type=str, help="Path to JSON file with measurements")
    parser.add_argument("--gender", type=str, default="female", choices=["female", "male"])
    parser.add_argument("--height", type=float, default=165.0, help="Height in cm")
    parser.add_argument("--shoulder", type=float, default=None, help="Shoulder circumference or width in cm")
    parser.add_argument("--bust", type=float, default=None, help="Bust circumference in cm")
    parser.add_argument("--waist", type=float, default=None, help="Waist circumference in cm")
    parser.add_argument("--hip", type=float, default=None, help="Hip circumference in cm")
    parser.add_argument("--arm", type=float, default=None, help="Arm length in cm")
    parser.add_argument("--leg", type=float, default=None, help="Leg length in cm")
    parser.add_argument("--output", type=str, default="outputs/body_sample.png", help="Path to save output image")

    args = parser.parse_args()

    if args.json:
        with open(args.json, "r") as f:
            data = json.load(f)
    else:
        data = {
            "gender": args.gender,
            "height_cm": args.height,
            "shoulder_cm": args.shoulder,
            "bust_cm": args.bust,
            "waist_cm": args.waist,
            "hip_cm": args.hip,
            "arm_length_cm": args.arm,
            "leg_length_cm": args.leg,
        }

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    img = generate_body(data, output_path=args.output)
    print(f"Generated body illustration saved to: {args.output}")


if __name__ == "__main__":
    main()
