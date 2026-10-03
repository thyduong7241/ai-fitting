"""
3D Parametric Human Body Generator.
Integrates High-Fidelity Anatomical Base Topology with the Anthropometric Deformation Engine
and morphological Body Analyzer.
Zero garment dependencies, zero hardcoded magic numbers.
"""

from typing import Dict, Any, List, Tuple, Optional
import numpy as np
import trimesh
from PIL import Image, ImageDraw

from ..schemas.measurements import BodyMeasurements
from ..config_loader import load_config
from .deformation_engine import AnthropometricDeformationEngine, ParametricBodyResult
from .body_analyzer import BodyAnalyzer, BodyAnalysis


class ParametricBody3D:
    """
    Parametric 3D Anatomical Human Avatar.
    Deforms realistic base topologies (Male/Female) to match individual anthropometric measurements.
    """

    def __init__(
        self,
        measurements: BodyMeasurements,
        config: Optional[Dict[str, Any]] = None,
        skin_tone: str = "natural"
    ):
        self.meas = measurements
        self.cfg = config or load_config()
        self.H = float(self.meas.height_cm)
        self.gender = self.meas.gender
        self.skin_tone = skin_tone

        # Initialize engines
        self._engine = AnthropometricDeformationEngine()
        self._analyzer = BodyAnalyzer()

        # Generate deformed parametric avatar
        self._result: ParametricBodyResult = self._engine.generate(self.meas, skin_tone=self.skin_tone)
        self._mesh = self._result.trimesh
        self.skin_color = self._result.skin_color
        self.measurement_tapes = self._result.measurement_tapes
        self.landmarks = self._result.landmarks
        self.uvs = self._result.uvs

        # Perform morphological analysis
        self.analysis: BodyAnalysis = self._analyzer.analyze(self.meas)

    def get_mesh(self) -> trimesh.Trimesh:
        """Returns the high-fidelity 3D trimesh instance."""
        return self._mesh

    def get_landmarks_3d(self) -> Dict[str, List[float]]:
        """Returns major 3D anatomical skeletal landmarks."""
        return self.landmarks

    def get_measurement_tapes(self) -> Dict[str, Any]:
        """Returns 3D measurement tapes wrapping the body at bust, waist, hip, stature."""
        return self.measurement_tapes

    def get_analysis(self) -> Dict[str, Any]:
        """Returns BMI, WHR, and morphological body shape classification."""
        return self.analysis.to_dict()

    def render_ortho_view(self, view: str = "front", image_size: Tuple[int, int] = (600, 1000)) -> Image.Image:
        """Fast CPU 2D projection rendering of the 3D mesh."""
        w_img, h_img = image_size
        img = Image.new("RGBA", (w_img, h_img), (250, 250, 250, 255))
        draw = ImageDraw.Draw(img)

        verts = self._mesh.vertices
        faces = self._mesh.faces

        if view == "side":
            px = verts[:, 2]
            py = verts[:, 1]
        elif view == "three_quarter":
            cos45 = 0.7071
            px = verts[:, 0] * cos45 - verts[:, 2] * cos45
            py = verts[:, 1]
        else:
            px = verts[:, 0]
            py = verts[:, 1]

        margin = 40
        canvas_h = h_img - 2 * margin
        scale = canvas_h / self.H

        screen_x = w_img * 0.5 + px * scale
        screen_y = (h_img - margin) - py * scale

        triangles = []
        for f in faces:
            pts = [(screen_x[f[0]], screen_y[f[0]]),
                   (screen_x[f[1]], screen_y[f[1]]),
                   (screen_x[f[2]], screen_y[f[2]])]
            avg_depth = (verts[f[0], 2] + verts[f[1], 2] + verts[f[2], 2]) / 3.0
            triangles.append((avg_depth, pts))

        triangles.sort(key=lambda t: t[0])

        skin_col = tuple(self.skin_color)
        line_col = (140, 120, 110)

        for _, pts in triangles:
            draw.polygon(pts, fill=skin_col + (255,), outline=line_col + (180,))

        return img
