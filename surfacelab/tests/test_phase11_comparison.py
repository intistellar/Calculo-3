from __future__ import annotations

import unittest

from surfacelab.models.comparison import SurfaceComparison
from surfacelab.models.integral_model import IntegralModel
from surfacelab.models.surface_model import Limits


class TestPhase11Comparison(unittest.TestCase):
    def test_compare_equal_planes(self):
        model_a = IntegralModel.create(
            system="cartesian",
            func_expr="0",
            limits=Limits(0, 2, 0, 3),
            integral_type="area",
        ).model
        model_b = IntegralModel.create(
            system="cartesian",
            func_expr="0",
            limits=Limits(0, 2, 0, 3),
            integral_type="area",
        ).model
        result = SurfaceComparison.compare(model_a, model_b, "area")
        self.assertIsNotNone(result)
        self.assertAlmostEqual(result.difference, 0.0, places=5)
        self.assertAlmostEqual(result.ratio, 1.0, places=5)

    def test_compare_different_surfaces(self):
        model_a = IntegralModel.create(
            system="cartesian",
            func_expr="0",
            limits=Limits(0, 2, 0, 3),
            integral_type="area",
        ).model
        model_b = IntegralModel.create(
            system="cartesian",
            func_expr="0",
            limits=Limits(0, 1, 0, 1),
            integral_type="area",
        ).model
        result = SurfaceComparison.compare(model_a, model_b, "area")
        self.assertIsNotNone(result)
        self.assertGreater(result.difference, 0.0)


if __name__ == "__main__":
    unittest.main()
