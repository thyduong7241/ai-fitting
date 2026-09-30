"""
Generate synthetic image fixtures for vision-service quantitative benchmarks.
Creates sample valid images and error-injected images (blurry, cut-off, bad lighting, etc.)
"""

import argparse
import json
import os
from pathlib import Path
import numpy as np

try:
    import cv2
except ImportError:
    cv2 = None


def create_synthetic_person_image(
    width: int = 720,
    height: int = 1280,
    cut_head: bool = False,
    cut_feet: bool = False,
    blur: bool = False,
    dark: bool = False,
    overexposed: bool = False,
    no_person: bool = False,
) -> np.ndarray:
    """Create a synthetic RGB image simulating a full-body person photo."""
    # Background (neutral wall / floor)
    if dark:
        img = np.full((height, width, 3), 30, dtype=np.uint8)
    elif overexposed:
        img = np.full((height, width, 3), 245, dtype=np.uint8)
    else:
        # Subtle gradient background
        y_vals = np.linspace(210, 180, height).reshape(-1, 1)
        img = np.repeat(y_vals, width, axis=1).astype(np.uint8)
        img = np.stack([img, img, img], axis=-1)

    if no_person:
        return img

    cx = width // 2
    # Person vertical range
    head_top = 30 if cut_head else 120
    feet_bottom = height - 5 if cut_feet else height - 120

    # Draw head
    head_center_y = head_top + 60
    head_radius = 50
    head_color = (200, 180, 160)  # Skin tone
    torso_color = (60, 80, 120)    # Navy t-shirt
    pants_color = (40, 40, 50)     # Dark jeans

    # Head
    if cv2 is not None:
        cv2.circle(img, (cx, head_center_y), head_radius, head_color, -1)
        # Torso
        shoulder_y = head_center_y + head_radius + 15
        waist_y = shoulder_y + 320
        cv2.rectangle(img, (cx - 110, shoulder_y), (cx + 110, waist_y), torso_color, -1)
        # Arms
        cv2.line(img, (cx - 100, shoulder_y + 20), (cx - 130, waist_y + 80), head_color, 24)
        cv2.line(img, (cx + 100, shoulder_y + 20), (cx + 130, waist_y + 80), head_color, 24)
        # Legs
        ankle_y = feet_bottom - 20
        cv2.line(img, (cx - 50, waist_y), (cx - 50, ankle_y), pants_color, 45)
        cv2.line(img, (cx + 50, waist_y), (cx + 50, ankle_y), pants_color, 45)
        # Feet
        cv2.ellipse(img, (cx - 50, feet_bottom - 10), (35, 15), 0, 0, 360, (20, 20, 20), -1)
        cv2.ellipse(img, (cx + 50, feet_bottom - 10), (35, 15), 0, 0, 360, (20, 20, 20), -1)

        if blur:
            img = cv2.GaussianBlur(img, (45, 45), 0)
    else:
        # Fallback numpy simple drawing
        img[head_top:head_top + 100, cx - 40:cx + 40] = head_color
        img[head_top + 100:head_top + 450, cx - 100:cx + 100] = torso_color
        img[head_top + 450:feet_bottom, cx - 70:cx + 70] = pants_color

    return img


def generate_all_fixtures(base_dir: Path):
    """Generate all images listed in ground_truth.json."""
    gt_path = base_dir / "ground_truth.json"
    if not gt_path.exists():
        raise FileNotFoundError(f"Cannot find {gt_path}")

    with open(gt_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Subdirectories
    subdirs = ["valid", "cut_head", "cut_feet", "blurry", "bad_lighting", "bad_pose"]
    for sub in subdirs:
        (base_dir / "images" / sub).mkdir(parents=True, exist_ok=True)

    # Generate measurement subjects images
    for subject in data.get("measurement_subjects", []):
        front_p = base_dir / subject["front_image_path"]
        side_p = base_dir / subject["side_image_path"] if subject.get("side_image_path") else None

        front_p.parent.mkdir(parents=True, exist_ok=True)
        img_front = create_synthetic_person_image()
        if cv2 is not None:
            cv2.imwrite(str(front_p), img_front)
        else:
            with open(front_p, "wb") as f:
                f.write(b"\xFF\xD8\xFF\xE0" + b"\x00" * 1000)

        if side_p:
            side_p.parent.mkdir(parents=True, exist_ok=True)
            img_side = create_synthetic_person_image()
            if cv2 is not None:
                cv2.imwrite(str(side_p), img_side)
            else:
                with open(side_p, "wb") as f:
                    f.write(b"\xFF\xD8\xFF\xE0" + b"\x00" * 1000)

    # Generate quality test case images
    for qc in data.get("quality_cases", []):
        img_p = base_dir / qc["image_path"]
        img_p.parent.mkdir(parents=True, exist_ok=True)

        issues = qc.get("expected_issues", [])
        cut_h = "head_cut_off" in issues
        cut_f = "feet_cut_off" in issues
        is_blur = "blurry" in issues
        is_dark = "bad_lighting" in issues and "dark" in qc["id"]
        is_bright = "bad_lighting" in issues and "overexposed" in qc["id"]
        no_p = "no_person" in issues

        img = create_synthetic_person_image(
            cut_head=cut_h,
            cut_feet=cut_f,
            blur=is_blur,
            dark=is_dark,
            overexposed=is_bright,
            no_person=no_p,
        )

        if "low_resolution" in issues and cv2 is not None:
            img = cv2.resize(img, (300, 400))

        if cv2 is not None:
            cv2.imwrite(str(img_p), img)
        else:
            with open(img_p, "wb") as f:
                f.write(b"\xFF\xD8\xFF\xE0" + b"\x00" * 1000)

    print(f"Generated benchmark fixtures successfully in {base_dir / 'images'}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", action="store_true", help="Verify dataset schema and fixtures")
    args = parser.parse_args()

    cur_dir = Path(__file__).resolve().parent
    generate_all_fixtures(cur_dir)

    if args.verify:
        from schema import GroundTruthDataset
        gt_file = cur_dir / "ground_truth.json"
        with open(gt_file, "r", encoding="utf-8") as f:
            raw = json.load(f)
        validated = GroundTruthDataset(**raw)
        print(f"Dataset Verified: {len(validated.measurement_subjects)} measurement subjects, {len(validated.quality_cases)} quality cases.")
