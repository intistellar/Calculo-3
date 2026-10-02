from __future__ import annotations

from typing import Dict, Iterable, List, Optional

import sympy as sp


COORD_VARS: Dict[str, List[sp.Symbol]] = {
    "cartesian": [sp.Symbol("x"), sp.Symbol("y"), sp.Symbol("z")],
    "polar": [sp.Symbol("r"), sp.Symbol("theta")],
    "cylindrical": [sp.Symbol("r"), sp.Symbol("theta"), sp.Symbol("z")],
    "spherical": [sp.Symbol("rho"), sp.Symbol("theta"), sp.Symbol("phi")],
    "parametric": [sp.Symbol("u"), sp.Symbol("v")],
}


def available_variables(system: str) -> List[sp.Symbol]:
    system = (system or "cartesian").lower()
    if system not in COORD_VARS:
        system = "cartesian"
    return list(COORD_VARS[system])


def parse_expression(
    expr_str: str,
    variables: Optional[Iterable[sp.Symbol]] = None,
    system: str = "cartesian",
) -> sp.Expr:
    if variables is None:
        variables = available_variables(system)

    local_dict: Dict[str, sp.Expr] = {str(v): v for v in variables}
    local_dict.update(
        {
            "sin": sp.sin,
            "cos": sp.cos,
            "tan": sp.tan,
            "sqrt": sp.sqrt,
            "exp": sp.exp,
            "log": sp.log,
            "pi": sp.pi,
            "E": sp.E,
            "abs": sp.Abs,
            "asin": sp.asin,
            "acos": sp.acos,
            "atan": sp.atan,
            "sinh": sp.sinh,
            "cosh": sp.cosh,
            "tanh": sp.tanh,
        }
    )

    expr_str = expr_str.strip()
    if not expr_str:
        raise ValueError("Expresión vacía.")

    try:
        expr = sp.parse_expr(expr_str, local_dict=local_dict, transformations="all")
    except Exception as exc:
        raise ValueError(f"Expresión inválida: {expr_str}") from exc

    free_symbols = set(expr.free_symbols)
    allowed = set(variables)
    unknown = free_symbols - allowed
    if unknown:
        raise ValueError(
            f"Variables desconocidas en la expresión: {sorted(str(s) for s in unknown)}"
        )

    return sp.simplify(expr)


def numeric_lambda(expr: sp.Expr, variables: Iterable[sp.Symbol]):
    variables = list(variables)
    return sp.lambdify(variables, expr, modules="numpy")
