from __future__ import annotations

from typing import List, Optional

import sympy as sp

from surfacelab.models.surface_model import SurfaceModel


class ProcedureBuilder:
    @staticmethod
    def build_procedure(model: SurfaceModel, result: dict, integral_type: str = "area") -> List[str]:
        steps: List[str] = []
        system = model.system.value

        steps.append("=" * 60)
        steps.append("PROCEDIMIENTO MATEMÁTICO")
        steps.append("=" * 60)

        if system == "cartesian":
            steps.extend(ProcedureBuilder._cartesian_steps(model))
        elif system == "parametric":
            steps.extend(ProcedureBuilder._parametric_steps(model))
        elif system == "polar":
            steps.extend(ProcedureBuilder._polar_steps(model))
        elif system == "cylindrical":
            steps.extend(ProcedureBuilder._cylindrical_steps(model))
        elif system == "spherical":
            steps.extend(ProcedureBuilder._spherical_steps(model))

        steps.append("-" * 60)
        steps.append("INTEGRAL")
        if integral_type == "area":
            steps.append("A = ∬_S dS")
        elif integral_type == "scalar":
            steps.append("I = ∬_S g(x,y,z) dS")
        elif integral_type in {"flux", "flux_vector"}:
            steps.append("Φ = ∬_S F · n dS")

        if result.get("exact") is not None:
            steps.append(f"Resultado exacto: {result['exact']}")
        if result.get("approximate") is not None:
            steps.append(f"Resultado numérico: {result['approximate']}")
        steps.append(f"Método: {result.get('method', 'N/A')}")
        steps.append("=" * 60)

        return steps

    @staticmethod
    def _cartesian_steps(model: SurfaceModel) -> List[str]:
        steps = ["SUPERFICIE CARTESIANA"]
        f = model.func_expr
        if f is not None:
            steps.append(f"z = f(x,y) = {f}")
            x, y = sp.Symbol("x"), sp.Symbol("y")
            fx = sp.diff(f, x)
            fy = sp.diff(f, y)
            steps.append(f"∂f/∂x = {fx}")
            steps.append(f"∂f/∂y = {fy}")
            ds = sp.sqrt(1 + fx ** 2 + fy ** 2)
            steps.append(f"dS = √(1 + (∂f/∂x)² + (∂f/∂y)²) dx dy")
            steps.append(f"dS = {ds} dx dy")
        return steps

    @staticmethod
    def _parametric_steps(model: SurfaceModel) -> List[str]:
        steps = ["SUPERFICIE PARAMÉTRICA"]
        x_expr, y_expr, z_expr = model.x_expr, model.y_expr, model.z_expr
        if x_expr is not None and y_expr is not None and z_expr is not None:
            steps.append(f"r(u,v) = ({x_expr}, {y_expr}, {z_expr})")
            u, v = sp.Symbol("u"), sp.Symbol("v")
            rx = sp.Matrix([x_expr, y_expr, z_expr])
            ru = sp.diff(rx, u)
            rv = sp.diff(rx, v)
            cross = ru.cross(rv)
            magnitude = sp.sqrt(cross.dot(cross))
            steps.append(f"r_u = ({ru[0]}, {ru[1]}, {ru[2]})")
            steps.append(f"r_v = ({rv[0]}, {rv[1]}, {rv[2]})")
            steps.append(f"r_u × r_v = ({cross[0]}, {cross[1]}, {cross[2]})")
            steps.append(f"|r_u × r_v| = {sp.simplify(magnitude)}")
            steps.append(f"dS = |r_u × r_v| du dv")
        return steps

    @staticmethod
    def _polar_steps(model: SurfaceModel) -> List[str]:
        steps = ["SUPERFICIE EN COORDENADAS POLARES"]
        f = model.func_expr
        if f is not None:
            steps.append(f"z = f(r, θ) = {f}")
            r, th = sp.Symbol("r"), sp.Symbol("theta")
            fr = sp.diff(f, r)
            fth = sp.diff(f, th)
            steps.append(f"∂f/∂r = {fr}")
            steps.append(f"∂f/∂θ = {fth}")
            ds = sp.sqrt(1 + fr ** 2 + (fth / r) ** 2) * r
            steps.append(f"dS = √(1 + (∂f/∂r)² + (∂f/∂θ)²/r²) * r dr dθ")
            steps.append(f"dS = {ds} dr dθ")
        return steps

    @staticmethod
    def _cylindrical_steps(model: SurfaceModel) -> List[str]:
        steps = ["SUPERFICIE CILÍNDRICA"]
        f = model.func_expr
        if f is not None:
            steps.append(f"z = f(r, θ) = {f}")
            r, th = sp.Symbol("r"), sp.Symbol("theta")
            fr = sp.diff(f, r)
            fth = sp.diff(f, th)
            ds = sp.sqrt(1 + fr ** 2 + (fth / r) ** 2) * r
            steps.append(f"dS = √(1 + (∂f/∂r)² + (∂f/∂θ)²/r²) * r dr dθ")
            steps.append(f"dS = {ds} dr dθ")
        return steps

    @staticmethod
    def _spherical_steps(model: SurfaceModel) -> List[str]:
        steps = ["SUPERFICIE ESFÉRICA"]
        rho = model.limits.u_min if model.limits else 1.0
        steps.append(f"Esfera de radio ρ = {rho}")
        steps.append(f"r(θ, φ) = (ρ sin φ cos θ, ρ sin φ sin θ, ρ cos φ)")
        phi = sp.Symbol("phi")
        ds = rho ** 2 * sp.sin(phi)
        steps.append(f"dS = ρ² sin φ dθ dφ = {ds} dθ dφ")
        return steps
