from __future__ import annotations

import math
import unittest

import numpy as np
import sympy as sp

from surfacelab.core.differential import Differential
from surfacelab.core.normals import Normals
from surfacelab.core.parametrization import ParametricSurface
from surfacelab.core.surface import CartesianSurface, SurfaceDefinitionError
from surfacelab.core.validation import validate_expression, validate_limits
from surfacelab.models.integral_model import IntegralModel
from surfacelab.models.parameter_model import ParameterModel
from surfacelab.models.surface_model import IntegralType, Limits, SurfaceModel, SurfaceSystem
from surfacelab.utils.parser import (
    available_variables,
    numeric_lambda,
    parse_expression,
)


class TestParser(unittest.TestCase):
    def test_parse_cartesian_expression(self):
        expr = parse_expression("x**2 + y**2", system="cartesian")
        self.assertIsInstance(expr, sp.Expr)
        x, y = sp.Symbol("x"), sp.Symbol("y")
        self.assertEqual(sp.simplify(expr - (x ** 2 + y ** 2)), 0)

    def test_parse_parametric_expression(self):
        expr = parse_expression("u**2 + v**2", system="parametric")
        self.assertIsInstance(expr, sp.Expr)

    def test_unknown_variable_raises(self):
        with self.assertRaises(ValueError):
            parse_expression("x + w", system="cartesian")

    def test_empty_expression_raises(self):
        with self.assertRaises(ValueError):
            parse_expression("", system="cartesian")

    def test_available_variables(self):
        vars_ = available_variables("cartesian")
        self.assertEqual([str(v) for v in vars_], ["x", "y", "z"])

    def test_available_variables_spherical(self):
        vars_ = available_variables("spherical")
        self.assertEqual([str(v) for v in vars_], ["rho", "theta", "phi"])

    def test_numeric_lambda(self):
        expr = parse_expression("x**2 + y", system="cartesian")
        fn = numeric_lambda(expr, [sp.Symbol("x"), sp.Symbol("y")])
        result = fn(2.0, 3.0)
        self.assertAlmostEqual(float(result), 7.0)


class TestModels(unittest.TestCase):
    def test_surface_model_defaults(self):
        model = SurfaceModel()
        self.assertEqual(model.system, SurfaceSystem.CARTESIAN)
        self.assertIsNone(model.func_expr)

    def test_parameter_model_validation(self):
        model = ParameterModel(resolution=1)
        errors = model.validate()
        self.assertTrue(any("resolución" in e.lower() for e in errors))

    def test_parameter_model_valid(self):
        model = ParameterModel()
        self.assertEqual(model.validate(), [])

    def test_integral_model_create_cartesian(self):
        im = IntegralModel.create(
            system="cartesian",
            func_expr="x**2 + y**2",
            integral_type="area",
        )
        self.assertEqual(im.model.system, SurfaceSystem.CARTESIAN)
        self.assertIsNotNone(im.model.func_expr)

    def test_integral_model_create_parametric(self):
        im = IntegralModel.create(
            system="parametric",
            x_expr="u",
            y_expr="v",
            z_expr="u**2 + v**2",
            integral_type="area",
        )
        self.assertEqual(im.model.system, SurfaceSystem.PARAMETRIC)
        self.assertIsNotNone(im.model.x_expr)

    def test_integral_model_flux_components(self):
        im = IntegralModel.create(
            system="cartesian",
            func_expr="x**2 + y**2",
            flux_expr="x, y, z",
            integral_type="flux",
        )
        self.assertIsNotNone(im.model.flux_components)
        self.assertEqual(len(im.model.flux_components), 3)


class TestValidation(unittest.TestCase):
    def test_limits_valid(self):
        errors = validate_limits(Limits(0, 2, 0, 3), "cartesian")
        self.assertEqual(errors, [])

    def test_limits_inverted(self):
        errors = validate_limits(Limits(2, 0, 0, 3), "cartesian")
        self.assertTrue(any("u_min" in e for e in errors))

    def test_limits_non_numeric(self):
        errors = validate_limits(Limits("a", 2, 0, 3), "cartesian")
        self.assertTrue(any("numéricos" in e for e in errors))

    def test_validate_expression_unknown_var(self):
        x = sp.Symbol("x")
        expr = x ** 2 + sp.Symbol("w")
        errors = validate_expression(expr)
        self.assertTrue(any("w" in e for e in errors))


class TestCartesianSurface(unittest.TestCase):
    def test_paraboloid_parametrization(self):
        model = SurfaceModel(
            system=SurfaceSystem.CARTESIAN,
            func_expr=sp.Symbol("x") ** 2 + sp.Symbol("y") ** 2,
            limits=Limits(-1, 1, -1, 1),
        )
        surf = CartesianSurface(model)
        u = np.linspace(-1, 1, 20)
        v = np.linspace(-1, 1, 20)
        x, y, z = surf.parametrization(u, v)
        self.assertEqual(x.shape, (20,))
        self.assertEqual(y.shape, (20,))
        self.assertEqual(z.shape, (20,))

    def test_paraboloid_differential_area(self):
        model = SurfaceModel(
            system=SurfaceSystem.CARTESIAN,
            func_expr=sp.Symbol("x") ** 2 + sp.Symbol("y") ** 2,
            limits=Limits(-1, 1, -1, 1),
        )
        surf = CartesianSurface(model)
        u = np.linspace(-1, 1, 10)
        v = np.linspace(-1, 1, 10)
        dS = surf.differential_area(u, v)
        self.assertEqual(dS.shape, (10,))
        self.assertTrue(np.all(dS > 0))

    def test_plane_normal(self):
        model = SurfaceModel(
            system=SurfaceSystem.CARTESIAN,
            func_expr=sp.Integer(0),
            limits=Limits(0, 2, 0, 3),
        )
        surf = CartesianSurface(model)
        u = np.array([0.0, 1.0])
        v = np.array([0.0, 1.0])
        nx, ny, nz = surf.normal(u, v)
        np.testing.assert_allclose(nz, np.ones_like(nz), atol=1e-6)
        np.testing.assert_allclose(nx, np.zeros_like(nx), atol=1e-6)
        np.testing.assert_allclose(ny, np.zeros_like(ny), atol=1e-6)

    def test_missing_func_raises(self):
        model = SurfaceModel(system=SurfaceSystem.CARTESIAN)
        surf = CartesianSurface(model)
        u = np.array([0.0])
        v = np.array([0.0])
        with self.assertRaises(SurfaceDefinitionError):
            surf.parametrization(u, v)


