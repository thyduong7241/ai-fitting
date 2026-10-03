"""Experiment runner: test varying one measurement at a time and generate comparison grids."""

import os
import sys
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.pipeline import generate_body
from src.schemas.measurements import BodyMeasurements


def create_comparison_strip(images, labels, title, output_path):
    """Combine multiple images side-by-side with measurement labels and save."""
    img_w, img_h = images[0].size
    n = len(images)
    header_h = 60
    footer_h = 50

    combined = Image.new("RGB", (img_w * n, img_h + header_h + footer_h), (255, 255, 255))
    draw = ImageDraw.Draw(combined)

    # Title
    draw.text((20, 20), title, fill=(30, 30, 30))

    for i, (img, label) in enumerate(zip(images, labels)):
        x_offset = i * img_w
        combined.paste(img, (x_offset, header_h))
        # Label below each figure
        draw.text((x_offset + 30, header_h + img_h + 15), label, fill=(50, 50, 50))
        # Separator line
        if i > 0:
            draw.line([(x_offset, header_h), (x_offset, header_h + img_h)], fill=(220, 220, 220), width=2)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    combined.save(output_path)
    print(f"Saved experiment comparison to {output_path}")


def run_experiments():
    base_female = {
        "gender": "female",
        "height_cm": 165,
        "shoulder_cm": 92,
        "bust_cm": 86,
        "waist_cm": 66,
        "hip_cm": 92,
        "leg_length_cm": 85,
    }

    # Experiment 1: Vary Waist (58cm to 86cm)
    print("\n--- Running Experiment 1: Varying Waist ---")
    waist_values = [58, 66, 76, 86]
    waist_imgs = []
    waist_labels = []
    for w in waist_values:
        data = dict(base_female, waist_cm=w)
        img = generate_body(data, width=320, height=600)
        waist_imgs.append(img)
        waist_labels.append(f"Waist: {w} cm")
    create_comparison_strip(
        waist_imgs,
        waist_labels,
        "Experiment 1: Effect of Waist Circumference (58 -> 86 cm)",
        "outputs/experiments/ablation_waist.png"
    )

    # Experiment 2: Vary Hip (82cm to 108cm)
    print("\n--- Running Experiment 2: Varying Hip ---")
    hip_values = [82, 90, 100, 110]
    hip_imgs = []
    hip_labels = []
    for h in hip_values:
        data = dict(base_female, hip_cm=h)
        img = generate_body(data, width=320, height=600)
        hip_imgs.append(img)
        hip_labels.append(f"Hip: {h} cm")
    create_comparison_strip(
        hip_imgs,
        hip_labels,
        "Experiment 2: Effect of Hip Circumference (82 -> 110 cm)",
        "outputs/experiments/ablation_hip.png"
    )

    # Experiment 3: Vary Bust (78cm to 102cm)
    print("\n--- Running Experiment 3: Varying Bust ---")
    bust_values = [78, 86, 94, 102]
    bust_imgs = []
    bust_labels = []
    for b in bust_values:
        data = dict(base_female, bust_cm=b)
        img = generate_body(data, width=320, height=600)
        bust_imgs.append(img)
        bust_labels.append(f"Bust: {b} cm")
    create_comparison_strip(
        bust_imgs,
        bust_labels,
        "Experiment 3: Effect of Bust Circumference (78 -> 102 cm)",
        "outputs/experiments/ablation_bust.png"
    )

    # Experiment 4: Vary Shoulder (78cm to 106cm)
    print("\n--- Running Experiment 4: Varying Shoulder ---")
    shoulder_values = [78, 88, 98, 108]
    shoulder_imgs = []
    shoulder_labels = []
    for s in shoulder_values:
        data = dict(base_female, shoulder_cm=s)
        img = generate_body(data, width=320, height=600)
        shoulder_imgs.append(img)
        shoulder_labels.append(f"Shoulder: {s} cm")
    create_comparison_strip(
        shoulder_imgs,
        shoulder_labels,
        "Experiment 4: Effect of Shoulder Circumference (78 -> 108 cm)",
        "outputs/experiments/ablation_shoulder.png"
    )

    print("\nAll ablation experiments completed successfully!")


if __name__ == "__main__":
    run_experiments()
