import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from body_fit.src.schemas.measurements import BodyMeasurements
from body_fit.src.body_model.deformation_engine import AnthropometricDeformationEngine

class TestDeformationEngine(unittest.TestCase):
    def test_height_and_circumference_morphing(self):
        meas_slim = BodyMeasurements(
            gender="female",
            height_cm=160.0,
            weight_kg=48.0,
            bust_cm=80.0,
            waist_cm=58.0,
            hip_cm=85.0
        )
        meas_curvy = BodyMeasurements(
            gender="female",
            height_cm=175.0,
            weight_kg=68.0,
            bust_cm=100.0,
            waist_cm=75.0,
            hip_cm=105.0
        )

        engine = AnthropometricDeformationEngine()
        res_slim = engine.generate(meas_slim)
        res_curvy = engine.generate(meas_curvy)

        mesh_slim = res_slim.trimesh
        mesh_curvy = res_curvy.trimesh

        # Check height corresponds to input stature
        h_slim = mesh_slim.bounds[1][1] - mesh_slim.bounds[0][1]
        h_curvy = mesh_curvy.bounds[1][1] - mesh_curvy.bounds[0][1]
        self.assertAlmostEqual(h_slim, 160.0, delta=2.5)
        self.assertAlmostEqual(h_curvy, 175.0, delta=2.5)

        # Curvy should have strictly wider bounding box in X and Z
        w_slim = mesh_slim.bounds[1][0] - mesh_slim.bounds[0][0]
        w_curvy = mesh_curvy.bounds[1][0] - mesh_curvy.bounds[0][0]
        self.assertGreater(w_curvy, w_slim)

        # Check measurement tapes are populated
        self.assertIn("bust", res_curvy.measurement_tapes)
        self.assertIn("waist", res_curvy.measurement_tapes)
        self.assertIn("hip", res_curvy.measurement_tapes)
        self.assertGreater(len(res_curvy.measurement_tapes["bust"]["points"]), 10)

    def test_male_athletic_deformation(self):
        meas = BodyMeasurements(
            gender="male",
            height_cm=182.0,
            weight_kg=78.0,
            shoulder_width_cm=48.0,
            bust_cm=104.0,
            waist_cm=80.0,
            hip_cm=98.0
        )
        engine = AnthropometricDeformationEngine()
        res = engine.generate(meas)
        self.assertEqual(len(res.trimesh.vertex_normals), len(res.trimesh.vertices))
        self.assertIn("shoulder", res.landmarks)

    def test_smooth_shoulder_and_no_spikes(self):
        """Verifies that alteration of shoulder width and leg length does not tear edges or create spikes."""
        import numpy as np
        meas = BodyMeasurements(
            gender="male",
            height_cm=180.0,
            weight_kg=74.0,
            bust_cm=86.5,
            waist_cm=80.0,
            hip_cm=96.0,
            shoulder_width_cm=50.0,
            leg_length_cm=96.5
        )
        engine = AnthropometricDeformationEngine()
        res = engine.generate(meas)
        mesh = res.trimesh

        # Height should precisely match target
        h = mesh.bounds[1][1] - mesh.bounds[0][1]
        self.assertAlmostEqual(h, 180.0, delta=1.5)

        # Max edge length should remain strictly bounded (no torn spikes > 15cm)
        edges = mesh.edges_unique
        lens = np.linalg.norm(mesh.vertices[edges[:, 0]] - mesh.vertices[edges[:, 1]], axis=1)
        self.assertLess(lens.max(), 14.5)

    def test_female_natural_bust_curvature(self):
        """Verifies that large bust retains a smooth curvature and does not form a sharp cone."""
        import numpy as np
        meas = BodyMeasurements(
            gender="female",
            height_cm=168.0,
            weight_kg=50.5,
            bust_cm=102.0,
            waist_cm=66.0,
            hip_cm=92.0
        )
        engine = AnthropometricDeformationEngine()
        res = engine.generate(meas)
        mesh = res.trimesh
        v = mesh.vertices

        # Locate bust region vertices
        bust_pts = v[(v[:, 1] > 110.0) & (v[:, 1] < 125.0) & (v[:, 2] > 0)]
        self.assertGreater(len(bust_pts), 10)
        # Apex Z should be rounded, smooth, and physically plausible
        apex_z = bust_pts[:, 2].max()
        self.assertGreater(apex_z, 12.0)
        self.assertLess(apex_z, 16.5)

if __name__ == "__main__":
    unittest.main()
