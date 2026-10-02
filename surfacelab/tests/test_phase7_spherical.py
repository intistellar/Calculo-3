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


class TestPhase7Spherical(unittest.TestCase):
    def test_sphere_area_spherical(self):
        model = IntegralModel.create(
            system="spherical",
            func_expr="2",
            limits=Limits(0, 2 * math.pi, 0, math.pi),
            integral_type="area",
        ).model
        result = IntegralCalculator.calculate(model, "area")
        self.assertTrue(result["success"])
        expected = 4 * math.pi * 2 ** 2
        self.assertAlmostEqual(result["approximate"], expected, places=3)

    def test_sphere_scalar_spherical(self):
        model = IntegralModel.create(
            system="spherical",
            func_expr="1",
            limits=Limits(0, 2 * math.pi, 0, math.pi),
            integral_type="scalar",
            scalar_expr="1",
        ).model
        result = IntegralCalculator.calculate(model, "scalar")
        self.assertTrue(result["success"])
        expected = 4 * math.pi * 1 ** 2
        self.assertAlmostEqual(result["approximate"], expected, places=3)

    def test_spherical_mesh_shape(self):
        model = IntegralModel.create(
            system="spherical",
            func_expr="rho",
            limits=Limits(2, 2, 0, 2 * math.pi),
        ).model
        X, Y, Z = SurfacePlot.build_mesh(model, resolution=10)
        self.assertEqual(X.shape, (10, 10))
        self.assertEqual(Y.shape, (10, 10))
        self.assertEqual(Z.shape, (10, 10))

    def test_spherical_normal_vectors_output(self):
        model = IntegralModel.create(
            system="spherical",
            func_expr="rho",
            limits=Limits(2, 2, 0, 2 * math.pi),
        ).model
        x, y, z, nx, ny, nz = VectorPlot.normal_vectors(model, resolution=6, scale=0.4)
        self.assertIsNotNone(x)
        self.assertEqual(x.shape, (6, 6))

    def test_spherical_render_produces_figure(self):
        model = IntegralModel.create(
            system="spherical",
            func_expr="rho",
            limits=Limits(2, 2, 0, 2 * math.pi),
        ).model
        fig = MatplotlibSurfaceRenderer.render(model, resolution=10)
        self.assertIsNotNone(fig)
        self.assertGreaterEqual(len(fig.axes), 1)


if __name__ == "__main__":
    unittest.main()
