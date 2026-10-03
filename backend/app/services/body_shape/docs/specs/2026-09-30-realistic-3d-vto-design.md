# Design Spec: Realistic 3D Human Body Anatomy & Dynamic Virtual Try-On

## Date: 2026-09-30
## Status: Approved (User Selected Realistic Anatomical Direction)

### 1. Problem Statement
The current 3D parametric avatar in `body_fit` generated body meshes via primitive stacked ellipses. This resulted in an unrealistic, balloon/tube-like avatar lacking key human anatomical features:
- Head had no facial profile (nose, jaw, chin).
- Torso lacked realistic breast/pectoral contours, scapulae, spinal curvature, and gluteal (buttocks) protrusion.
- Limbs were straight cylindrical tubes terminating in flat cross-sections, with no hands or feet.
- The 3D Try-On engine was hardcoded to a single 16cm short-sleeved t-shirt in a flat monotone color, completely ignoring garment categories (vests, jackets, coats, shirts), real product dimensions in size charts, and the high-resolution garment imagery available in the catalog.

### 2. Goals & Success Criteria
1. **Realistic 3D Human Anatomy**:
   - Parametric 3D mesh with distinct anatomical features for both female and male avatars.
   - Organic contours for head & face (jaw, nose, chin), neck & clavicle, torso (chest, waist, hips, spine, buttocks), arms & stylized hands, legs (thighs, knees, calves, ankles) & feet.
   - Smooth curvature, continuous normals, no harsh seams.
   - Dynamic responsiveness to all measurement inputs (height, weight/BMI, bust, waist, hip, shoulder width, arm length, leg length).
2. **Dynamic Product-Driven Virtual Try-On**:
   - Zero hardcoding of garment geometry.
   - Real garment silhouettes parsed from product metadata:
     - Sleeveless vests (0cm sleeve, contoured armholes).
     - Trench coats & long coats (extended hem down to thighs, long sleeves).
     - Jackets & bombers (waist-length, full sleeves, cuffs).
     - T-shirts & tops (crew/collar, short or long sleeves per product).
   - Accurate ease and drape sizing derived from each product's `size_chart` (`length`, `sleeve`, `shoulder`, `bust`).
3. **Photorealistic Garment Texturing**:
   - Full UV texture coordinate mapping generated on the garment mesh.
   - High-resolution product images from `D:/hackathon/assets/products` mapped seamlessly in Three.js and preserved in exported `.obj`.
4. **Performance & Reliability**:
   - Pure CPU computation under 100ms.
   - Zero external binary dependencies beyond standard Python packages (`trimesh`, `numpy`, `pillow`, `fastapi`).

### 3. Architecture & Data Flow
```
[User Measurements & Product Selection]
               │
               ▼
[ParametricBody3D] ─── Anatomical Slices ───► Watertight 3D Human Mesh
               │
               ▼
[GarmentEngine] ─── Product Category & Size Chart ───► Dynamic 3D Garment Mesh + UV Mapping
               │
               ▼
[FastAPI Server] ───► Three.js Web Viewer with TextureLoader & Realistic Materials
               │
               ▼
[OBJ + MTL Export] ───► Universal 3D CAD/Viewer compatibility
```

### 4. Verification Plan
- Unit tests in `tests/test_3d_vto.py` verifying anatomical features, multi-category garment generation, UV map validity.
- Visual browser verification covering male & female anatomies and diverse garment types (vest, coat, jacket).
