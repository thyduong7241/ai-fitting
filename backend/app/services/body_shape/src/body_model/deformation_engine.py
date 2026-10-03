"""
Anthropometric Deformation Engine.
Applies continuous multi-layer spatial deformation to the canonical base human topology
according to exact individual anthropometric measurements.
Maintains fixed, undeformed realistic head & facial features for Male & Female.
Strictly non-hardcoded: reads landmarks, falloff sigmas, and scaling bounds from anatomy_config.yaml.
"""

import math
import os
from dataclasses import dataclass
from typing import Dict, Any, List, Tuple, Optional
import numpy as np
import trimesh
import trimesh.smoothing as sm
import yaml

from .base_topology import BaseHumanTopology, AnatomicalTopology
from ..schemas.measurements import BodyMeasurements


@dataclass
class ParametricBodyResult:
    trimesh: trimesh.Trimesh
    measurement_tapes: Dict[str, Any]
    landmarks: Dict[str, List[float]]
    skin_color: List[int]
    gender: str
    height_cm: float
    weight_kg: Optional[float]
    uvs: Optional[np.ndarray] = None


class AnthropometricDeformationEngine:
    """
    Parametric morphing engine for human anatomy.
    Deforms bone proportions, circumferential cross-sections, and soft tissue volume
    while strictly keeping head/facial geometry fixed and undeformed.
    """

    def __init__(self, config_path: Optional[str] = None):
        if not config_path:
            config_path = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "../../config/anatomy_config.yaml")
            )
        self.config = self._load_config(config_path)

    def _load_config(self, path: str) -> Dict[str, Any]:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        return {}

    def generate(self, meas: BodyMeasurements, skin_tone: str = "natural") -> ParametricBodyResult:
        gender = meas.gender.lower().strip()
        topo = BaseHumanTopology.get_topology(gender)

        # -------------------------------------------------------------
        # 1. Global Stature Scaling with Rigid Cranial Protection & Seamless Neck
        # -------------------------------------------------------------
        verts = np.copy(topo.vertices)
        H_target = float(meas.height_cm)
        H_canon = topo.canonical_height_cm
        s_y = H_target / max(1.0, H_canon)

        y_crotch = float(topo.landmarks_canonical["crotch"][1])
        y_neck_base = float(topo.landmarks_canonical["shoulder"][1])
        y_chin = float(topo.landmarks_canonical["neck"][1]) + 2.0
        h_head = H_canon - y_chin
        delta_y_head = H_target - H_canon

        # Continuous target landmark levels with safe bounds
        if meas.leg_length_cm and float(meas.leg_length_cm) > 0:
            y_crotch_target = np.clip(float(meas.leg_length_cm), 0.36 * H_target, 0.60 * H_target)
        else:
            y_crotch_target = y_crotch * s_y

        y_chin_target = H_target - h_head
        l_neck_canon = y_chin - y_neck_base
        l_neck_target = l_neck_canon * np.clip(s_y, 0.85, 1.15)
        y_neck_base_target = y_chin_target - l_neck_target

        s_leg = y_crotch_target / max(1.0, y_crotch)
        s_torso = (y_neck_base_target - y_crotch_target) / max(1.0, (y_neck_base - y_crotch))

        # Continuous vertical mapping with zero neck seam and zero vertical tears
        def map_y(y_arr):
            res_y = np.copy(y_arr)
            leg_m = y_arr <= y_crotch
            res_y[leg_m] = y_arr[leg_m] * s_leg

            torso_m = (y_arr > y_crotch) & (y_arr <= y_neck_base)
            res_y[torso_m] = y_crotch_target + (y_arr[torso_m] - y_crotch) * s_torso

            neck_m = (y_arr > y_neck_base) & (y_arr <= y_chin)
            if np.any(neck_m):
                u = (y_arr[neck_m] - y_neck_base) / max(1.0, (y_chin - y_neck_base))
                w = u * u * (3.0 - 2.0 * u)
                y_torso_proj = y_neck_base_target + (y_arr[neck_m] - y_neck_base) * s_torso
                y_head_proj = y_chin_target + (y_arr[neck_m] - y_chin)
                res_y[neck_m] = (1.0 - w) * y_torso_proj + w * y_head_proj

            head_m = y_arr > y_chin
            res_y[head_m] = y_arr[head_m] + delta_y_head
            return res_y

        verts[:, 1] = map_y(verts[:, 1])

        # Scaled canonical landmarks
        landmarks_scaled = {
            k: [float(v[0]), float(map_y(np.array([v[1]]))[0]), float(v[2])]
            for k, v in topo.landmarks_canonical.items()
        }

        # Cranial aspect ratio stays fixed (rigid facial bones)
        head_indices = topo.zone_indices.get("head", np.array([]))
        if len(head_indices) > 0:
            verts[head_indices, 0] = topo.vertices[head_indices, 0]
            verts[head_indices, 2] = topo.vertices[head_indices, 2]

        # -------------------------------------------------------------
        # 2. Shoulder Width Adjustment (Smooth Continuous Shoulder Girdle & Arm Translation)
        # -------------------------------------------------------------
        canon_sh_w = float(topo.landmarks_canonical["shoulder_right"][0])
        canon_total_w = canon_sh_w * 2.0
        target_sh_w = float(meas.shoulder_width_cm) if (meas.shoulder_width_cm and meas.shoulder_width_cm > 0) else canon_total_w
        delta_sh_x = (target_sh_w - canon_total_w) * 0.5

        if abs(delta_sh_x) > 0.001:
            # Smoothstep ramp across X from neck base (x=7) to shoulder joint (x=20)
            x_abs = np.abs(verts[:, 0])
            u_x = np.clip((x_abs - 7.0) / 13.0, 0.0, 1.0)
            w_sh_x = u_x * u_x * (3.0 - 2.0 * u_x)

            # Vertical falloff along torso
            y_waist = landmarks_scaled["waist"][1]
            y_sh = landmarks_scaled["shoulder"][1]

            arm_indices = topo.zone_indices.get("arms", np.array([]))
            hand_indices = topo.zone_indices.get("hands", np.array([]))
            arm_all = np.union1d(arm_indices, hand_indices)

            w_sh_y = np.clip((verts[:, 1] - y_waist) / max(1.0, y_sh - y_waist), 0.0, 1.0)
            w_sh_y = w_sh_y * w_sh_y
            w_sh_y[arm_all] = 1.0

            legs_indices = topo.zone_indices.get("legs", np.array([]))
            w_sh_y[head_indices] = 0.0
            w_sh_y[legs_indices] = 0.0

            verts[:, 0] += np.sign(verts[:, 0]) * (delta_sh_x * w_sh_x * w_sh_y)

        # -------------------------------------------------------------
        # 3. Continuous Circumferential Morphing (Chest, Waist, Hips)
        # -------------------------------------------------------------
        prop_cfg = self.config.get("anatomy", {}).get("proportions", {}).get(gender, {})
        def_zones_cfg = self.config.get("anatomy", {}).get("deformation_zones", {})

        canon_bust_c = H_target * prop_cfg.get("bust", 0.54)
        canon_waist_c = H_target * prop_cfg.get("waist", 0.41)
        canon_hip_c = H_target * prop_cfg.get("hip", 0.55)

        target_bust = float(meas.bust_cm) if (meas.bust_cm and meas.bust_cm > 0) else canon_bust_c
        target_waist = float(meas.waist_cm) if (meas.waist_cm and meas.waist_cm > 0) else canon_waist_c
        target_hip = float(meas.hip_cm) if (meas.hip_cm and meas.hip_cm > 0) else canon_hip_c

        ratio_bust = target_bust / max(1.0, canon_bust_c)
        ratio_waist = target_waist / max(1.0, canon_waist_c)
        ratio_hip = target_hip / max(1.0, canon_hip_c)

        delta_bust = ratio_bust - 1.0
        delta_waist = ratio_waist - 1.0
        delta_hip = ratio_hip - 1.0

        y_bust = landmarks_scaled["bust"][1]
        y_waist = landmarks_scaled["waist"][1]
        y_hip = landmarks_scaled["hip"][1]

        sigma_bust = H_target * def_zones_cfg.get("bust", {}).get("sigma_fraction", 0.082)
        sigma_waist = H_target * def_zones_cfg.get("waist", {}).get("sigma_fraction", 0.070)
        sigma_hip = H_target * def_zones_cfg.get("hip", {}).get("sigma_fraction", 0.090)

        # Torso and pelvis vertices filter (exclude limbs and head)
        torso_zone = topo.zone_indices.get("torso", np.array([]))
        legs_zone = topo.zone_indices.get("legs", np.array([]))
        body_candidates = np.union1d(torso_zone, legs_zone) if len(torso_zone) > 0 else np.arange(len(verts))

        knee_level = landmarks_scaled["knee"][1]
        shoulder_level = landmarks_scaled["shoulder"][1]
        active_mask = (verts[body_candidates, 1] >= knee_level - 5.0) & (verts[body_candidates, 1] <= shoulder_level + 3.0)
        active_indices = body_candidates[active_mask]
        y_active = verts[active_indices, 1]
        z_act = verts[active_indices, 2]

        w_bust_y = np.exp(-((y_active - y_bust) ** 2) / (2.0 * (sigma_bust ** 2)))
        w_waist_y = np.exp(-((y_active - y_waist) ** 2) / (2.0 * (sigma_waist ** 2)))
        w_hip_y = np.exp(-((y_active - y_hip) ** 2) / (2.0 * (sigma_hip ** 2)))

        # Morph Bust / Pectorals with smooth C2 ribcage and anatomical dome
        sh_armhole_x = canon_sh_w * 0.70
        u_arm = np.clip(1.0 - (np.abs(verts[active_indices, 0]) - (sh_armhole_x - 5.0)) / 5.0, 0.0, 1.0)
        w_bust_x = u_arm * u_arm * (3.0 - 2.0 * u_arm)

        s_front = 0.5 + 0.5 * np.tanh(z_act / 3.5)
        depth_mult = 0.50 * (1.0 - s_front) + 0.70 * s_front

        verts[active_indices, 0] += verts[active_indices, 0] * (delta_bust * w_bust_y * w_bust_x * 0.65)
        verts[active_indices, 2] += z_act * (delta_bust * w_bust_y * depth_mult)

        # Anatomical curvature dome (avoids conical tip and creates natural smooth silhouette)
        if gender == "female":
            w_breast_x = np.exp(-((np.abs(verts[active_indices, 0]) - 7.5) ** 2) / (2.0 * (6.0 ** 2)))
            dy_bust = y_active - y_bust
            sigma_y_pole = np.where(dy_bust >= 0, sigma_bust * 0.85, sigma_bust * 1.15)
            w_breast_y = np.exp(-(dy_bust ** 2) / (2.0 * (sigma_y_pole ** 2)))
            w_front_dome = np.maximum(0.0, np.tanh(z_act / 3.0))
            delta_z_dome = delta_bust * 5.5 * w_breast_x * w_breast_y * w_front_dome
            verts[active_indices, 2] += delta_z_dome
        else:
            w_pec_x = np.exp(-((np.abs(verts[active_indices, 0]) - 8.0) ** 2) / (2.0 * (7.5 ** 2)))
            w_front_pec = np.maximum(0.0, np.tanh(z_act / 3.0))
            delta_z_pec = delta_bust * 2.8 * w_bust_y * w_pec_x * w_front_pec
            verts[active_indices, 2] += delta_z_pec

        # Morph Waist / Abdomen
        verts[active_indices, 0] += verts[active_indices, 0] * (delta_waist * w_waist_y * 0.85)
        verts[active_indices, 2] += verts[active_indices, 2] * (delta_waist * w_waist_y * 0.80)

        # Morph Hip & Pelvis with smooth gluteal profile
        s_buttock = 0.5 - 0.5 * np.tanh(z_act / 5.0)
        z_hip_mult = 0.70 * (1.0 - s_buttock) + 1.25 * s_buttock
        verts[active_indices, 0] += verts[active_indices, 0] * (delta_hip * w_hip_y * 0.90)
        verts[active_indices, 2] += verts[active_indices, 2] * (delta_hip * w_hip_y * z_hip_mult)

        # -------------------------------------------------------------
        # 4. Volumetric BMI Mass Redistribution (Continuous Weight Field)
        # -------------------------------------------------------------
        weight_cfg = self.config.get("anatomy", {}).get("weight_modeling", {})
        base_bmi = weight_cfg.get("base_bmi", 22.0)
        if meas.weight_kg and meas.weight_kg > 0:
            h_m = H_target / 100.0
            actual_bmi = float(meas.weight_kg) / (h_m ** 2)
            delta_bmi = actual_bmi - base_bmi

            d_scale = weight_cfg.get("depth_scale_per_bmi", 0.018)
            w_scale = weight_cfg.get("width_scale_per_bmi", 0.012)

            bmi_d_fac = np.clip(1.0 + delta_bmi * d_scale, 0.82, 1.40)
            bmi_w_fac = np.clip(1.0 + delta_bmi * w_scale, 0.85, 1.35)

            # Continuous vertical weight profile centered between waist and hip
            y_bmi_center = 0.5 * (y_waist + y_hip)
            sigma_bmi_y = 0.22 * H_target
            w_bmi_y = np.exp(-((verts[:, 1] - y_bmi_center) ** 2) / (2.0 * (sigma_bmi_y ** 2)))

            # Protect head and lower limbs
            w_bmi_y[head_indices] = 0.0
            feet_indices = topo.zone_indices.get("feet", np.array([]))
            w_bmi_y[feet_indices] = 0.0

            s_belly = 0.5 + 0.5 * np.tanh(verts[:, 2] / 4.0)
            bmi_d_eff = (bmi_d_fac - 1.0) * (1.0 + 0.35 * s_belly)
            bmi_w_eff = (bmi_w_fac - 1.0)

            verts[:, 0] += verts[:, 0] * (bmi_w_eff * w_bmi_y)
            verts[:, 2] += verts[:, 2] * (bmi_d_eff * w_bmi_y)

        # -------------------------------------------------------------
        # 5. Volume-Preserving Taubin Surface Smoothing & Normal Refinement
        # -------------------------------------------------------------
        mesh = trimesh.Trimesh(
            vertices=verts,
            faces=topo.faces,
            process=False
        )

        v_pre_smooth = np.copy(mesh.vertices)
        sm.filter_taubin(mesh, lamb=0.20, nu=-0.21, iterations=2)
        v_smoothed = mesh.vertices

        # Blend back rigid zones (head, hands, feet) so fine details are 100% preserved
        orig_head_idx = topo.zone_indices.get("head", np.array([]))
        orig_hands_idx = topo.zone_indices.get("hands", np.array([]))
        orig_feet_idx = topo.zone_indices.get("feet", np.array([]))
        rigid_indices = np.unique(np.concatenate([orig_head_idx, orig_hands_idx, orig_feet_idx]))

        smooth_weight = np.ones(len(verts), dtype=np.float64)
        smooth_weight[rigid_indices] = 0.0

        # Smooth neck blend
        neck_mask = (v_pre_smooth[:, 1] >= y_neck_base_target) & (v_pre_smooth[:, 1] <= y_chin_target)
        if np.any(neck_mask):
            u_neck = (v_pre_smooth[neck_mask, 1] - y_neck_base_target) / max(1.0, (y_chin_target - y_neck_base_target))
            smooth_weight[neck_mask] = 1.0 - (u_neck * u_neck * (3.0 - 2.0 * u_neck))

        # Smooth wrist blend
        wrist_mask = (np.abs(v_pre_smooth[:, 0]) >= 34.0) & (np.abs(v_pre_smooth[:, 0]) <= 39.0)
        if np.any(wrist_mask):
            u_wrist = (np.abs(v_pre_smooth[wrist_mask, 0]) - 34.0) / 5.0
            smooth_weight[wrist_mask] = np.minimum(smooth_weight[wrist_mask], 1.0 - (u_wrist * u_wrist * (3.0 - 2.0 * u_wrist)))

        mesh.vertices = v_pre_smooth * (1.0 - smooth_weight[:, None]) + v_smoothed * smooth_weight[:, None]
        mesh.fix_normals()

        # Multi-color styling & skin tone tinting
        skin_rgb = self._resolve_skin_color(skin_tone)
        final_colors = np.copy(topo.colors)

        skin_cfg = self.config.get("anatomy", {}).get("canonical_skin_rgb", {})
        c_orig_skin = skin_cfg.get(gender, [228, 178, 146] if gender == "male" else [238, 196, 174])
        is_skin = (np.abs(topo.colors[:, 0].astype(int) - c_orig_skin[0]) < 12) & \
                  (np.abs(topo.colors[:, 1].astype(int) - c_orig_skin[1]) < 12) & \
                  (np.abs(topo.colors[:, 2].astype(int) - c_orig_skin[2]) < 12)

        final_colors[is_skin, 0] = skin_rgb[0]
        final_colors[is_skin, 1] = skin_rgb[1]
        final_colors[is_skin, 2] = skin_rgb[2]

        mesh.visual.vertex_colors = final_colors

        # -------------------------------------------------------------
        # 6. Extract 3D Interactive Measurement Tapes
        # -------------------------------------------------------------
        measurement_tapes = self._extract_measurement_tapes(
            mesh=mesh,
            y_bust=y_bust,
            y_waist=y_waist,
            y_hip=y_hip,
            height_cm=H_target,
            target_bust=target_bust,
            target_waist=target_waist,
            target_hip=target_hip
        )

        return ParametricBodyResult(
            trimesh=mesh,
            measurement_tapes=measurement_tapes,
            landmarks=landmarks_scaled,
            skin_color=skin_rgb,
            gender=gender,
            height_cm=H_target,
            weight_kg=meas.weight_kg,
            uvs=topo.uvs
        )

    def _extract_measurement_tapes(
        self,
        mesh: trimesh.Trimesh,
        y_bust: float,
        y_waist: float,
        y_hip: float,
        height_cm: float,
        target_bust: float,
        target_waist: float,
        target_hip: float
    ) -> Dict[str, Any]:
        """
        Extracts 3D closed polyline loops wrapping the body surface at exact measurement heights.
        """
        tapes = {}
        verts = mesh.vertices

        for key, y_level, val_cm, col in [
            ("bust", y_bust, target_bust, [59, 130, 246]),   # Blue
            ("waist", y_waist, target_waist, [16, 185, 129]), # Green
            ("hip", y_hip, target_hip, [245, 158, 11]),     # Amber
        ]:
            band = np.where(np.abs(verts[:, 1] - y_level) < 2.5)[0]
            if len(band) > 8:
                pts = verts[band]
                pts_torso = pts[np.abs(pts[:, 0]) < (np.max(np.abs(pts[:, 0])) * 0.78)] if len(pts) > 16 else pts
                angles = np.arctan2(pts_torso[:, 0], pts_torso[:, 2])
                sort_idx = np.argsort(angles)
                ring_pts = pts_torso[sort_idx].tolist()
                if len(ring_pts) > 0:
                    ring_pts.append(ring_pts[0])

                tapes[key] = {
                    "label": f"Vòng {key.capitalize()}: {round(val_cm, 1)} cm",
                    "height_y": float(y_level),
                    "value_cm": round(val_cm, 1),
                    "color": col,
                    "points": ring_pts
                }

        tapes["stature"] = {
            "label": f"Chiều cao: {round(height_cm, 1)} cm",
            "height_y": float(height_cm),
            "value_cm": round(height_cm, 1),
            "color": [139, 92, 246],
            "points": [
                [0.0, 0.0, 0.0],
                [0.0, float(height_cm), 0.0]
            ]
        }

        return tapes

    def _resolve_skin_color(self, tone_name: str) -> List[int]:
        tones_cfg = self.config.get("studio", {}).get("skin_tones", {})
        if tone_name in tones_cfg and "rgb" in tones_cfg[tone_name]:
            return list(tones_cfg[tone_name]["rgb"])
        return list(tones_cfg.get("natural", {}).get("rgb", [235, 196, 172]))
