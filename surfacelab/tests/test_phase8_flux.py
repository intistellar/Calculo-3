from __future__ import annotations

import math
import unittest

import numpy as np
import sympy as sp

from surfacelab.calculators.coordinate_calculators import IntegralCalculator
from surfacelab.models.integral_model import IntegralModel
from surfacelab.models.surface_model import Limits, SurfaceSystem
from surfacelab.visualization.surface_plot import SurfacePlot, VectorPlot
from surfacelab.visualization.vector_plot import MatplotlibSurfaceRenderer


class TestPhase8Flux(unittest.TestCase):
    def test_flux_plane(self):
        model = IntegralModel.create(
            system="cartesian",
            func_expr="0",
            limits=Limits(0, 2, 0, 3),
            integral_type="flux",
            flux_expr="0, 0, 1",
        ).model
        result = IntegralCalculator.calculate(model, "flux")
        self.assertTrue(result["success"])
        self.assertGreater(result["approximate"], 0.0)

    def test_flux_paraboloid_parametric(self):
        model = IntegralModel.create(
            system="parametric",
            x_expr="u",
            y_expr="v",
            z_expr="u**2 + v**2",
            limits=Limits(-1, 1, -1, 1),
            integral_type="flux",
            flux_expr="0, 0, 1",
        ).model
        result = IntegralCalculator.calculate(model, "flux")
        self.assertTrue(result["success"])

    def test_flux_polar(self):
        model = IntegralModel.create(
            system="polar",
            func_expr="r",
            limits=Limits(0, 1, 0, 2 * math.pi),
            integral_type="flux",
            flux_expr="0, 0, 1",
        ).model
        result = IntegralCalculator.calculate(model, "flux")
        self.assertTrue(result["success"])

    def test_flux_cylindrical(self):
        model = IntegralModel.create(
            system="cylindrical",
            func_expr="r",
            limits=Limits(0, 1, 0, 2 * math.pi),
            integral_type="flux",
            flux_expr="0, 0, 1",
        ).model
        result = IntegralCalculator.calculate(model, "flux")
        self.assertTrue(result["success"])

    def test_flux_sphere(self):
        model = IntegralModel.create(
            system="spherical",
            func_expr="2",
            limits=Limits(0, 2 * math.pi, 0, math.pi),
            integral_type="flux",
            flux_expr="0, 0, 1",
        ).model
        result = IntegralCalculator.calculate(model, "flux")
        self.assertTrue(result["success"])


if __name__ == "__main__":
    unittest.main()
