from __future__ import annotations

import math
from typing import Optional, Tuple

import numpy as np
import sympy as sp

from surfacelab.models.surface_model import Limits


class ValidationError(Exception):
    pass


def validate_limits(limits: Limits, system: str) -> list[str]:
    errors: list[str] = []
    u_min, u_max, v_min, v_max = limits.as_tuple()
    values = (u_min, u_max, v_min, v_max)
    if not all(isinstance(v, (int, float)) and not math.isnan(v) for v in values):
        errors.append("Los límites deben ser numéricos.")
        return errors
    if u_min >= u_max:
        errors.append("u_min debe ser menor que u_max.")
    if v_min >= v_max:
        errors.append("v_min debe ser menor que v_max.")
    if system in {"polar", "cylindrical", "spherical"}:
        if not (0 <= u_min <= 2 * math.pi) or not (0 <= u_max <= 2 * math.pi):
            errors.append("Los límites angulares deben estar en [0, 2π].")
    return errors


def validate_expression(expr: Optional[sp.Expr], label: str = "expresión") -> list[str]:
    errors: list[str] = []
    if expr is None:
        return errors
    if not isinstance(expr, sp.Expr):
        errors.append(f"{label} no es una expresión simbólica válida.")
        return errors
    for sym in expr.free_symbols:
        if sym.name not in {"x", "y", "z", "r", "theta", "phi", "rho", "u", "v"}:
            errors.append(f"Variable desconocida '{sym.name}' en {label}.")
    for atom in sp.preorder_traversal(expr):
        if atom.is_Pow and atom.exp.is_real and atom.exp < 0 and atom.base != 0:
            pass
    return errors
