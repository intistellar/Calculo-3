"""
Módulo de cálculo vectorial para SURFACELAB.
Implementa operadores diferenciales vectoriales: gradiente, divergencia, rotacional.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

import numpy as np
import sympy as sp


class VectorOperator:
    """
    Clase para calcular operadores vectoriales (gradiente, divergencia, rotacional).
    Soporta coordenadas Cartesianas, Cilíndricas y Esféricas.
    """

    COORD_VARS: Dict[str, List[sp.Symbol]] = {
        "cartesian": [sp.Symbol("x"), sp.Symbol("y"), sp.Symbol("z")],
        "cylindrical": [sp.Symbol("r"), sp.Symbol("theta"), sp.Symbol("z")],
        "spherical": [sp.Symbol("rho"), sp.Symbol("theta"), sp.Symbol("phi")],
    }

    @classmethod
    def _get_vars(cls, system: str) -> Tuple[sp.Symbol, sp.Symbol, sp.Symbol]:
        vars_list = cls.COORD_VARS.get(system.lower(), cls.COORD_VARS["cartesian"])
        return vars_list[0], vars_list[1], vars_list[2]

    @classmethod
    def _parse_field(cls, field_expr: str, system: str = "cartesian") -> Tuple[sp.Expr, sp.Expr, sp.Expr]:
        x_sym, y_sym, z_sym = cls._get_vars(system)
        local_dict = {
            "sin": sp.sin, "cos": sp.cos, "tan": sp.tan, "sqrt": sp.sqrt,
            "exp": sp.exp, "log": sp.log, "pi": sp.pi, "E": sp.E,
            x_sym.name: x_sym, y_sym.name: y_sym, z_sym.name: z_sym,
        }
        components = [c.strip() for c in field_expr.split(",")]
        if len(components) != 3:
            raise ValueError(f"Campo vectorial debe tener 3 componentes: {field_expr}")
        F1 = sp.parse_expr(components[0], local_dict=local_dict, transformations="all")
        F2 = sp.parse_expr(components[1], local_dict=local_dict, transformations="all")
        F3 = sp.parse_expr(components[2], local_dict=local_dict, transformations="all")
        return sp.simplify(F1), sp.simplify(F2), sp.simplify(F3)

    @classmethod
    def gradient(cls, scalar_field: str, system: str = "cartesian") -> Tuple[sp.Expr, sp.Expr, sp.Expr]:
        x_sym, y_sym, z_sym = cls._get_vars(system)
        local_dict = {
            "sin": sp.sin, "cos": sp.cos, "tan": sp.tan, "sqrt": sp.sqrt,
            "exp": sp.exp, "log": sp.log, "pi": sp.pi, "E": sp.E,
            x_sym.name: x_sym, y_sym.name: y_sym, z_sym.name: z_sym,
        }
        f = sp.parse_expr(scalar_field, local_dict=local_dict, transformations="all")
        grad_x = sp.diff(f, x_sym)
        grad_y = sp.diff(f, y_sym)
        grad_z = sp.diff(f, z_sym)
        return sp.simplify(grad_x), sp.simplify(grad_y), sp.simplify(grad_z)

    @classmethod
    def divergence(cls, vector_field: str, system: str = "cartesian") -> sp.Expr:
        F1, F2, F3 = cls._parse_field(vector_field, system)
        x_sym, y_sym, z_sym = cls._get_vars(system)
        if system.lower() == "cartesian":
            div = sp.diff(F1, x_sym) + sp.diff(F2, y_sym) + sp.diff(F3, z_sym)
        elif system.lower() == "cylindrical":
            r, theta, z = x_sym, y_sym, z_sym
            div = sp.diff(r * F1, r) / r + sp.diff(F2, theta) / r + sp.diff(F3, z)
        elif system.lower() == "spherical":
            rho, theta, phi = x_sym, y_sym, z_sym
            sin_phi = sp.sin(phi)
            div = (sp.diff(rho**2 * F1, rho) / rho**2 + 
                   sp.diff(sin_phi * F2, theta) / (rho * sin_phi) + 
                   sp.diff(sin_phi * F3, phi) / (rho * sin_phi))
        else:
            raise ValueError(f"Sistema no soportado: {system}")
        return sp.simplify(div)

    @classmethod
    def curl(cls, vector_field: str, system: str = "cartesian") -> Tuple[sp.Expr, sp.Expr, sp.Expr]:
        F1, F2, F3 = cls._parse_field(vector_field, system)
        x_sym, y_sym, z_sym = cls._get_vars(system)
        if system.lower() == "cartesian":
            curl_x = sp.diff(F3, y_sym) - sp.diff(F2, z_sym)
            curl_y = sp.diff(F1, z_sym) - sp.diff(F3, x_sym)
            curl_z = sp.diff(F2, x_sym) - sp.diff(F1, y_sym)
        elif system.lower() == "cylindrical":
            r, theta, z = x_sym, y_sym, z_sym
            dF3_dtheta = sp.diff(F3, theta)
            dF2_dz = sp.diff(F2, z)
            dF1_dz = sp.diff(F1, z)
            dF3_dr = sp.diff(F3, r)
            dF2_dr = sp.diff(F2, r)
            dF1_dtheta = sp.diff(F1, theta)
            curl_r = (dF3_dtheta - dF2_dz) / r
            curl_theta = dF1_dz - dF3_dr
            curl_z = (dF2_dr - dF1_dtheta + F2 / r)
            cos_t, sin_t = sp.cos(theta), sp.sin(theta)
            curl_x = sp.simplify(curl_r * cos_t - curl_theta * sin_t)
            curl_y = sp.simplify(curl_r * sin_t + curl_theta * cos_t)
            curl_z = sp.simplify(curl_z)
        elif system.lower() == "spherical":
            rho, theta, phi = x_sym, y_sym, z_sym
            sin_phi = sp.sin(phi)
            dF3_dtheta = sp.diff(F3, theta)
            dF2_dphi = sp.diff(F2, phi)
            dF1_dphi = sp.diff(F1, phi)
            dF3_drho = sp.diff(F3, rho)
            dF2_drho = sp.diff(F2, rho)
            dF1_dtheta = sp.diff(F1, theta)
            curl_rho = (dF3_dtheta - dF2_dphi) / (rho * sin_phi)
            curl_theta = (dF1_dphi * sin_phi + F1 * sp.cos(phi) - dF3_drho * sin_phi) / rho
            curl_phi = (dF2_drho * rho + F2 - dF1_dtheta) / (rho * sin_phi)
            cos_t, sin_t = sp.cos(theta), sp.sin(theta)
            cos_p, sin_p = sp.cos(phi), sp.sin(phi)
            curl_x = sp.simplify(curl_rho * sin_p * cos_t - curl_theta * cos_p * cos_t - curl_phi * sin_t / (rho * sin_p))
            curl_y = sp.simplify(curl_rho * sin_p * sin_t - curl_theta * cos_p * sin_t + curl_phi * cos_t / (rho * sin_p))
            curl_z = sp.simplify(curl_rho * cos_p + curl_theta * sin_p)
        else:
            raise ValueError(f"Sistema no soportado: {system}")
        return sp.simplify(curl_x), sp.simplify(curl_y), sp.simplify(curl_z)

    @classmethod
    def laplacian(cls, scalar_field: str, system: str = "cartesian") -> sp.Expr:
        grad_x, grad_y, grad_z = cls.gradient(scalar_field, system)
        return cls.divergence(f"{grad_x}, {grad_y}, {grad_z}", system)

    @classmethod
    def field_to_lambda(cls, field_expr: str, system: str = "cartesian"):
        x_sym, y_sym, z_sym = cls._get_vars(system)
        components = field_expr.split(",")
        lambdas = []
        for comp in components:
            expr = sp.parse_expr(comp.strip(), local_dict={x_sym.name: x_sym, y_sym.name: y_sym, z_sym.name: z_sym}, transformations="all")
            lambdas.append(sp.lambdify((x_sym, y_sym, z_sym), expr, modules="numpy"))
        return lambdas


def compute_flux_through_surface(vector_field: str, surface_expr: str) -> sp.Expr:
    """Calcular flujo de campo vectorial a través de superficie z = f(x,y)."""
    x_sym, y_sym, z_sym = sp.Symbol("x"), sp.Symbol("y"), sp.Symbol("z")
    local_dict = {"sin": sp.sin, "cos": sp.cos, "tan": sp.tan, "sqrt": sp.sqrt,
                  "exp": sp.exp, "log": sp.log, "pi": sp.pi, "E": sp.E,
                  "x": x_sym, "y": y_sym, "z": z_sym}
    f = sp.parse_expr(surface_expr, local_dict=local_dict, transformations="all")
    nx, ny, nz = -sp.diff(f, x_sym), -sp.diff(f, y_sym), 1
    F1, F2, F3 = VectorOperator._parse_field(vector_field, "cartesian")
    flux_density = sp.simplify(F1 * nx + F2 * ny + F3 * nz)
    dS = sp.sqrt(1 + sp.diff(f, x_sym)**2 + sp.diff(f, y_sym)**2)
    return sp.simplify(flux_density * dS)