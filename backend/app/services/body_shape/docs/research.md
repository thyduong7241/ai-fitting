# Body Fit — Technical Research

> **Document status:** Pre-implementation research  
> **Author:** AI Engineer (Body Fit)  
> **Date:** 2026-09-28  
> **Version:** 1.0

---

## Table of Contents

1. [Problem Definition](#1-problem-definition)
2. [The Measurement-Consistency Challenge](#2-the-measurement-consistency-challenge)
3. [The Ambiguity Problem](#3-the-ambiguity-problem)
4. [Approach A — Direct Image-Generation Conditioning](#4-approach-a--direct-image-generation-conditioning)
5. [Approach B — Parametric Human Body Model](#5-approach-b--parametric-human-body-model)
6. [Approach C — 2D Pose-Conditioned Generation](#6-approach-c--2d-pose-conditioned-generation)
7. [Approach D — Hybrid (Parametric → Diffusion)](#7-approach-d--hybrid-parametric--diffusion)
8. [Comparison Table](#8-comparison-table)
9. [Relevant Models and Tools](#9-relevant-models-and-tools)
10. [Relevant Papers](#10-relevant-papers)
11. [Datasets](#11-datasets)
12. [Evaluation Pipeline Design](#12-evaluation-pipeline-design)
13. [MVP Recommendation](#13-mvp-recommendation)
14. [Risks](#14-risks)
15. [Assumptions](#15-assumptions)

---

## 1. Problem Definition

### 1.1 What we are building

Body Fit is a subsystem within a larger Virtual Try-On (VTO) platform.

Its sole responsibility:

```
Structured body measurements (JSON)
              ↓
Body Fit Pipeline
              ↓
2D full-body human image
with visually consistent body proportions
```

The output image serves as a *body canvas* for the VTO system. Other teams will place garments on it.

### 1.2 What "measurement-consistent" means for the MVP

This is a critical definition to establish before any implementation.

**We are NOT claiming:**
- The generated image looks like the real user
- The image is a precise reconstruction from measurements
- Pixel-level accuracy of body dimensions

**We ARE claiming:**
- If user A has a larger waist than user B (all else equal), the generated body for A should visually have a proportionally larger waist than B
- If waist decreases from 80 cm to 66 cm, the waist region in the image narrows accordingly
- The overall body silhouette reflects the gross proportions given (tall/short, heavy/lean, hip-dominant, etc.)

This is a **relative consistency** requirement, not an absolute reconstruction requirement.

### 1.3 Why this is not a standard text-to-image problem

Standard text-to-image models (e.g., Stable Diffusion with a prompt) generate a *random* person satisfying a text description. The same prompt will produce different body shapes on different runs.

We need **deterministic, measurement-controlled body shape**:

```
Measurements: waist=66, hip=90
→ specific body proportions
→ reproducible with seed

vs.

Prompt: "woman, slim waist"
→ unpredictable body proportions
→ no guarantee of correct hip-to-waist ratio
```

Text prompts cannot reliably encode precise numerical ratios like WHR (waist-to-hip ratio = 0.73), or a specific height-to-torso ratio.

---

## 2. The Measurement-Consistency Challenge

### 2.1 The inverse mapping problem

The core technical challenge is:

```
Measurements (numbers) → Body representation → Image
```

But to evaluate the system, we need:

```
Image → Body representation estimation → Measurement estimation
```

This second direction (image → measurements) is significantly harder because:
- Images are 2D projections of 3D bodies
- Depth information is lost
- Camera intrinsics are unknown
- Clothing, lighting, and pose all obscure true body shape

For the MVP, we will use **proxy metrics** (described in §12) instead of claiming pixel-level accuracy.

### 2.2 What measurements control what visual feature

| Measurement | Expected visual effect |
|---|---|
| `height_cm` | Overall scale / aspect ratio of the body |
| `weight_kg` | General "heaviness" — useful as a soft constraint |
| `bust_cm` | Chest width, especially for female bodies |
| `waist_cm` | Width of mid-section |
| `hip_cm` | Width of hip region |
| `shoulder_width_cm` | Width at shoulder joint level |
| `arm_length_cm` | Length of arm segments |
| `leg_length_cm` | Length of leg segments |

Note: `weight_kg` is partially redundant with circumference measurements. It is useful for deriving body-fat estimates and as a sanity-check signal, but not a primary shape driver.

---

## 3. The Ambiguity Problem

### 3.1 The same measurements, different bodies

Two real people can share identical:
- height, weight, bust, waist, hip, shoulder width

but differ in:
- torso/leg ratio (same height, different torso/leg split)
- fat vs. muscle distribution
- breast/chest shape
- posture (lordosis, kyphosis, etc.)
- body symmetry

This means the mapping from measurements to body shape is **one-to-many**. There is no unique correct image.

### 3.2 How the MVP handles this ambiguity

We accept ambiguity. The MVP makes these explicit design decisions:

| Ambiguous dimension | MVP resolution |
|---|---|
| Torso/leg ratio | Use population-average ratio for gender; override if `leg_length_cm` and `arm_length_cm` are both provided |
| Fat vs. muscle | Not distinguished. Use `weight_kg` + circumferences for approximate fatness |
| Posture | Fix to a standard neutral A-pose or T-pose for consistency |
| Body symmetry | Assume bilateral symmetry (left = right) |
| Breast shape | Not modeled in MVP |
| Face/identity | Random, de-identified |

**Terminology contract:** We will always call the output a *visually consistent body representation* or *measurement-approximate body image*, never a *body reconstruction* or *accurate body image* until we have objective validation.

---

## 4. Approach A — Direct Image-Generation Conditioning

### 4.1 How it works

Train or fine-tune a text-to-image diffusion model to accept numerical body measurements as conditioning signals alongside the text prompt.

```
[height=160, waist=66, hip=90, ...] + [text prompt]
          ↓
Modified UNet (with measurement conditioning)
          ↓
2D full-body image
```

The conditioning can be implemented as:
- **Textual conditioning only**: convert measurements to natural language ("a woman with 66 cm waist, 90 cm hips…")
- **Embedding injection**: learn a small MLP that converts measurement vectors into conditioning embeddings injected into the UNet's cross-attention layers
- **Fine-tuning**: fine-tune a base model (e.g., Stable Diffusion) on paired (measurement, image) data

### 4.2 Required input

- Numerical body measurements (any subset)
- Base diffusion model weights
- For fine-tuning: paired dataset of (image, body measurements)

### 4.3 Expected output

- 2D RGB image (512×512 or 768×768 typical)

### 4.4 Pretrained models

- **Text-only conditioning** (naive): Stable Diffusion 1.5 / SDXL — available on Hugging Face. No fine-tuning needed for text-only.
- **Direct measurement conditioning**: No publicly available pretrained model that directly takes numerical anthropometric measurements as input. Research prototypes exist (see §10) but are not released as ready-to-use models.

### 4.5 Training requirements

- **Text-only (no fine-tuning)**: no training needed, but low measurement control
- **Embedding injection**: requires fine-tuning on ~10K+ paired (image, measurement) samples
- **Full fine-tuning**: requires large dataset (50K+ samples), significant GPU time

### 4.6 Dataset requirements

For fine-tuning: images with ground-truth body measurements (not just pose annotations). Such datasets are rare because:
- Ground-truth circumference measurements require 3D scanning or manual tape measurement
- CAESAR dataset (3D body scans + measurements) exists but requires licensing
- SURREAL (synthetic) provides SMPL parameters but not direct cm measurements

### 4.7 Implementation complexity

| Sub-approach | Complexity |
|---|---|
| Text-only prompt engineering | Low |
| Embedding injection fine-tune | High |
| Full fine-tuning | Very High |

### 4.8 Inference speed

- CPU: 60–300 seconds per image
- Consumer GPU (RTX 3080): 3–15 seconds per image
- Cloud GPU (A100): ~1–3 seconds per image

### 4.9 Ability to control body measurements

**Low** (text-only) to **Medium** (with fine-tuning).

Even with measurement-conditioned fine-tuning, diffusion models are probabilistic. Measurement adherence is statistical — there is no guarantee a specific waist circumference appears in the image.

### 4.10 Expected visual quality

**High** — state-of-the-art photorealism. Stable Diffusion SDXL generates very realistic human images.

### 4.11 Main failure modes

- Measurement conditioning ignored by the model (text prompt dominates)
- Mode collapse to average body shapes
- Generated proportions correlate weakly with numerical inputs
- Requires large paired dataset for fine-tuning — hard to obtain
- No formal guarantee of measurement consistency

### 4.12 Suitability for MVP

**Low** as primary approach.  
- Measurement control is weak without fine-tuning  
- Fine-tuning requires paired data we don't have  
- Cannot formally verify measurement consistency  

**Viable as Stage 3 enhancement** (image quality boost after Stage 1-2 succeed).

---

## 5. Approach B — Parametric Human Body Model

### 5.1 Background: What is a parametric body model?

> **Concept explanation (for newcomers):**
>
> A parametric body model is a mathematical function that takes a small set of numbers (parameters) and produces a realistic 3D human body mesh. Think of it as a "body dial" — turning dial #1 makes the body taller, dial #2 makes the waist wider, etc.
>
> The most widely used is **SMPL** (Skinned Multi-Person Linear Model), developed by the Max Planck Institute. It was trained on thousands of 3D body scans and learned a compact representation of human body variation.
>
> SMPL has two key parameter sets:
> - **β (beta) — shape parameters**: 10 numbers that control body shape (how fat, tall, proportioned the body is). These are like "body type dials."
> - **θ (theta) — pose parameters**: 72 numbers that control joint angles (are the arms raised? legs spread?).

### 5.2 How the approach works

```
Measurements (height=160, waist=66, hip=90, ...)
              ↓
[Measurement → β mapping]
(optimization or learned regressor)
              ↓
SMPL/SMPL-X β parameters
              ↓
SMPL forward pass → 3D mesh (6890 vertices)
              ↓
pyrender / trimesh → rendered 2D image
```

#### Step 1: Measurement → β parameters

The SMPL model encodes shape in a 10-dimensional β space. We need to find β values that produce a body with the desired measurements.

**Two methods:**

**Method B.1 — Optimization (gradient descent):**
```
Initialize β = [0, 0, ..., 0]  (mean body)
Loop:
  body = SMPL(β)
  computed_measurements = SMPL_Anthropometry(body)
  loss = MSE(computed_measurements, target_measurements)
  β = β - lr * ∇β loss
Until convergence
```
This is exact but slow (~5–30 seconds per optimization). It is differentiable through PyTorch.

**Method B.2 — Learned regressor (A2B model):**
```
measurements_vector → small MLP → β
```
A neural network trained on (measurement, β) pairs. Inference is instant (<1 ms). Requires training data or a pretrained checkpoint.

The `kaulquappe23/a2b_human_mesh` repository provides a pretrained A2B model.

#### Step 2: SMPL → 3D mesh

```python
import smplx
model = smplx.create(model_path, model_type='smpl', gender='female')
output = model(betas=betas, body_pose=pose)
vertices = output.vertices  # shape (1, 6890, 3)
faces = model.faces          # shape (13776, 3)
```

#### Step 3: 3D mesh → 2D rendered image

Using pyrender + trimesh:
```python
import pyrender, trimesh
mesh = trimesh.Trimesh(vertices, faces)
scene = pyrender.Scene()
scene.add(pyrender.Mesh.from_trimesh(mesh))
renderer = pyrender.OffscreenRenderer(512, 768)
color, depth = renderer.render(scene)
```

### 5.3 Required input

- SMPL model weights (.pkl file, free for research — requires registration at smpl.is.tue.mpg.de)
- Body measurements (subset of: height, weight, bust, waist, hip, shoulder, arm, leg)
- Target pose (default: T-pose or A-pose)

### 5.4 Expected output

- 2D image of a 3D mesh rendered from front view
- **Visual style**: looks like a 3D mannequin / mesh render, not a photograph

This is a key trade-off: the image will not be photorealistic, but it will be *geometrically accurate*.

### 5.5 Pretrained models available?

| Component | Availability |
|---|---|
| SMPL model | Free for research (requires registration) |
| SMPL-X model | Free for research (requires registration) |
| `smplx` Python library | pip install smplx |
| SMPL-Anthropometry | Open-source (DavidBoja/SMPL-Anthropometry) |
| A2B regressor checkpoint | Available (kaulquappe23/a2b_human_mesh) |

### 5.6 Training requirements

- With A2B regressor: **no training needed** if we use the pretrained checkpoint
- With optimization-based β fitting: **no training needed**, only gradient descent at inference time
- If A2B model needs fine-tuning: dataset can be **synthesized** from SMPL itself

### 5.7 Dataset requirements

**Uniquely favorable:** We do not need real human photographs. We can generate arbitrary (measurement, β) pairs synthetically using SMPL-Anthropometry.

### 5.8 Implementation complexity

**Medium overall.** Each individual component is well-documented.

### 5.9 Inference speed

| Method | Speed |
|---|---|
| A2B regressor (instant β) | < 1 sec total |
| Optimization-based β fitting | 5–30 sec per image |
| SMPL forward pass | < 0.1 sec |
| pyrender rendering | < 1 sec |

### 5.10 Ability to control body measurements

**High** — strongest advantage of Approach B.

Because SMPL-Anthropometry can compute measurements directly from the mesh (forward direction), we have a closed loop:

```
Target measurements → β optimization → mesh → computed measurements
```

We can directly verify that the generated mesh has the correct measurements before rendering.

### 5.11 Expected visual quality

- **Geometric quality: Excellent** — accurate body silhouette
- **Photorealism: Low** — looks like a mesh, not a photograph
- **Practical quality:** Sufficient for Stage 1-2 MVP

### 5.12 Main failure modes

- β optimization may get stuck in local minima for extreme measurements
- SMPL has limited expressive range for some body types (very obese bodies)
- Rendered images look like a mannequin — acceptable for MVP, not for final product
- SMPL license restricts commercial use without separate agreement

### 5.13 Suitability for MVP

**High** — most appropriate primary approach for the MVP.

---

## 6. Approach C — 2D Pose-Conditioned Generation

### 6.1 How it works

> **Concept explanation:**
>
> ControlNet (Zhang et al., 2023) adds an extra conditioning pathway to a diffusion model. Instead of only text, it also accepts an image-like control signal such as a skeleton/pose map, depth map, or edge map.

```
Measurements
    ↓
Compute 2D keypoint positions
    ↓
Draw pose skeleton image (18-24 keypoints)
    ↓
ControlNet (OpenPose mode) + Stable Diffusion
    ↓
2D photorealistic image conditioned on skeleton
```

### 6.2 Pretrained models available?

**Yes.** ControlNet OpenPose is freely available on Hugging Face:
- `lllyasviel/control_v11p_sd15_openpose`
- SDXL-compatible ControlNet variants

### 6.3 Ability to control body measurements

**Low.** ControlNet controls limb proportions via keypoint positions, but does **not** control circumferences (waist, hip, bust). These must come from text prompt, which is unreliable.

### 6.4 Suitability for MVP

**Low as primary approach.** The most important measurements (circumferences) cannot be controlled.

**Viable as Stage 3 enhancement** when combined with Approach B.

---

## 7. Approach D — Hybrid (Parametric → Diffusion)

### 7.1 How it works

```
Measurements
    ↓
SMPL β fitting (Approach B)
    ↓
3D mesh → rendered depth/normal/silhouette
    ↓
ControlNet (depth or normal mode)
    ↓
Stable Diffusion
    ↓
Photorealistic 2D image matching SMPL body shape
```

The SMPL mesh render (which has exact body proportions) is used as ControlNet conditioning. This forces the diffusion model to follow the geometric body shape while generating photorealistic output.

### 7.2 Pretrained models available?

- SMPL: yes (registration required)
- ControlNet Depth: `lllyasviel/control_v11f1p_sd15_depth` (free)
- ControlNet Normal: `lllyasviel/control_v11p_sd15_normalbae` (free)

### 7.3 Ability to control body measurements

**Medium-High.** Body shape from SMPL is geometrically accurate; diffusion may drift slightly.

### 7.4 Suitability for MVP

**Too complex for Stage 1, but ideal Stage 3 target.**

---

## 8. Comparison Table

| Criterion | A: Direct Diffusion | B: Parametric (SMPL) | C: 2D Pose ControlNet | D: Hybrid (SMPL + Diffusion) |
|---|:---:|:---:|:---:|:---:|
| **No training required** | ❌ (for control) | ✅ | ✅ | ✅ |
| **No paired real data needed** | ❌ | ✅ | ✅ | ✅ |
| **Controls circumferences** | 🟡 weak | ✅ exact | ❌ none | ✅ good |
| **Controls proportions/lengths** | 🟡 weak | ✅ | ✅ | ✅ |
| **Photorealism** | ✅ high | ❌ mesh look | ✅ high | ✅ high |
| **Measurement verifiable** | ❌ | ✅ | ❌ | 🟡 partial |
| **Reproducible (seed)** | ✅ | ✅ | ✅ | ✅ |
| **CPU feasible** | 🟡 slow | ✅ | ❌ | ❌ |
| **Dev complexity** | Low | Medium | Medium | High |
| **Time to prototype** | Days | Days–Week | Days | Weeks |
| **Upgrade path** | Limited | **Excellent** | Limited | Best |
| **MVP suitability** | Low | **High** | Low | Too complex |

---

## 9. Relevant Models and Tools

### 9.1 Core body model

| Tool | Description | Link |
|---|---|---|
| **SMPL** | Parametric body model (10 shape + 72 pose params) | smpl.is.tue.mpg.de |
| **SMPL-X** | Extended SMPL with hands and face | smpl-x.is.tue.mpg.de |
| **`smplx` Python lib** | Official Python interface | `pip install smplx` |
| **SMPL-Anthropometry** | Measurement extraction from SMPL mesh | DavidBoja/SMPL-Anthropometry |
| **A2B regressor** | Learned measurement → β | kaulquappe23/a2b_human_mesh |

### 9.2 Rendering

| Tool | Description |
|---|---|
| **pyrender** | Python-based OpenGL renderer (offscreen) |
| **trimesh** | 3D mesh manipulation |
| **Open3D** | Alternative 3D visualization + rendering |

### 9.3 Diffusion models (for Stage 3)

| Model | Description |
|---|---|
| **Stable Diffusion 1.5** | Base text-to-image model |
| **SDXL** | Higher-quality base model |
| **ControlNet (OpenPose)** | Pose-conditioned generation |
| **ControlNet (Depth)** | Depth-conditioned generation |
| **diffusers (HuggingFace)** | Python pipeline library |

### 9.4 Evaluation tools

| Tool | Description |
|---|---|
| **MediaPipe Pose** | 2D keypoint detection from images |
| **ViTPose** | High-accuracy 2D pose estimation |
| **HMR2.0 / 4DHumans** | Monocular 3D body reconstruction from image |
| **SMPLify-X** | 2D keypoints → SMPL parameters |

---

## 10. Relevant Papers

| Paper | Year | Relevance |
|---|---|---|
| **SMPL: A Skinned Multi-Person Linear Model** (Loper et al.) | 2015 | Foundation of Approach B |
| **SMPL-X: Expressive Body Capture** (Pavlakos et al.) | 2019 | Extended SMPL model |
| **ControlNet: Adding Conditional Control to T2I Diffusion** (Zhang et al.) | 2023 | Foundation of Approach C/D |
| **Leveraging Anthropometric Measurements to Improve Human Mesh Estimation** (Kaulquappe et al.) | 2023 | A2B measurement → β mapping |
| **Measurements-to-Body** (2024) | 2024 | Direct measurement → 3D body shape |
| **BodyShapeGPT** (2024) | 2024 | LLM-driven SMPL shape manipulation |
| **BodyMetric** (2024) | 2024 | Evaluation of body proportion realism |
| **SURREAL: Synthetic Bodies for Learning** (Varol et al.) | 2017 | Synthetic training data |
| **SMPLify: Keep It SMPL** (Bogo et al.) | 2016 | Fitting SMPL to 2D keypoints |
| **HMR2.0** (Goel et al.) | 2023 | Monocular human mesh recovery |

---

## 11. Datasets

| Dataset | Content | License | Useful for |
|---|---|---|---|
| **CAESAR** | 3D body scans + 73 measurements, 4400 subjects | Commercial license | Ground-truth measurements for evaluation |
| **SURREAL** | Synthetic rendered SMPL bodies | Research only | Pre-training, synthetic augmentation |
| **Human3.6M** | Video + 3D pose, some shape info | Research only | Evaluation |
| **AGORA** | Synthetic realistic renderings with SMPL-X GT | Research | Appearance quality |
| **DeepFashion** | Fashion images with body keypoints | Research | Visual quality reference |

**Key observation:** For our MVP, we do **not** need any real-world dataset. We can synthesize (measurement, β) pairs entirely from SMPL + SMPL-Anthropometry.

---

## 12. Evaluation Pipeline Design

### 12.1 Overview

```
Input measurements (JSON)
        ↓
Body Fit Pipeline
        ↓
Generated image (PNG)
        ↓
Body measurement estimator
        ↓
Estimated measurements (JSON)
        ↓
Error computation
        ↓
Report
```

### 12.2 Available estimators

**Stage 1 evaluation (closed-loop, from mesh):**
```
Input β → SMPL mesh → SMPL-Anthropometry → estimated measurements
Error = |input_measurement - estimated_measurement|
```

**Stage 2 evaluation (image round-trip):**
```
Rendered image → HMR2.0 → recovered β → SMPL-Anthropometry → estimated measurements
Error = |input_measurement - image_estimated_measurement|
```

### 12.3 Proposed metrics

**Absolute Measurement Error (AME):**
```
AME(m) = |input_m - estimated_m|   [in cm]
```

**Relative Measurement Error (RME):**
```
RME(m) = |input_m - estimated_m| / input_m   [fraction]
```

**Proportion Error (PE):**
```
WHR_input = waist_cm / hip_cm
WHR_estimated = estimated_waist / estimated_hip
PE_WHR = |WHR_input - WHR_estimated|
```

**Rank Consistency (RC):**
For a set of images varying one measurement (e.g., waist ∈ {60, 65, 70, 75}):
```
RC = fraction of pairs where rank(estimated_waist_i) == rank(true_waist_i)
```

**Generation Consistency (GC):**
```
GC = std(estimated_measurement_i across seeds)
```

### 12.4 Why pixel-level metrics are wrong

Do NOT use:
- SSIM — images differ even if proportions are correct
- FID — measures distribution realism, not measurement fidelity
- LPIPS — perceptual similarity, not measurement fidelity

These are appropriate for Stage 3 (image quality), not Stage 1-2 (measurement consistency).

---

## 13. MVP Recommendation

### Recommended: **Approach B — SMPL parametric body model with optimization-based β fitting**

**Stage 1 (now):** Approach B — SMPL optimization → mesh render → 2D image

**Stage 3 (future):** Approach D — use SMPL mesh depth/normal as ControlNet signal → photorealistic image

**Rationale:**
1. Exact measurement control via closed-loop SMPL-Anthropometry
2. No real training data needed (synthetic pairs from SMPL)
3. Reproducible given seed
4. Modular — mesh can be wrapped with diffusion later
5. Established Python ecosystem (`smplx`, `pyrender`, `trimesh`)
6. Measurement verification is a first-class feature (not an afterthought)

---

## 14. Risks

| Risk | Severity | Likelihood | Mitigation |
|---|---|---|---|
| SMPL license prevents commercial use | High | Medium | Negotiate license before production |
| β optimization slow for production | Medium | High | Train lightweight A2B regressor at Stage 2 |
| β optimization diverges for extreme measurements | Medium | Low | Add β regularization; clamp β range |
| SMPL cannot represent very obese/thin bodies | Medium | Low | Document limitation; test boundary cases |
| Rendered images too synthetic for final product | High (Stage 3) | High | Planned: add diffusion at Stage 3 |
| Measurement estimator inaccurate in Stage 2 | Medium | Medium | Document as approximation; use HMR2.0 |
| pyrender issues on headless systems | Medium | Medium | Use OSMesa/EGL backend; test early |

---

## 15. Assumptions

| # | Assumption | Impact if wrong |
|---|---|---|
| A1 | SMPL's β space covers the input measurement range | Body shape wrong for extreme measurements |
| A2 | Bilateral body symmetry (left = right) | Does not represent asymmetric bodies |
| A3 | Standard neutral A-pose for all generated images | Pose may not suit downstream garment try-on |
| A4 | Single front-view rendering sufficient for MVP | May not expose all body proportions |
| A5 | Gender is binary (male/female) in SMPL | Does not support non-binary representations |
| A6 | Missing measurements filled with population-average defaults | Generated body may not reflect user if critical measurements absent |
| A7 | BMI is a reasonable proxy for weight → fatness | BMI is imperfect for individuals |
| A8 | SMPL-Anthropometry measurement definitions match real tape measurements | Measurement protocols may differ |

---

*End of research document. Next: `docs/architecture.md`*
