from __future__ import annotations

import unittest

from surfacelab.calculators.procedure_builder import ProcedureBuilder
from surfacelab.models.integral_model import IntegralModel
from surfacelab.models.surface_model import Limits


class TestPhase9Procedure(unittest.TestCase):
    def test_cartesian_procedure_contains_ds(self):
        model = IntegralModel.create(
            system="cartesian",
            func_expr="x**2 + y**2",
            limits=Limits(-1, 1, -1, 1),
            integral_type="area",
        ).model
        result = {"success": True, "exact": None, "approximate": 1.0, "method": "test", "procedure": ["dS = √(1 + 4x² + 4y²) dx dy"]}
        steps = ProcedureBuilder.build_procedure(model, result, "area")
        self.assertTrue(any("dS" in s for s in steps))
        self.assertTrue(any("PROCEDIMIENTO MATEMÁTICO" in s for s in steps))

    def test_parametric_procedure_contains_cross(self):
        model = IntegralModel.create(
            system="parametric",
            x_expr="u",
            y_expr="v",
            z_expr="u**2 + v**2",
            limits=Limits(-1, 1, -1, 1),
            integral_type="area",
        ).model
        result = {"success": True, "exact": None, "approximate": 1.0, "method": "test", "procedure": ["r_u × r_v = ..."]}
        steps = ProcedureBuilder.build_procedure(model, result, "area")
        self.assertTrue(any("r_u" in s for s in steps))
        self.assertTrue(any("PARAMÉTRICA" in s for s in steps))

    def test_polar_procedure_contains_jacobian(self):
        model = IntegralModel.create(
            system="polar",
            func_expr="r",
            limits=Limits(0, 1, 0, 1),
            integral_type="area",
        ).model
        result = {"success": True, "exact": None, "approximate": 1.0, "method": "test", "procedure": ["dS = ..."]}
        steps = ProcedureBuilder.build_procedure(model, result, "area")
        self.assertTrue(any("POLARES" in s for s in steps))


if __name__ == "__main__":
    unittest.main()
