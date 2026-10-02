from __future__ import annotations

import unittest

from surfacelab.models.examples import Examples
from surfacelab.models.integral_model import IntegralModel


class TestPhase10Examples(unittest.TestCase):
    def test_list_examples(self):
        examples = Examples.list_examples()
        self.assertGreater(len(examples), 0)
        names = [e.name for e in examples]
        self.assertIn("Plano", names)
        self.assertIn("Esfera", names)

    def test_load_plane_example(self):
        model = Examples.load_example("Plano")
        self.assertIsNotNone(model)
        self.assertEqual(model.model.system.value, "cartesian")

    def test_load_sphere_example(self):
        model = Examples.load_example("Esfera")
        self.assertIsNotNone(model)
        self.assertEqual(model.model.system.value, "spherical")

    def test_load_nonexistent_example(self):
        model = Examples.load_example("NoExiste")
        self.assertIsNone(model)


if __name__ == "__main__":
    unittest.main()
