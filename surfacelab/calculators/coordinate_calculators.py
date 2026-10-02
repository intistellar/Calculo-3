from __future__ import annotations

from typing import Optional

import sympy as sp

from surfacelab.models.surface_model import SurfaceModel, SurfaceSystem
from surfacelab.calculators.surface_area import SurfaceAreaCalculator
from surfacelab.calculators.scalar_surface_integral import ScalarSurfaceIntegralCalculator
from surfacelab.calculators.flux_integral import FluxIntegralCalculator


class IntegralCalculator:
    @staticmethod
    def calculate(model: SurfaceModel, integral_type: str = "area") -> dict:
        integral_type = (integral_type or model.scalar_expr and "scalar" or model.flux_components and "flux" or "area").lower()
        if integral_type == "area":
            return SurfaceAreaCalculator.calculate(model)
        if integral_type == "scalar":
            return ScalarSurfaceIntegralCalculator.calculate(model)
        if integral_type in {"flux", "flux_vector"}:
            return FluxIntegralCalculator.calculate(model)
        raise ValueError(f"Tipo de integral no soportado: {integral_type}")
