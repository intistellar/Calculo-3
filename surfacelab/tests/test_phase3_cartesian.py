from __future__ import annotations

import math
import unittest

import sympy as sp

from surfacelab.calculators.coordinate_calculators import IntegralCalculator
from surfacelab.models.integral_model import IntegralModel
from surfacelab.models.surface_model import Limits, SurfaceSystem


class TestPhase3Cartesian(unittest.TestCase):
    def test_plane_area(self):
        model = IntegralModel.create(
            system="cartesian",
            func_expr="0",
            limits=Limits(0, 2, 0, 3),
            integral_type="area",
        ).model
        result = IntegralCalculator.calculate(model, "area")
        self.assertTrue(result["success"])
        self.assertAlmostEqual(result["approximate"], 6.0, places=5)
        if result["exact"] is not None:
            self.assertEqual(sp.simplify(result["exact"] - 6), 0)

    def test_paraboloid_area_numerical(self):
        model = IntegralModel.create(
            system="cartesian",
            func_expr="x**2 + y**2",
            limits=Limits(-1, 1, -1, 1),
            integral_type="area",
        ).model
        result = IntegralCalculator.calculate(model, "area")
        self.assertTrue(result["success"])
        self.assertGreater(result["approximate"], 0.0)
        self.assertIn("∂f/∂x", result["procedure"][1])

    def test_paraboloid_scalar_integral(self):
        model = IntegralModel.create(
            system="cartesian",
            func_expr="x**2 + y**2",
            limits=Limits(-1, 1, -1, 1),
            integral_type="scalar",
            scalar_expr="1",
        ).model
        result = IntegralCalculator.calculate(model, "scalar")
        self.assertTrue(result["success"])
        self.assertGreater(result["approximate"], 0.0)

    def test_procedure_generated(self):
        model = IntegralModel.create(
            system="cartesian",
            func_expr="x**2 + y**2",
            limits=Limits(-1, 1, -1, 1),
            integral_type="area",
        ).model
        result = IntegralCalculator.calculate(model, "area")
        self.assertTrue(result["success"])
        procedure = result["procedure"]
        self.assertTrue(any("dS =" in p for p in procedure))
        self.assertTrue(any("A =" in p for p in procedure))


if __name__ == "__main__":
    unittest.main()
