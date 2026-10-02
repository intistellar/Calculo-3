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


class TestPhase4Parametric(unittest.TestCase):
    def test_paraboloid_area_parametric(self):
        model = IntegralModel.create(
            system="parametric",
            x_expr="u",
            y_expr="v",
            z_expr="u**2 + v**2",
            limits=Limits(-1, 1, -1, 1),
            integral_type="area",
        ).model
        result = IntegralCalculator.calculate(model, "area")
        self.assertTrue(result["success"])
        self.assertGreater(result["approximate"], 0.0)

    def test_paraboloid_scalar_parametric(self):
        model = IntegralModel.create(
            system="parametric",
            x_expr="u",
            y_expr="v",
            z_expr="u**2 + v**2",
            limits=Limits(-1, 1, -1, 1),
            integral_type="scalar",
            scalar_expr="1",
        ).model
        result = IntegralCalculator.calculate(model, "scalar")
        self.assertTrue(result["success"])

    def test_paraboloid_flux_parametric(self):
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

    def test_parametric_mesh_shape(self):
        model = IntegralModel.create(
            system="parametric",
            x_expr="u",
            y_expr="v",
            z_expr="u**2 + v**2",
            limits=Limits(-1, 1, -1, 1),
        ).model
        X, Y, Z = SurfacePlot.build_mesh(model, resolution=10)
        self.assertEqual(X.shape, (10, 10))
        self.assertEqual(Y.shape, (10, 10))
        self.assertEqual(Z.shape, (10, 10))

    def test_render_produces_figure(self):
        model = IntegralModel.create(
            system="parametric",
            x_expr="u",
            y_expr="v",
            z_expr="u**2 + v**2",
            limits=Limits(-1, 1, -1, 1),
        ).model
        fig = MatplotlibSurfaceRenderer.render(model, resolution=10)
        self.assertIsNotNone(fig)
        self.assertGreaterEqual(len(fig.axes), 1)

    def test_normal_vectors_output(self):
        model = IntegralModel.create(
            system="parametric",
            x_expr="u",
            y_expr="v",
            z_expr="u**2 + v**2",
            limits=Limits(-1, 1, -1, 1),
        ).model
        x, y, z, nx, ny, nz = VectorPlot.normal_vectors(model, resolution=6, scale=0.4)
        self.assertIsNotNone(x)
        self.assertEqual(x.shape, (6, 6))


if __name__ == "__main__":
    unittest.main()
