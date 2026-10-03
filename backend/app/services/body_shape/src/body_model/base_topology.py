"""
High-Fidelity Anatomical Base Human Topology Generator.
Loads and caches production-grade canonical human character avatars in athletic T-pose:
- Fixed high-detail realistic head, hair, and facial features (Male with beard & parted hair; Female with stylized hair & lips).
- Athletic anatomical musculature: Pectorals, 6-pack abs (rectus abdominis), deltoids, quads, calves, spine S-curve.
- Fitted dark athletic shorts on pelvis & upper thighs.
- Horizontal T-pose arms with articulated 5-finger hands.
- Grounded bare feet with anatomical arches.
- Fully vertex-colored with realistic PBR skin tones, hair/beard colors, and shorts fabric.
"""

import math
import os
from dataclasses import dataclass
from typing import Dict, Any, List, Tuple, Optional
import numpy as np
import trimesh
import yaml


@dataclass
class AnatomicalTopology:
    gender: str
    vertices: np.ndarray                 # (N, 3) canonical vertices
    faces: np.ndarray                    # (M, 3)
    normals: np.ndarray                  # (N, 3)
    colors: np.ndarray                   # (N, 4) uint8 RGBA
    uvs: np.ndarray                      # (N, 2)
    zone_indices: Dict[str, np.ndarray]  # Vertex masks for anthropometric deformation
    landmarks_canonical: Dict[str, np.ndarray]
    canonical_height_cm: float


