import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from fastapi.testclient import TestClient
from body_fit.src.api.server import app


class TestBodyAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health_endpoint(self):
        res = self.client.get("/api/v1/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["service"], "Realistic 3D Body Studio")
        self.assertNotIn("products_available", data)

    def test_generate_body_endpoint(self):
        payload = {
            "gender": "female",
            "height_cm": 168.0,
            "weight_kg": 56.0,
            "bust_cm": 88.0,
            "waist_cm": 64.0,
            "hip_cm": 92.0,
            "skin_tone": "natural"
        }
        res = self.client.post("/api/v1/body/generate", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("body_mesh", data)
        self.assertIn("measurement_tapes", data)
        self.assertIn("analysis", data)
        self.assertEqual(data["analysis"]["body_shape"], "Đồng hồ cát (Hourglass)")
        self.assertNotIn("garment_mesh", data)

    def test_export_obj_endpoint(self):
        payload = {"gender": "male", "height_cm": 175.0, "weight_kg": 70.0}
        res = self.client.post("/api/v1/body/export/obj", json=payload)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(b"v " in res.content)


if __name__ == "__main__":
    unittest.main()
