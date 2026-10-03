import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from body_fit.src.schemas.measurements import BodyMeasurements
from body_fit.src.body_model.body_analyzer import BodyAnalyzer

class TestBodyAnalyzer(unittest.TestCase):
    def test_female_hourglass_analysis(self):
        meas = BodyMeasurements(
            gender="female",
            height_cm=165.0,
            weight_kg=58.0,
            bust_cm=90.0,
            waist_cm=65.0,
            hip_cm=94.0
        )
        analyzer = BodyAnalyzer()
        res = analyzer.analyze(meas)
        self.assertAlmostEqual(res.bmi, 21.3, places=1)
        self.assertEqual(res.bmi_category, "Bình thường (Normal)")
        self.assertEqual(res.body_shape, "Đồng hồ cát (Hourglass)")
        self.assertAlmostEqual(res.whr, 0.69, places=2)

    def test_male_athletic_analysis(self):
        meas = BodyMeasurements(
            gender="male",
            height_cm=178.0,
            weight_kg=74.0,
            shoulder_width_cm=46.0,
            bust_cm=102.0,
            waist_cm=78.0,
            hip_cm=96.0
        )
        analyzer = BodyAnalyzer()
        res = analyzer.analyze(meas)
        self.assertEqual(res.body_shape, "Hình thang / Thể thao (Trapezoid / Athletic)")
        self.assertAlmostEqual(res.whr, 0.81, places=2)

if __name__ == "__main__":
    unittest.main()