class TestParametricSurface(unittest.TestCase):
    def test_paraboloid_parametrization(self):
        model = SurfaceModel(
            system=SurfaceSystem.PARAMETRIC,
            x_expr=sp.Symbol("u"),
            y_expr=sp.Symbol("v"),
            z_expr=sp.Symbol("u") ** 2 + sp.Symbol("v") ** 2,
            limits=Limits(-1, 1, -1, 1),
        )
        surf = ParametricSurface(model)
        u = np.linspace(-1, 1, 10)
        v = np.linspace(-1, 1, 10)
        x, y, z = surf.parametrization(u, v)
        np.testing.assert_allclose(z, u[:, None] ** 2 + v[None, :] ** 2, atol=1e-6)

    def test_differential_area_positive(self):
        model = SurfaceModel(
            system=SurfaceSystem.PARAMETRIC,
            x_expr=sp.Symbol("u"),
            y_expr=sp.Symbol("v"),
            z_expr=sp.Symbol("u") ** 2 + sp.Symbol("v") ** 2,
            limits=Limits(-1, 1, -1, 1),
        )
        surf = ParametricSurface(model)
        u = np.linspace(-1, 1, 10)
        v = np.linspace(-1, 1, 10)
        dS = surf.differential_area(u, v)
        self.assertEqual(dS.shape, (10, 10))
        self.assertTrue(np.all(dS > 0))

    def test_normal_unit_length(self):
        model = SurfaceModel(
            system=SurfaceSystem.PARAMETRIC,
            x_expr=sp.Symbol("u"),
            y_expr=sp.Symbol("v"),
            z_expr=sp.Symbol("u") ** 2 + sp.Symbol("v") ** 2,
            limits=Limits(-1, 1, -1, 1),
        )
        surf = ParametricSurface(model)
        u = np.linspace(-1, 1, 10)
        v = np.linspace(-1, 1, 10)
        nx, ny, nz = surf.normal(u, v)
        norm = np.sqrt(nx ** 2 + ny ** 2 + nz ** 2)
        np.testing.assert_allclose(norm, np.ones_like(norm), atol=1e-5)


class TestDifferential(unittest.TestCase):
    def test_cartesian_ds_paraboloid(self):
        model = SurfaceModel(
            system=SurfaceSystem.CARTESIAN,
            func_expr=sp.Symbol("x") ** 2 + sp.Symbol("y") ** 2,
        )
        diff = Differential(model)
        ds = diff.ds_expression()
        x, y = sp.Symbol("x"), sp.Symbol("y")
        expected = sp.sqrt(1 + (2 * x) ** 2 + (2 * y) ** 2)
        self.assertEqual(sp.simplify(ds - expected), 0)

    def test_parametric_ds_paraboloid(self):
        u, v = sp.Symbol("u"), sp.Symbol("v")
        model = SurfaceModel(
            system=SurfaceSystem.PARAMETRIC,
            x_expr=u,
            y_expr=v,
            z_expr=u ** 2 + v ** 2,
        )
        diff = Differential(model)
        ds = diff.ds_expression()
        expected = sp.sqrt(1 + 4 * u ** 2 + 4 * v ** 2)
        self.assertEqual(sp.simplify(ds - expected), 0)


class TestNormals(unittest.TestCase):
    def test_cartesian_normal_paraboloid(self):
        model = SurfaceModel(
            system=SurfaceSystem.CARTESIAN,
            func_expr=sp.Symbol("x") ** 2 + sp.Symbol("y") ** 2,
        )
        normals = Normals(model)
        n = normals.symbolic_normal()
        self.assertEqual(len(n), 3)
        self.assertEqual(n[0], -2 * sp.Symbol("x"))
        self.assertEqual(n[1], -2 * sp.Symbol("y"))
        self.assertEqual(n[2], 1)

    def test_parametric_normal_paraboloid(self):
        u, v = sp.Symbol("u"), sp.Symbol("v")
        model = SurfaceModel(
            system=SurfaceSystem.PARAMETRIC,
            x_expr=u,
            y_expr=v,
            z_expr=u ** 2 + v ** 2,
        )
        normals = Normals(model)
        n = normals.symbolic_normal()
        expected = sp.Matrix([-2 * u, -2 * v, 1])
        self.assertEqual(sp.simplify(n - expected), sp.Matrix([0, 0, 0]))


if __name__ == "__main__":
    unittest.main()
