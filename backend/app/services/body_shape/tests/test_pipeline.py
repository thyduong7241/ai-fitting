"""Unit tests for the Body Fit clean interface, validation, and determinism."""

import unittest
import sys
import os
from PIL import Image

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from body_fit import generate_body, BodyMeasurements, calculate_parameters


class TestBodyFit(unittest.TestCase):
    def test_schema_defaults(self):
        """Test missing optional measurements are automatically filled with proportions."""
        meas = BodyMeasurements(gender="female", height_cm=160.0)
        self.assertIsNotNone(meas.waist_cm)
        self.assertIsNotNone(meas.hip_cm)
        self.assertIsNotNone(meas.bust_cm)
        self.assertIsNotNone(meas.shoulder_width_cm)

    def test_invalid_range_raises_value_error(self):
        """Test out-of-range inputs raise clear ValueError."""
        with self.assertRaises(ValueError):
            generate_body(height_cm=50.0)  # Too short

        with self.assertRaises(ValueError):
            generate_body(waist_cm=250.0)  # Too large

        with self.assertRaises(ValueError):
            generate_body(gender="unknown")  # Invalid gender

    def test_parameter_scaling(self):
        """Test waist alteration strictly widens waist without modifying shoulder width."""
        meas_a = BodyMeasurements(gender="female", height_cm=165.0, waist_cm=65.0)
        meas_b = BodyMeasurements(gender="female", height_cm=165.0, waist_cm=85.0)

        params_a = calculate_parameters(meas_a)
        params_b = calculate_parameters(meas_b)

        # Waist B must be wider than Waist A
        self.assertGreater(params_b.w_waist, params_a.w_waist)
        # Shoulders must remain identical
        self.assertAlmostEqual(params_a.w_shoulder, params_b.w_shoulder, places=5)

    def test_deterministic_output(self):
        """Test identical seeds and inputs produce bit-identical pixel outputs."""
        img1 = generate_body(height_cm=165, waist_cm=70, seed=42, width=200, height=300)
        img2 = generate_body(height_cm=165, waist_cm=70, seed=42, width=200, height=300)
        self.assertEqual(list(img1.getdata()), list(img2.getdata()))

    def test_save_to_path(self):
        """Test output_path writes file directly."""
        test_out = "outputs/demo/test_saved.png"
        img = generate_body(height_cm=165, output_path=test_out, width=200, height=300)
        self.assertTrue(os.path.exists(test_out))
        self.assertEqual(img.size, (200, 300))


if __name__ == "__main__":
    unittest.main()
