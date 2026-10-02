from __future__ import annotations

from typing import Optional

import numpy as np
import sympy as sp
from scipy.integrate import dblquad

from surfacelab.core.parametrization import ParametricSurface
from surfacelab.models.surface_model import Limits, SurfaceModel
from surfacelab.utils.parser import numeric_lambda


class FluxIntegralCalculator:
    @staticmethod
    def calculate(model: SurfaceModel) -> dict:
        if model.flux_components is None:
            raise ValueError("Falta el campo vectorial F = (P, Q, R).")
        system = model.system.value
        if system == "cartesian":
            return FluxIntegralCalculator._cartesian(model)
        if system in {"parametric", "polar", "cylindrical", "spherical"}:
            return FluxIntegralCalculator._parametric(model)
        raise NotImplementedError(f"Flujo no implementado para '{system}' en Fase 8.")

    @staticmethod
    def _cartesian(model: SurfaceModel):
        from surfacelab.core.surface import CartesianSurface

        surf = CartesianSurface(model)
        x_sym, y_sym, z_sym = sp.Symbol("x"), sp.Symbol("y"), sp.Symbol("z")
        P, Q, R = model.flux_components
        fx = model.func_expr
        if fx is None:
            raise ValueError("Falta z = f(x,y) para superficie cartesiana.")
        fx_f = sp.diff(fx, x_sym)
        fy_f = sp.diff(fx, y_sym)
        n_x = -fx_f
        n_y = -fy_f
        n_z = sp.Integer(1)
        flux_expr = sp.simplify(P * n_x + Q * n_y + R * n_z)
        ds_expr = sp.sqrt(1 + fx_f ** 2 + fy_f ** 2)
        integrand = sp.simplify(flux_expr * ds_expr)

        procedure = [
            f"F = ({P}, {Q}, {R})",
            f"z = f(x,y) = {fx}",
            f"n = (-∂f/∂x, -∂f/∂y, 1) = ({n_x}, {n_y}, {n_z})",
            f"dS = √(1 + (∂f/∂x)² + (∂f/∂y)²) dx dy",
            f"F · n dS = {integrand} dx dy",
            f"Φ = ∬ F · n dS",
        ]

        fn = numeric_lambda(integrand, [x_sym, y_sym])
        u_min, u_max, v_min, v_max = model.limits.as_tuple()

        try:
            exact = sp.integrate(integrand, (x_sym, u_min, u_max), (y_sym, v_min, v_max))
            exact = sp.simplify(exact)
            approximate = float(exact.evalf())
            method = "SymPy simbólica"
            procedure.append(f"Resultado exacto: {exact}")
        except Exception:
            approximate, err = dblquad(
                lambda x, y: float(fn(x, y)),
                v_min, v_max,
                lambda xv: u_min,
                lambda xv: u_max,
            )
            exact = None
            method = "SciPy numérica (dblquad)"
            procedure.append(f"Resultado numérico: {approximate:.6f}")

        return {
            "success": True,
            "exact": exact,
            "approximate": approximate,
            "method": method,
            "procedure": procedure,
            "ds_expression": integrand,
        }

    @staticmethod
    def _parametric(model: SurfaceModel):
        from surfacelab.core.parametrization import (
            CylindricalSurface,
            ParametricSurface,
            PolarSurface,
            SphericalSurface,
        )
        from surfacelab.core.surface import CartesianSurface

        system = model.system.value
        if system == "cartesian":
            return FluxIntegralCalculator._cartesian(model)
        if system == "polar":
            surf = PolarSurface(model)
            surf._prepare_polar()
        elif system == "cylindrical":
            surf = CylindricalSurface(model)
            surf._prepare_cylindrical()
        elif system == "spherical":
            surf = SphericalSurface(model)
            if model.func_expr is not None:
                surf._prepare_spherical()
            else:
                surf._prepare_sphere(float(model.limits.u_min) if model.limits else 1.0)
        else:
            surf = ParametricSurface(model)

        u_sym, v_sym = sp.Symbol("u"), sp.Symbol("v")
        P, Q, R = model.flux_components
        rx = sp.Matrix([model.x_expr, model.y_expr, model.z_expr])
        ru = sp.diff(rx, u_sym)
        rv = sp.diff(rx, v_sym)
        cross = ru.cross(rv)

        flux_expr = sp.simplify(P * cross[0] + Q * cross[1] + R * cross[2])
        orientation_note = "orientación positiva" if model.orientation == "positive" else "orientación negativa"

        procedure = [
            f"F = ({P}, {Q}, {R})",
            f"r(u,v) = ({model.x_expr}, {model.y_expr}, {model.z_expr})",
            f"r_u = ({ru[0]}, {ru[1]}, {ru[2]})",
            f"r_v = ({rv[0]}, {rv[1]}, {rv[2]})",
            f"r_u × r_v = ({cross[0]}, {cross[1]}, {cross[2]})",
            f"F · (r_u × r_v) = {flux_expr}",
            f"Φ = ∬ F · (r_u × r_v) du dv ({orientation_note})",
        ]

        fn = numeric_lambda(flux_expr, [u_sym, v_sym])
        u_min, u_max, v_min, v_max = model.limits.as_tuple()

        try:
            exact = sp.integrate(flux_expr, (u_sym, u_min, u_max), (v_sym, v_min, v_max))
            exact = sp.simplify(exact)
            approximate = float(exact.evalf())
            method = "SymPy simbólica"
            procedure.append(f"Resultado exacto: {exact}")
        except Exception:
            approximate, err = dblquad(
                lambda u, v: float(fn(u, v)),
                v_min, v_max,
                lambda uv: u_min,
                lambda uv: u_max,
            )
            exact = None
            method = "SciPy numérica (dblquad)"
            procedure.append(f"Resultado numérico: {approximate:.6f}")

        return {
            "success": True,
            "exact": exact,
            "approximate": approximate,
            "method": method,
            "procedure": procedure,
            "ds_expression": cross,
        }
