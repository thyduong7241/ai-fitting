# Body Fit — 2D Parametric Body Proportion Generator

Body Fit is a standalone, lightweight Python module developed for the Virtual Try-On system. It generates a **2D full-body human illustration / mannequin** whose proportions dynamically adapt to a user's input measurements.

---

## 1. What Body Fit Does

Given numerical body measurements (height, bust, waist, hip, shoulder width, etc.), Body Fit generates a clean, front-facing 2D body illustration with anatomical contours matching the entered proportions.

- **Deterministic**: The same measurements and seed always produce the exact same image.
- **CPU-Only**: Requires no GPU, model checkpoints, or heavyweight machine learning frameworks.
- **Fast**: Generates illustrations in under **20 milliseconds**.
- **Decoupled Architecture**: Keeps validation, measurement normalization, geometry calculation, and raster rendering cleanly isolated.

---

## 2. Input Measurements

The primary interface accepts standard anthropometric measurements in **centimeters** and **kilograms**:

| Parameter | Type | Required? | Default / Physiological Bounds | Description |
| :--- | :--- | :--- | :--- | :--- |
| `height_cm` | `float` | **Yes** | 165.0 cm (bounds: 100–250 cm) | Total stature from crown to floor |
| `gender` | `str` | No | `"female"` (`"female"` or `"male"`) | Selects base anatomical proportion ratios |
| `waist_cm` | `float` | No | Proportional ($\approx 0.40 \times H$) (40–180 cm) | Waist circumference |
| `hip_cm` | `float` | No | Proportional ($\approx 0.55 \times H$) (50–190 cm) | Hip/pelvis circumference |
| `bust_cm` | `float` | No | Proportional ($\approx 0.52 \times H$) (50–180 cm) | Chest/bust circumference |
| `shoulder_width_cm`| `float` | No | Proportional ($\approx 0.225 \times H$) (25–120 cm) | Biacromial tip-to-tip width or outer span |
| `arm_length_cm` | `float` | No | Proportional ($\approx 0.33 \times H$) (30–110 cm) | Shoulder tip to wrist length |
| `leg_length_cm` | `float` | No | Proportional ($\approx 0.48 \times H$) (45–140 cm) | Inseam / leg length |
| `weight_kg` | `float` | No | None (25–300 kg) | Body mass |
| `seed` | `int` | No | `42` | Random seed for deterministic rendering |

> **Validation Note:** Missing optional measurements are automatically filled using anthropometrically sound defaults based on height and gender. Any values outside realistic physiological bounds immediately raise a clear `ValueError`.

---

## 3. Output

- **Return Value**: A `PIL.Image.Image` instance (RGB).
- **Optional File Output**: Provide `output_path="path/to/image.png"` to save the image directly to disk.
- **Resolution**: Configurable (`width=600`, `height=1000` by default).

---

## 4. Example Usage

```python
from body_fit import generate_body

# Generate body illustration from measurements
image = generate_body(
    height_cm=165,
    weight_kg=65,
    shoulder_width_cm=74,
    bust_cm=86,
    waist_cm=85,
    hip_cm=92,
    gender="female",
    seed=42,
    output_path="outputs/demo/reference_body.png"
)

# image is a PIL Image object
image.show()
```

---

## 5. How to Run Locally

### Requirements
- Python 3.9+ (Python 3.10 recommended)
- Dependencies: `pip install -r requirements.txt`

### Quick Start
```bash
# 1. Start the interactive 3D Web Studio
# Double-click start.bat in the Hackathon root directory, or run:
python -m uvicorn body_fit.src.api.server:app --host 0.0.0.0 --port 8000 --reload

# Open in browser: http://localhost:8000/
# Swagger API docs: http://localhost:8000/docs

# 2. Run the automated test suite
python -m unittest discover -v tests

# 3. Verify live server end-to-end
python scripts/test_live_api.py

# 4. Run the 2D reference demo
python scripts/demo.py
```

---

## 6. Architecture & Separation of Concerns

```
Input Measurements (dict / kwargs)
       │
       ▼
1. Validation & Schemas (`src/schemas/measurements.py`)
   - Type checking, physiological range assertion [min, max]
   - Anthropometric defaulting for missing fields
       │
       ▼
2. Measurement-to-Parameter Normalization (`src/body_model/parameters.py`)
   - Converts tape circumferences to 2D elliptical frontal half-widths:
     w = (circumference / 2π) * frontal_ratio / H
   - Normalizes vertical landmarks (crotch, knees, ankles, elbows)
       │
       ▼
3. Geometry Generation (`src/generator/geometry.py`)
   - Constructs bilateral control points
   - Evaluates cubic Catmull-Rom splines for smooth anatomical silhouettes
       │
       ▼
4. Deterministic Rendering (`src/generator/renderer.py`)
   - Multi-layer rendering (arms, legs, torso)
   - Supersampling (2x) and Lanczos anti-aliasing
       │
       ▼
Output: PIL Image / PNG
```

---

## 7. Limitations of This MVP

1. **Non-Photorealistic**: The current output is a clean 2D vector silhouette/illustration, not a textured photorealistic human or 3D mesh.
2. **Simplified Front View**: The model represents a frontal standing posture; it does not yet produce lateral/side or back views.
3. **Cross-Section Approximation**: Body circumferences are projected to frontal width using empirical transverse elliptical ratios rather than full 3D volumetric tomography.

---

## 8. Why This MVP Does Not Use an AI Model Yet

1. **Predictable Measurement Adherence**: Off-the-shelf generative diffusion models (Stable Diffusion, Midjourney, Flux) cannot reliably adhere to precise numerical centimeter constraints via text prompting alone.
2. **Zero Overhead & Instant Feedback**: This mathematical model executes in under 20ms on any standard CPU without requiring GPUs, CUDA drivers, or multi-gigabyte weight downloads.
3. **Modular Foundation for Future AI Stages**: A mathematically grounded 2D silhouette serves as the ideal ControlNet / conditioning signal for future generative AI stages (e.g., rendering realistic skin and clothing over verified body proportions).
