import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from body_fit.src.body_model.base_topology import BaseHumanTopology

class TestBaseTopology(unittest.TestCase):
    def test_female_base_topology_generation(self):
        topo = BaseHumanTopology.get_topology("female")
        self.assertGreater(len(topo.vertices), 1000)
        self.assertGreater(len(topo.faces), 1500)
        self.assertIn("bust", topo.zone_indices)
        self.assertIn("waist", topo.zone_indices)
        self.assertIn("hip", topo.zone_indices)
        self.assertIn("shorts", topo.zone_indices)
        self.assertIn("hands", topo.zone_indices)
        self.assertIsNotNone(topo.normals)
        self.assertEqual(len(topo.normals), len(topo.vertices))

    def test_male_base_topology_generation(self):
        topo = BaseHumanTopology.get_topology("male")
        self.assertGreater(len(topo.vertices), 1000)
        self.assertGreater(len(topo.faces), 1500)
        self.assertIn("shoulder", topo.zone_indices)
        self.assertIn("pectorals", topo.zone_indices)
        self.assertIn("waist", topo.zone_indices)
        self.assertIsNotNone(topo.normals)

if __name__ == "__main__":
    unittest.main()