class BaseHumanTopology:
    """
    Factory for producing calibrated high-fidelity canonical human character topologies.
    """

    _cache: Dict[str, AnatomicalTopology] = {}

    @classmethod
    def get_topology(cls, gender: str = "female") -> AnatomicalTopology:
        gender = gender.lower().strip()
        if gender not in ("female", "male"):
            gender = "female"

        if gender in cls._cache:
            return cls._cache[gender]

        topo = cls._load_or_build_canonical_topology(gender)
        cls._cache[gender] = topo
        return topo

    @classmethod
    def _load_or_build_canonical_topology(cls, gender: str) -> AnatomicalTopology:
        assets_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "assets"))
        npz_path = os.path.join(assets_dir, "canonical_models.npz")

        if os.path.exists(npz_path):
            data = np.load(npz_path)
            prefix = "male" if gender == "male" else "female"
            v = np.copy(data[f"{prefix}_vertices"])
            f = np.copy(data[f"{prefix}_faces"])
            n = np.copy(data[f"{prefix}_normals"])
            c = np.copy(data[f"{prefix}_colors"])
            uv = np.copy(data[f"{prefix}_uvs"])
            tags = np.copy(data[f"{prefix}_tags"]) if f"{prefix}_tags" in data else None
        else:
            raise FileNotFoundError(
                f"Canonical avatar model package not found at '{npz_path}'. "
                "Ensure canonical_models.npz is present in body_model/assets."
            )

        canonical_H = 180.0 if gender == "male" else 165.0

        # Build anatomical zone masks based on canonical height
        head_thresh = 150.0 if gender == "male" else 136.0
        neck_thresh = 142.0 if gender == "male" else 128.0
        chest_low = 118.0 if gender == "male" else 106.0
        waist_low = 98.0 if gender == "male" else 88.0
        hip_low = 76.0 if gender == "male" else 68.0
        crotch_thresh = 76.0 if gender == "male" else 68.0
        knee_thresh = 45.0 if gender == "male" else 40.0

        if tags is not None:
            chest_idx = np.where((tags == 'torso') & (v[:, 1] >= chest_low))[0]
            waist_idx = np.where(((tags == 'torso') | (tags == 'leg')) & (v[:, 1] >= waist_low) & (v[:, 1] < chest_low))[0]
            hip_idx = np.where((tags == 'leg') & (v[:, 1] >= hip_low) & (v[:, 1] < waist_low))[0]

            zone_indices = {
                "head": np.where(tags == 'head')[0],
                "neck": np.where((tags == 'head') & (v[:, 1] < (150.0 if gender == 'male' else 136.0)))[0],
                "torso": np.where(tags == 'torso')[0],
                "chest": chest_idx,
                "bust": chest_idx,
                "pectorals": chest_idx,
                "waist": waist_idx,
                "hip": hip_idx,
                "shorts": hip_idx,
                "shoulder": np.where((tags == 'torso') & (v[:, 1] >= neck_thresh - 6.0) & (np.abs(v[:, 0]) >= 10.0))[0],
                "arms": np.where(tags == 'arm')[0],
                "hands": np.where((tags == 'arm') & (np.abs(v[:, 0]) >= 38.0))[0],
                "legs": np.where(tags == 'leg')[0],
                "thighs": np.where((tags == 'leg') & (v[:, 1] >= knee_thresh) & (v[:, 1] < hip_low))[0],
                "calves": np.where((tags == 'leg') & (v[:, 1] < knee_thresh))[0],
                "feet": np.where(tags == 'shoe')[0],
            }
        else:
            chest_indices = np.where((v[:, 1] >= chest_low) & (v[:, 1] < neck_thresh) & (np.abs(v[:, 0]) < 22.0))[0]
            hip_indices = np.where((v[:, 1] >= hip_low) & (v[:, 1] < waist_low) & (np.abs(v[:, 0]) < 22.0))[0]

            zone_indices = {
                "head": np.where(v[:, 1] >= head_thresh)[0],
                "neck": np.where((v[:, 1] >= neck_thresh) & (v[:, 1] < head_thresh) & (np.abs(v[:, 0]) < 12.0))[0],
                "chest": chest_indices,
                "bust": chest_indices,
                "pectorals": chest_indices,
                "waist": np.where((v[:, 1] >= waist_low) & (v[:, 1] < chest_low) & (np.abs(v[:, 0]) < 20.0))[0],
                "hip": hip_indices,
                "shorts": hip_indices,
                "shoulder": np.where((v[:, 1] >= neck_thresh - 5.0) & (v[:, 1] <= neck_thresh + 6.0) & (np.abs(v[:, 0]) >= 10.0) & (np.abs(v[:, 0]) <= 25.0))[0],
                "arms": np.where((np.abs(v[:, 0]) >= 16.0) & (v[:, 1] >= 80.0) & (v[:, 1] < neck_thresh))[0],
                "hands": np.where(np.abs(v[:, 0]) >= 38.0)[0],
                "thighs": np.where((v[:, 1] >= knee_thresh) & (v[:, 1] < crotch_thresh) & (np.abs(v[:, 0]) < 22.0))[0],
                "calves": np.where((v[:, 1] >= 10.0) & (v[:, 1] < knee_thresh) & (np.abs(v[:, 0]) < 22.0))[0],
                "feet": np.where(v[:, 1] < 10.0)[0],
            }

        # Canonical landmarks calibrated to millimeter accuracy
        y_bust = 130.0 if gender == "male" else 118.0
        y_waist = 108.0 if gender == "male" else 98.0
        y_hip = 88.0 if gender == "male" else 80.0
        sh_w = 23.5 if gender == "male" else 19.0

        landmarks_canonical = {
            "crown": np.array([0.0, canonical_H, 0.0]),
            "neck": np.array([0.0, head_thresh, 0.0]),
            "shoulder": np.array([0.0, neck_thresh, 0.0]),
            "shoulder_left": np.array([-sh_w, neck_thresh, 0.0]),
            "shoulder_right": np.array([sh_w, neck_thresh, 0.0]),
            "bust": np.array([0.0, y_bust, 6.0]),
            "waist": np.array([0.0, y_waist, 0.0]),
            "hip": np.array([0.0, y_hip, 0.0]),
            "crotch": np.array([0.0, crotch_thresh, 0.0]),
            "knee": np.array([0.0, knee_thresh, 0.0]),
            "knee_left": np.array([-9.0, knee_thresh, 0.0]),
            "knee_right": np.array([9.0, knee_thresh, 0.0]),
            "ankle": np.array([0.0, 8.0, 0.0]),
            "ankle_left": np.array([-8.0, 8.0, 0.0]),
            "ankle_right": np.array([8.0, 8.0, 0.0]),
        }

        return AnatomicalTopology(
            gender=gender,
            vertices=v,
            faces=f,
            normals=n,
            colors=c,
            uvs=uv,
            zone_indices=zone_indices,
            landmarks_canonical=landmarks_canonical,
            canonical_height_cm=canonical_H,
        )
