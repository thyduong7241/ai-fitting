"""Script to generate the reference demo image and the 4-case comparison grid (A | B | C | D)."""

import os
import sys
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.pipeline import generate_body


def main():
    os.makedirs("outputs/demo", exist_ok=True)

    # 1. Reference Body
    ref_input = {
        "gender": "female",
        "height_cm": 165,
        "weight_kg": 65,
        "shoulder_width_cm": 74,
        "bust_cm": 86,
        "waist_cm": 85,
        "hip_cm": 92
    }
    ref_img = generate_body(ref_input, output_path="outputs/demo/reference_body.png", width=600, height=1000)
    print("Saved reference body to outputs/demo/reference_body.png")

    # 2. Cases A, B, C, D
    cases = [
        ("Case A - Slim waist", {
            "gender": "female",
            "height_cm": 165,
            "weight_kg": 65,
            "shoulder_width_cm": 74,
            "bust_cm": 86,
            "waist_cm": 65,
            "hip_cm": 92
        }, "waist: 65cm | hip: 92cm | H: 165cm"),
        ("Case B - Wider waist", {
            "gender": "female",
            "height_cm": 165,
            "weight_kg": 65,
            "shoulder_width_cm": 74,
            "bust_cm": 86,
            "waist_cm": 85,
            "hip_cm": 92
        }, "waist: 85cm | hip: 92cm | H: 165cm"),
        ("Case C - Wider hips", {
            "gender": "female",
            "height_cm": 165,
            "weight_kg": 65,
            "shoulder_width_cm": 74,
            "bust_cm": 86,
            "waist_cm": 65,
            "hip_cm": 105
        }, "waist: 65cm | hip: 105cm | H: 165cm"),
        ("Case D - Taller body", {
            "gender": "female",
            "height_cm": 175,
            "weight_kg": 65,
            "shoulder_width_cm": 74,
            "bust_cm": 86,
            "waist_cm": 65,
            "hip_cm": 92
        }, "waist: 65cm | hip: 92cm | H: 175cm"),
    ]

    images = []
    labels = []
    subtitles = []

    # Use baseline height 165cm as reference so Case D (175cm) visually renders taller
    for title, data, sub in cases:
        img = generate_body(data, width=320, height=650, reference_height_cm=165.0)
        images.append(img)
        labels.append(title)
        subtitles.append(sub)

    # Combine into A | B | C | D grid
    n = len(images)
    img_w, img_h = images[0].size
    header_h = 70
    footer_h = 60

    combined = Image.new("RGB", (img_w * n, img_h + header_h + footer_h), (255, 255, 255))
    draw = ImageDraw.Draw(combined)

    # Main Header
    draw.text((25, 20), "Body Fit MVP - Visual Validation Grid (A | B | C | D)", fill=(20, 20, 20))

    for i in range(n):
        x = i * img_w
        combined.paste(images[i], (x, header_h))

        # Title and sub-label
        draw.text((x + 20, header_h + img_h + 10), labels[i], fill=(30, 40, 60))
        draw.text((x + 20, header_h + img_h + 32), subtitles[i], fill=(100, 100, 100))

        # Separator line
        if i > 0:
            draw.line([(x, header_h), (x, header_h + img_h)], fill=(225, 225, 225), width=2)

    comparison_path = "outputs/demo/comparison_grid_abcd.png"
    combined.save(comparison_path)
    print(f"Saved comparison grid to {comparison_path}")


if __name__ == "__main__":
    main()
