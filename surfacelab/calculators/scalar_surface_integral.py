from __future__ import annotations

from typing import Optional

import numpy as np
import sympy as sp
from scipy.integrate import dblquad

from surfacelab.core.surface import CartesianSurface
from surfacelab.core.parametrization import ParametricSurface
from surfacelab.models.surface_model import Limits, SurfaceModel
from surfacelab.utils.parser import numeric_lambda


class ScalarSurfaceIntegralCalculator:
    @staticmethod
    def calculate(model: SurfaceModel) -> dict:
        if model.scalar_expr is None:
            raise ValueError("Falta la expresión escalar g(x,y,z).")

        system = model.system.value
        if system == "cartesian":
            return ScalarSurfaceIntegralCalculator._cartesian(model)
        if system == "parametric":
            return ScalarSurfaceIntegralCalculator._parametric(model)
        if system == "polar":
            return ScalarSurfaceIntegralCalculator._polar(model)
        if system == "cylindrical":
            return ScalarSurfaceIntegralCalculator._cylindrical(model)
        if system == "spherical":
            return ScalarSurfaceIntegralCalculator._spherical(model)
        raise NotImplementedError(f"Integral escalar no implementada para '{system}' en Fase 7.")

    @staticmethod
    def _cylindrical(model: SurfaceModel):
        from surfacelab.core.parametrization import CylindricalSurface

        surf = CylindricalSurface(model)
        r_sym, th_sym = sp.Symbol("r"), sp.Symbol("theta")
        g = model.scalar_expr
        f = model.func_expr
        fr = sp.diff(f, r_sym)
        fth = sp.diff(f, th_sym)
        ds_expr = sp.sqrt(1 + fr ** 2 + (fth / r_sym) ** 2) * r_sym
        g_sub = g.subs({sp.Symbol("x"): r_sym * sp.cos(th_sym), sp.Symbol("y"): r_sym * sp.sin(th_sym), sp.Symbol("z"): f})
        integrand = sp.simplify(g_sub * ds_expr)

        procedure = [
            f"g(x,y,z) = {g}",
            f"z = f(r, θ) = {f}",
            f"dS = {ds_expr} dr dθ",
            f"∬ g dS = ∫∫ {integrand} dr dθ",
        ]

        fn = numeric_lambda(integrand, [r_sym, th_sym])
        u_min, u_max, v_min, v_max = model.limits.as_tuple()

        try:
            exact = sp.integrate(integrand, (r_sym, u_min, u_max), (th_sym, v_min, v_max))
            exact = sp.simplify(exact)
            approximate = float(exact.evalf())
            method = "SymPy simbólica"
            procedure.append(f"Resultado exacto: {exact}")
        except Exception:
            approximate, err = dblquad(
                lambda r, th: float(fn(r, th)),
                v_min, v_max,
                lambda rv: u_min,
                lambda rv: u_max,
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
            "ds_expression": ds_expr,
        }

    @staticmethod
    def _polar(model: SurfaceModel):
        from surfacelab.core.parametrization import PolarSurface

        surf = PolarSurface(model)
        r_sym, th_sym = sp.Symbol("r"), sp.Symbol("theta")
        g = model.scalar_expr
        f = model.func_expr
        fr = sp.diff(f, r_sym)
        fth = sp.diff(f, th_sym)
        ds_expr = sp.sqrt(1 + fr ** 2 + (fth / r_sym) ** 2) * r_sym
        g_sub = g.subs({sp.Symbol("x"): r_sym * sp.cos(th_sym), sp.Symbol("y"): r_sym * sp.sin(th_sym), sp.Symbol("z"): f})
        integrand = sp.simplify(g_sub * ds_expr)

        procedure = [
            f"g(x,y,z) = {g}",
            f"z = f(r, θ) = {f}",
            f"dS = {ds_expr} dr dθ",
            f"∬ g dS = ∫∫ {integrand} dr dθ",
        ]

        fn = numeric_lambda(integrand, [r_sym, th_sym])
        u_min, u_max, v_min, v_max = model.limits.as_tuple()

        try:
            exact = sp.integrate(integrand, (r_sym, u_min, u_max), (th_sym, v_min, v_max))
            exact = sp.simplify(exact)
            approximate = float(exact.evalf())
            method = "SymPy simbólica"
            procedure.append(f"Resultado exacto: {exact}")
        except Exception:
            approximate, err = dblquad(
                lambda r, th: float(fn(r, th)),
                v_min, v_max,
                lambda rv: u_min,
                lambda rv: u_max,
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
             "ds_expression": ds_expr,
         }

    @staticmethod
    def _spherical(model: SurfaceModel):
        from surfacelab.core.parametrization import SphericalSurface

        surf = SphericalSurface(model)
        phi_sym, th_sym = sp.Symbol("phi"), sp.Symbol("theta")
        g = model.scalar_expr
        rho_expr = model.func_expr or sp.Integer(1)
        try:
            rho = float(rho_expr.evalf())
        except Exception:
            rho = 1.0
        ds_expr = rho ** 2 * sp.sin(phi_sym)
        g_sub = g.subs({
            sp.Symbol("x"): rho * sp.sin(phi_sym) * sp.cos(th_sym),
            sp.Symbol("y"): rho * sp.sin(phi_sym) * sp.sin(th_sym),
            sp.Symbol("z"): rho * sp.cos(phi_sym),
        })
        integrand = sp.simplify(g_sub * ds_expr)

        procedure = [
            f"g(x,y,z) = {g}",
            f"Esfera de radio ρ = {rho}",
            f"dS = ρ² sin φ dθ dφ = {ds_expr} dθ dφ",
            f"∬ g dS = ∫∫ {integrand} dφ dθ",
        ]

        fn = numeric_lambda(integrand, [phi_sym, th_sym])
        theta_min, theta_max, phi_min, phi_max = model.limits.as_tuple()

        try:
            exact = sp.integrate(integrand, (phi_sym, phi_min, phi_max), (th_sym, theta_min, theta_max))
            exact = sp.simplify(exact)
            approximate = float(exact.evalf())
            method = "SymPy simbólica"
            procedure.append(f"Resultado exacto: {exact}")
        except Exception:
            approximate, err = dblquad(
                lambda phi, th: float(fn(phi, th)),
                theta_min, theta_max,
                lambda tv: phi_min,
                lambda tv: phi_max,
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
            "ds_expression": ds_expr,
        }

    @staticmethod
    def _cartesian(model: SurfaceModel):
        surf = CartesianSurface(model)
        x_sym, y_sym = sp.Symbol("x"), sp.Symbol("y")
        g = model.scalar_expr
        f = model.func_expr
        fx = sp.diff(f, x_sym) if f is not None else None
        fy = sp.diff(f, y_sym) if f is not None else None
        if fx is None or fy is None:
            raise ValueError("No se pudo derivar z = f(x,y).")

        ds_expr = sp.sqrt(1 + fx ** 2 + fy ** 2)
        integrand = sp.simplify(g * ds_expr)

        procedure = [
            f"g(x,y,z) = {g}",
            f"z = {f}",
            f"dS = √(1 + (∂f/∂x)² + (∂f/∂y)²) dx dy = {ds_expr} dx dy",
            f"∬ g dS = ∫∫ {integrand} dx dy",
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
            "ds_expression": ds_expr,
        }

    @staticmethod
    def _parametric(model: SurfaceModel):
        surf = ParametricSurface(model)
        u_sym, v_sym = sp.Symbol("u"), sp.Symbol("v")
        g = model.scalar_expr
        rx = sp.Matrix([model.x_expr, model.y_expr, model.z_expr])
        ru = sp.diff(rx, u_sym)
        rv = sp.diff(rx, v_sym)
        cross = ru.cross(rv)
        magnitude = sp.sqrt(cross.dot(cross))
        magnitude = sp.simplify(magnitude)

        g_sub = g.subs({sp.Symbol("x"): model.x_expr, sp.Symbol("y"): model.y_expr, sp.Symbol("z"): model.z_expr})
        integrand = sp.simplify(g_sub * magnitude)

        procedure = [
            f"g(x,y,z) = {g}",
            f"r(u,v) = ({model.x_expr}, {model.y_expr}, {model.z_expr})",
            f"|r_u × r_v| = {magnitude}",
            f"g(r(u,v)) = {g_sub}",
            f"∬ g dS = ∫∫ {integrand} du dv",
        ]

        fn = numeric_lambda(integrand, [u_sym, v_sym])
        u_min, u_max, v_min, v_max = model.limits.as_tuple()

        try:
            exact = sp.integrate(integrand, (u_sym, u_min, u_max), (v_sym, v_min, v_max))
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
            "ds_expression": magnitude,
        }
