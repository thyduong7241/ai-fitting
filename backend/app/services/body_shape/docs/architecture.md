# Body Fit — System Architecture

> **Document status:** Pre-implementation design  
> **Author:** AI Engineer (Body Fit)  
> **Date:** 2026-09-28  
> **Version:** 1.0

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Component Map](#2-component-map)
3. [Data Flow — End to End](#3-data-flow--end-to-end)
4. [Model Flow — Body Representation](#4-model-flow--body-representation)
5. [Evaluation Flow](#5-evaluation-flow)
6. [Module Descriptions](#6-module-descriptions)
7. [Input / Output Contracts](#7-input--output-contracts)
8. [Staged Implementation Plan](#8-staged-implementation-plan)
9. [Dependency Graph](#9-dependency-graph)
10. [Configuration Design](#10-configuration-design)
11. [Integration Points for Upstream VTO System](#11-integration-points-for-upstream-vto-system)

---

## 1. Architecture Overview

Body Fit is a **self-contained Python module** (`body_fit/`) that accepts structured body measurements and returns a 2D image.

It has no dependency on the rest of the Virtual Try-On system during inference.

```
┌─────────────────────────────────────────────────────────────────┐
│                        BODY FIT MODULE                          │
│                                                                 │
│  Input: BodyMeasurements (JSON / Python dict)                   │
│                         │                                       │
│                         ▼                                       │
│              ┌─────────────────────┐                            │
│              │  1. Preprocessing   │  Validate, normalize,      │
│              │     & Schema        │  fill missing values       │
│              └─────────┬───────────┘                            │
│                        │                                        │
│                        ▼                                        │
│              ┌─────────────────────┐                            │
│              │  2. Body Model      │  Measurements → SMPL β     │
│              │     (SMPL fitting)  │  via gradient optimization  │
│              └─────────┬───────────┘                            │
│                        │                                        │
│                        ▼                                        │
│              ┌─────────────────────┐                            │
│              │  3. Rendering       │  β + pose → 3D mesh        │
│              │                     │  → 2D image (pyrender)     │
│              └─────────┬───────────┘                            │
│                        │                                        │
│                        ▼                                        │
│  Output: PIL.Image (PNG)                                        │
└─────────────────────────────────────────────────────────────────┘
```

The module is designed so that each of the three internal stages can be replaced independently.

---

## 2. Component Map

```
body_fit/
│
├── README.md                  ← User-facing documentation
├── requirements.txt           ← Python dependencies
│
├── config/
│   └── config.yaml            ← All tunable parameters (no hardcoding)
│
├── src/
│   ├── __init__.py
│   ├── pipeline.py            ← Public API: generate_body()
│   │
│   ├── schemas/
│   │   └── measurements.py    ← Pydantic model: BodyMeasurements
│   │
│   ├── preprocessing/
│   │   └── normalize.py       ← Validation, defaults, unit conversion
│   │
│   ├── body_model/
│   │   ├── smpl_wrapper.py    ← SMPL model loading + forward pass
│   │   ├── beta_optimizer.py  ← Gradient descent: measurements → β
│   │   └── measurement_map.py ← Maps measurement names → SMPL vertices
│   │
│   ├── generation/
│   │   └── renderer.py        ← pyrender: β + pose → 2D image
│   │
│   └── evaluation/
│       ├── estimator.py       ← Image → estimated measurements
│       └── metrics.py         ← AME, RME, WHR error, rank consistency
│
├── scripts/
│   ├── generate.py            ← CLI: single image generation
│   ├── evaluate.py            ← CLI: evaluation report
│   └── run_experiments.py     ← CLI: ablation experiments (vary 1 measurement)
│
├── tests/
│   ├── test_schema.py
│   ├── test_optimizer.py
│   ├── test_renderer.py
│   └── test_pipeline.py
│
└── outputs/                   ← Generated images and reports
```

---

## 3. Data Flow — End to End

```
User / API caller
        │
        │  {gender, height_cm, waist_cm, hip_cm, ...}
        ▼
┌──────────────────────────┐
│  pipeline.generate_body()│
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│  schemas/measurements.py │  ←── Pydantic validation
│  BodyMeasurements model  │       range checks
│  + missing value filling │       gender normalization
└────────────┬─────────────┘
             │  NormalizedMeasurements
             ▼
┌──────────────────────────┐
│  preprocessing/          │  ←── Convert cm → SMPL units
│  normalize.py            │       Map height → expected β₀
│                          │       Compute BMI (soft signal)
└────────────┬─────────────┘
             │  measurement_vector (torch.Tensor)
             ▼
┌──────────────────────────┐
│  body_model/             │  ←── SMPL model loaded once
│  beta_optimizer.py       │       Gradient descent (Adam)
│                          │       Loss = weighted MSE over measurements
│                          │       β regularization (prior: β ~ N(0,1))
└────────────┬─────────────┘
             │  β (torch.Tensor, shape [1, 10])
             ▼
┌──────────────────────────┐
│  body_model/             │  ←── smplx.create(gender=gender)
│  smpl_wrapper.py         │       output = model(betas=β, body_pose=θ)
│                          │       vertices: (6890, 3)
│                          │       faces: (13776, 3)
└────────────┬─────────────┘
             │  (vertices, faces, joints)
             ▼
┌──────────────────────────┐
│  generation/             │  ←── trimesh.Trimesh(vertices, faces)
│  renderer.py             │       pyrender.Scene + camera + light
│                          │       OffscreenRenderer(W, H)
│                          │       → RGB image (numpy array)
│                          │       → PIL.Image
└────────────┬─────────────┘
             │  PIL.Image
             ▼
      Output image
      (saved to outputs/ if requested)
```

---

## 4. Model Flow — Body Representation

### 4.1 SMPL model internals (simplified)

```
β (shape params, dim=10)
θ (pose params, dim=72)
        ↓
T̄ + Bs(β) + Bp(θ)   ← template mesh + shape blend + pose blend
        ↓
W(T, J(β), θ, W)    ← linear blend skinning with joint locations
        ↓
Mesh M = (V, F)      ← 6890 vertices, 13776 triangles
```

**Key insight:** β is the "body shape" dial. We only need to control β. We fix θ to a standard pose (A-pose or T-pose).

### 4.2 Measurement → β optimization loop

```
β₀ = zeros(10)                           ← start from mean body
θ = a_pose_angles                         ← fixed pose

for iteration in range(max_iter):
    V, F = SMPL(β, θ)                    ← forward pass (differentiable)
    M = SMPL_Anthropometry(V)             ← compute measurements from mesh
    
    loss_meas = Σ wᵢ · (Mᵢ - Mᵢ_target)²  ← weighted per-measurement MSE
    loss_reg  = λ · ||β||²                  ← regularize toward mean body
    loss = loss_meas + loss_reg
    
    β.grad = ∇β loss
    β = optimizer.step(β)                 ← Adam update
```

**Measurement weights** allow prioritizing certain measurements:

```yaml
measurement_weights:
  height_cm: 2.0          # Important for overall scale
  waist_cm: 1.5           # Important for shape
  hip_cm: 1.5             # Important for shape
  bust_cm: 1.0
  shoulder_width_cm: 1.0
  arm_length_cm: 0.8
  leg_length_cm: 0.8
  weight_kg: 0.3          # Soft signal only
```

### 4.3 Pose convention

For the MVP, we use a fixed **A-pose** (arms at ~45° from body, legs slightly apart). This is preferred over T-pose for:
1. More natural appearance
2. Less mesh self-intersection
3. More suitable for downstream garment try-on

---

## 5. Evaluation Flow

### 5.1 Stage 1 evaluation — Mesh closed-loop

This is run automatically after β optimization. It answers: **"Does the SMPL mesh actually have the right measurements?"**

```
β (fitted)
    ↓
SMPL forward pass → mesh (V, F)
    ↓
SMPL-Anthropometry.measure(V)
    ↓
estimated_measurements (dict)
    ↓
Compare with input_measurements
    ↓
evaluation_report.json
```

This is a perfect ground-truth check because SMPL-Anthropometry is the same tool used in the optimization loss. Any significant residual error indicates a convergence failure.

### 5.2 Stage 2 evaluation — Image round-trip (future)

This will answer: **"Does the rendered 2D image preserve body measurement information?"**

```
Rendered image (PNG)
    ↓
HMR2.0 or SMPLify-X
(reconstruct SMPL params from image)
    ↓
Recovered β'
    ↓
SMPL-Anthropometry.measure(SMPL(β'))
    ↓
image_estimated_measurements
    ↓
Compare with input_measurements
    ↓
evaluation_report_stage2.json
```

Note: Stage 2 evaluation introduces additional uncertainty from the image reconstruction model.

### 5.3 Experiment evaluation — Rank consistency

```
for measurement in [waist, hip, height]:
    for value in [v₁, v₂, v₃, v₄]:
        generate image with measurement=value
        estimate measurement from image

    check: does estimated_measurement rank match true_measurement rank?
    
    report: rank_consistency_score
```

---

## 6. Module Descriptions

### 6.1 `src/schemas/measurements.py`

**Purpose:** Defines and validates the input data structure.

**Key class:** `BodyMeasurements`

```python
# Conceptual structure (not final code)
class BodyMeasurements(BaseModel):
    gender: Literal["male", "female", "neutral"]
    height_cm: Optional[float]      # 140–220 cm
    weight_kg: Optional[float]      # 30–200 kg
    bust_cm: Optional[float]        # 60–150 cm
    waist_cm: Optional[float]       # 50–150 cm
    hip_cm: Optional[float]         # 60–160 cm
    shoulder_width_cm: Optional[float]  # 30–60 cm
    arm_length_cm: Optional[float]  # 40–90 cm
    leg_length_cm: Optional[float]  # 60–120 cm
```

All fields except `gender` are optional. Missing fields are filled with population-average defaults (documented in `config.yaml`).

### 6.2 `src/preprocessing/normalize.py`

**Purpose:** Converts validated measurements into a form usable by the body model optimizer.

Responsibilities:
- Fill missing measurements with gender-specific defaults
- Convert height from cm to meters (SMPL uses meters)
- Compute derived quantities (e.g., BMI as soft signal)
- Output a `MeasurementVector` for the optimizer

### 6.3 `src/body_model/smpl_wrapper.py`

**Purpose:** Wraps the `smplx` library with a clean interface.

Responsibilities:
- Load SMPL model from configured path
- Accept β and pose tensors
- Return vertices, faces, joints

Key design decision: **model is loaded once and cached**. Loading SMPL takes ~2 seconds; inference is <100ms.

### 6.4 `src/body_model/beta_optimizer.py`

**Purpose:** Converts target measurements into β parameters via gradient descent.

Responsibilities:
- Initialize β from prior
- Run Adam optimization loop
- Compute measurement loss using SMPL-Anthropometry callbacks
- Return optimized β + convergence metadata

### 6.5 `src/body_model/measurement_map.py`

**Purpose:** Maps high-level measurement names to SMPL mesh operations.

This is the most technically subtle module. SMPL-Anthropometry defines measurements as operations on the mesh (e.g., "waist circumference = circumference of a cross-section at vertex Y"). This module maps our input field names (`waist_cm`, `hip_cm`, etc.) to the corresponding SMPL-Anthropometry measurement names.

### 6.6 `src/generation/renderer.py`

**Purpose:** Renders the 3D SMPL mesh into a 2D image.

Responsibilities:
- Accept (vertices, faces) from SMPL wrapper
- Set up pyrender scene: mesh, camera, lighting
- Configure camera for full-body front view
- Render offscreen → return PIL.Image

Key design: camera position and field-of-view are configurable in `config.yaml` to ensure consistent framing across different body heights.

### 6.7 `src/evaluation/estimator.py`

**Purpose:** Estimates body measurements from a rendered image.

Stage 1: Direct mesh measurement (no image needed — uses β directly)  
Stage 2: Uses HMR2.0 to reconstruct β from image, then measures

### 6.8 `src/evaluation/metrics.py`

**Purpose:** Computes evaluation metrics from input and estimated measurements.

Functions:
- `absolute_error(input, estimated)` → dict of AME per measurement
- `relative_error(input, estimated)` → dict of RME
- `proportion_error(input, estimated)` → WHR, SHR errors
- `rank_consistency(values, estimated_values)` → score 0–1
- `format_report(input, estimated, errors)` → formatted text report

### 6.9 `src/pipeline.py`

**Purpose:** Top-level public API.

```python
def generate_body(
    measurements: dict,
    seed: int = 42,
    save_path: Optional[str] = None
) -> PIL.Image:
    ...
```

This is the **only** function the VTO system needs to call.

---

## 7. Input / Output Contracts

### 7.1 Public API input

```python
measurements = {
    # Required
    "gender": "female",          # "male" | "female" | "neutral"
    
    # Recommended (at least height + one of waist/hip)
    "height_cm": 160.0,
    "waist_cm": 66.0,
    "hip_cm": 90.0,
    
    # Optional
    "weight_kg": 52.0,
    "bust_cm": 84.0,
    "shoulder_width_cm": 38.0,
    "arm_length_cm": 56.0,
    "leg_length_cm": 88.0,
}

seed = 42   # int, for reproducibility
```

### 7.2 Public API output

```python
image: PIL.Image  
# Mode: RGB
# Size: configurable (default 512 × 768 for portrait full-body)
# Content: front-view rendered body mesh
```

Optional:
```python
metadata: dict  # {
#   "beta": [list of 10 floats],
#   "convergence_error": float,
#   "estimated_measurements": {...},
#   "generation_time_seconds": float
# }
```

### 7.3 Evaluation script output

```json
{
  "input_measurements": {...},
  "estimated_measurements_mesh": {...},
  "errors_stage1": {
    "height_cm": {"absolute": 0.5, "relative": 0.003},
    "waist_cm": {"absolute": 0.8, "relative": 0.012},
    ...
  },
  "proportion_errors": {
    "WHR": 0.004,
    "SHR": 0.006
  },
  "convergence": {
    "iterations": 200,
    "final_loss": 0.0023
  }
}
```

---

## 8. Staged Implementation Plan

### Stage 1 — Measurement-controlled mesh rendering

**Goal:** Prove that measurements control body shape.

**Deliverables:**
- Working `generate_body()` function
- β optimization convergence
- Front-view SMPL mesh rendered as PNG
- Stage 1 evaluation report (closed-loop mesh measurements)
- Experiment scripts (vary 1 measurement at a time)

**Does not include:**
- Photorealism
- Image texture / skin color
- Background

**Success criterion:**
> Varying `waist_cm` from 60 to 75 (all else fixed) produces images where the waist region visually narrows/widens in the correct direction.

### Stage 2 — Measurement validation

**Goal:** Estimate measurements from rendered image and quantify error.

**Deliverables:**
- `evaluation/estimator.py` with HMR2.0 or SMPLify integration
- Stage 2 evaluation report (image round-trip)
- Updated experiment reports with image-level errors

### Stage 3 — Photorealistic rendering

**Goal:** Replace mesh render with photorealistic output, maintaining measurement control.

**Deliverables:**
- `generation/diffusion_renderer.py` (ControlNet depth/normal conditioning)
- Comparison: Stage 1 mesh vs. Stage 3 photorealistic
- Updated evaluation metrics

---

## 9. Dependency Graph

```
pipeline.generate_body()
    │
    ├── schemas.BodyMeasurements
    │       └── pydantic
    │
    ├── preprocessing.normalize
    │       └── numpy
    │
    ├── body_model.beta_optimizer
    │       ├── body_model.smpl_wrapper
    │       │       └── smplx (pip)
    │       ├── body_model.measurement_map
    │       │       └── SMPL-Anthropometry (git clone)
    │       └── torch (optimizer)
    │
    └── generation.renderer
            ├── pyrender (pip)
            ├── trimesh (pip)
            └── PIL / Pillow (pip)
```

**External model files (not pip):**
- `SMPL_NEUTRAL.pkl` / `SMPL_FEMALE.pkl` / `SMPL_MALE.pkl`
  - Download from: https://smpl.is.tue.mpg.de/ (requires registration)
  - Store at: `body_fit/models/smpl/`

---

## 10. Configuration Design

All tunable parameters live in `config/config.yaml`. Nothing is hardcoded in module files.

```yaml
# config/config.yaml

model:
  type: "smpl"                  # smpl | smplx
  model_dir: "models/smpl"
  
optimizer:
  max_iterations: 300
  learning_rate: 0.05
  beta_regularization: 0.1
  convergence_threshold: 1e-4   # loss change per iteration
  
measurement_weights:
  height_cm: 2.0
  waist_cm: 1.5
  hip_cm: 1.5
  bust_cm: 1.0
  shoulder_width_cm: 1.0
  arm_length_cm: 0.8
  leg_length_cm: 0.8
  weight_kg: 0.3

defaults:
  # Gender-specific defaults for missing measurements
  # Source: WHO reference data + SMPL mean body
  female:
    height_cm: 163.0
    weight_kg: 62.0
    bust_cm: 89.0
    waist_cm: 74.0
    hip_cm: 97.0
    shoulder_width_cm: 38.0
    arm_length_cm: 57.0
    leg_length_cm: 89.0
  male:
    height_cm: 175.0
    weight_kg: 80.0
    bust_cm: 97.0
    waist_cm: 84.0
    hip_cm: 97.0
    shoulder_width_cm: 45.0
    arm_length_cm: 64.0
    leg_length_cm: 97.0

rendering:
  width: 512
  height: 768
  camera_distance: 3.0          # meters from body
  camera_fov_degrees: 30        # narrow FOV reduces perspective distortion
  background_color: [240, 240, 240]   # light gray
  body_color: [200, 180, 160]   # warm neutral skin-approximate color

pose:
  type: "a_pose"                # a_pose | t_pose | custom
  
output:
  format: "PNG"
  save_metadata: true
```

---

## 11. Integration Points for Upstream VTO System

Body Fit is designed for easy integration. The VTO system only needs:

```python
from body_fit.src.pipeline import generate_body

image = generate_body(
    measurements={
        "gender": "female",
        "height_cm": 160,
        "waist_cm": 66,
        "hip_cm": 90,
    },
    seed=42
)

# image is a PIL.Image
# Pass it to the garment try-on pipeline
```

**No other imports from body_fit are needed.**

The `metadata` dict is available for debugging and logging but is not required by the VTO pipeline.

---

*End of architecture document. Proceed to implementation after approval.*
