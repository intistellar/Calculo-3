from __future__ import annotations

from typing import Optional

import sympy as sp

from surfacelab.models.surface_model import IntegralType, Limits, SurfaceModel, SurfaceSystem
from surfacelab.utils.parser import parse_expression


class IntegralModel:
    def __init__(self, model: Optional[SurfaceModel] = None):
        self.model = model or SurfaceModel()

    @staticmethod
    def create(
        system: str,
        func_expr: Optional[str] = None,
        x_expr: Optional[str] = None,
        y_expr: Optional[str] = None,
        z_expr: Optional[str] = None,
        limits: Optional[Limits] = None,
        integral_type: str = "area",
        scalar_expr: Optional[str] = None,
        flux_expr: Optional[str] = None,
        orientation: str = "positive",
        resolution: int = 40,
    ) -> "IntegralModel":
        system_enum = SurfaceSystem(system.lower())
        parsed_func = parse_expression(func_expr, system=system) if func_expr else None
        parsed_x = parse_expression(x_expr, system="parametric") if x_expr else None
        parsed_y = parse_expression(y_expr, system="parametric") if y_expr else None
        parsed_z = parse_expression(z_expr, system="parametric") if z_expr else None
        parsed_scalar = parse_expression(scalar_expr, system=system) if scalar_expr else None
        flux_components = None
        parsed_flux = None
        if flux_expr:
            components = [c.strip() for c in flux_expr.split(",")]
            if len(components) != 3:
                raise ValueError("El campo vectorial debe tener 3 componentes separados por coma.")
            syms = {
                "cartesian": [sp.Symbol("x"), sp.Symbol("y"), sp.Symbol("z")],
                "parametric": [sp.Symbol("u"), sp.Symbol("v")],
                "polar": [sp.Symbol("r"), sp.Symbol("theta")],
                "cylindrical": [sp.Symbol("r"), sp.Symbol("theta"), sp.Symbol("z")],
                "spherical": [sp.Symbol("rho"), sp.Symbol("theta"), sp.Symbol("phi")],
            }
            vars_ = syms.get(system, syms["cartesian"])
            flux_components = tuple(
                parse_expression(c, variables=vars_) for c in components
            )
            parsed_flux = sp.Matrix(flux_components)

        return IntegralModel(
            SurfaceModel(
                system=system_enum,
                func_expr=parsed_func,
                x_expr=parsed_x,
                y_expr=parsed_y,
                z_expr=parsed_z,
                limits=limits or Limits(),
                scalar_expr=parsed_scalar,
                flux_expr=parsed_flux,
                flux_components=flux_components,
                orientation=orientation,
                resolution=resolution,
            )
        )
