from __future__ import annotations

from typing import Optional

import numpy as np
import sympy as sp
from scipy.integrate import dblquad

from surfacelab.core.parametrization import ParametricSurface, PolarSurface
from surfacelab.core.surface import CartesianSurface
from surfacelab.models.surface_model import Limits, SurfaceModel
from surfacelab.utils.parser import numeric_lambda


class SurfaceAreaCalculator:
    @staticmethod
    def calculate(model: SurfaceModel) -> dict:
        system = model.system.value
        if system == "cartesian":
            return SurfaceAreaCalculator._cartesian(model)
        if system == "parametric":
            return SurfaceAreaCalculator._parametric(model)
        if system == "polar":
            return SurfaceAreaCalculator._polar(model)
        if system == "cylindrical":
            return SurfaceAreaCalculator._cylindrical(model)
        if system == "spherical":
            return SurfaceAreaCalculator._spherical(model)
        raise NotImplementedError(f"Área no implementada para '{system}' en Fase 7.")

    @staticmethod
    def _cartesian(model: SurfaceModel):
        surf = CartesianSurface(model)
        x_sym, y_sym = sp.Symbol("x"), sp.Symbol("y")
        f = model.func_expr
        fx = sp.diff(f, x_sym) if f is not None else None
        fy = sp.diff(f, y_sym) if f is not None else None
        if fx is None or fy is None:
            raise ValueError("No se pudo derivar z = f(x,y).")

        ds_expr = sp.sqrt(1 + fx ** 2 + fy ** 2)
        ds_simplified = sp.simplify(ds_expr)

        procedure = [
            f"z = {f}",
            f"∂f/∂x = {fx}",
            f"∂f/∂y = {fy}",
            f"dS = √(1 + (∂f/∂x)² + (∂f/∂y)²) dx dy = {ds_simplified} dx dy",
            f"A = ∫∫ dS = ∫∫ {ds_simplified} dx dy",
        ]

        fn = numeric_lambda(ds_simplified, [x_sym, y_sym])
        u_min, u_max, v_min, v_max = model.limits.as_tuple()

        try:
            exact = sp.integrate(ds_simplified, (x_sym, u_min, u_max), (y_sym, v_min, v_max))
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
            "ds_expression": ds_simplified,
        }

    @staticmethod
    def _parametric(model: SurfaceModel):
        surf = ParametricSurface(model)
        u_sym, v_sym = sp.Symbol("u"), sp.Symbol("v")
        rx = sp.Matrix([model.x_expr, model.y_expr, model.z_expr])
        ru = sp.diff(rx, u_sym)
        rv = sp.diff(rx, v_sym)
        cross = ru.cross(rv)
        magnitude = sp.sqrt(cross.dot(cross))
        magnitude = sp.simplify(magnitude)

        procedure = [
            f"r(u,v) = ({model.x_expr}, {model.y_expr}, {model.z_expr})",
            f"r_u = ({ru[0]}, {ru[1]}, {ru[2]})",
            f"r_v = ({rv[0]}, {rv[1]}, {rv[2]})",
            f"r_u × r_v = ({cross[0]}, {cross[1]}, {cross[2]})",
            f"|r_u × r_v| = {magnitude}",
            f"A = ∬ |r_u × r_v| du dv = ∫∫ {magnitude} du dv",
        ]

        fn = numeric_lambda(magnitude, [u_sym, v_sym])
        u_min, u_max, v_min, v_max = model.limits.as_tuple()

        try:
            exact = sp.integrate(magnitude, (u_sym, u_min, u_max), (v_sym, v_min, v_max))
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

    @staticmethod
    def _spherical(model: SurfaceModel):
        from surfacelab.core.parametrization import SphericalSurface

        surf = SphericalSurface(model)
        phi_sym, th_sym = sp.Symbol("phi"), sp.Symbol("theta")
        rho_expr = model.func_expr or sp.Integer(1)
        try:
            rho = float(rho_expr.evalf())
        except Exception:
            rho = 1.0
        ds_expr = rho ** 2 * sp.sin(phi_sym)
        ds_simplified = sp.simplify(ds_expr)

        theta_min, theta_max, phi_min, phi_max = model.limits.as_tuple()
        procedure = [
            f"Esfera de radio ρ = {rho}",
            f"r(θ, φ) = (ρ sin φ cos θ, ρ sin φ sin θ, ρ cos φ)",
            f"dS = ρ² sin φ dθ dφ = {ds_simplified} dθ dφ",
            f"A = ∫∫ dS = ∫_{theta_min}^{theta_max} ∫_{phi_min}^{phi_max} {ds_simplified} dφ dθ",
        ]

        fn = numeric_lambda(ds_simplified, [phi_sym, th_sym])

        try:
            exact = sp.integrate(ds_simplified, (phi_sym, phi_min, phi_max), (th_sym, theta_min, theta_max))
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
            "ds_expression": ds_simplified,
        }

    @staticmethod
    def _cylindrical(model: SurfaceModel):
        from surfacelab.core.parametrization import CylindricalSurface

        surf = CylindricalSurface(model)
        r_sym, th_sym = sp.Symbol("r"), sp.Symbol("theta")
        f = model.func_expr
        if f is None:
            raise ValueError("Falta z = f(r, theta) para superficie cilíndrica.")

        fr = sp.diff(f, r_sym)
        fth = sp.diff(f, th_sym)
        ds_expr = sp.sqrt(1 + fr ** 2 + (fth / r_sym) ** 2) * r_sym
        ds_simplified = sp.simplify(ds_expr)

        u_min, u_max, v_min, v_max = model.limits.as_tuple()
        procedure = [
            f"z = f(r, θ) = {f}",
            f"∂f/∂r = {fr}",
            f"∂f/∂θ = {fth}",
            f"dS = √(1 + (∂f/∂r)² + (∂f/∂θ)²/r²) * r dr dθ = {ds_simplified} dr dθ",
            f"A = ∫∫ dS = ∫_{v_min}^{v_max} ∫_{u_min}^{u_max} {ds_simplified} dr dθ",
        ]

        fn = numeric_lambda(ds_simplified, [r_sym, th_sym])

        try:
            exact = sp.integrate(ds_simplified, (r_sym, u_min, u_max), (th_sym, v_min, v_max))
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
            "ds_expression": ds_simplified,
        }

    @staticmethod
    def _polar(model: SurfaceModel):
        surf = PolarSurface(model)
        r_sym, th_sym = sp.Symbol("r"), sp.Symbol("theta")
        f = model.func_expr
        fr = sp.diff(f, r_sym) if f is not None else None
        fth = sp.diff(f, th_sym) if f is not None else None
        if fr is None or fth is None:
            raise ValueError("No se pudo derivar z = f(r, theta).")

        ds_expr = sp.sqrt(1 + fr ** 2 + (fth / r_sym) ** 2) * r_sym
        ds_simplified = sp.simplify(ds_expr)

        u_min, u_max, v_min, v_max = model.limits.as_tuple()
        procedure = [
            f"z = f(r, θ) = {f}",
            f"∂f/∂r = {fr}",
            f"∂f/∂θ = {fth}",
            f"dS = √(1 + (∂f/∂r)² + (∂f/∂θ)²/r²) * r dr dθ = {ds_simplified} dr dθ",
            f"A = ∫∫ dS = ∫_{v_min}^{v_max} ∫_{u_min}^{u_max} {ds_simplified} dr dθ",
        ]

        fn = numeric_lambda(ds_simplified, [r_sym, th_sym])

        try:
            exact = sp.integrate(ds_simplified, (r_sym, u_min, u_max), (th_sym, v_min, v_max))
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
            "ds_expression": ds_simplified,
        }
