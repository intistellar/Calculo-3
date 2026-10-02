from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from surfacelab.calculators.coordinate_calculators import IntegralCalculator
from surfacelab.models.surface_model import SurfaceModel


@dataclass
class ComparisonResult:
    name_a: str
    name_b: str
    result_a: dict
    result_b: dict
    difference: Optional[float] = None
    ratio: Optional[float] = None


class SurfaceComparison:
    @staticmethod
    def compare(model_a: SurfaceModel, model_b: SurfaceModel, integral_type: str = "area") -> ComparisonResult:
        result_a = IntegralCalculator.calculate(model_a, integral_type)
        result_b = IntegralCalculator.calculate(model_b, integral_type)

        approx_a = result_a.get("approximate")
        approx_b = result_b.get("approximate")

        difference = None
        ratio = None
        if approx_a is not None and approx_b is not None:
            difference = abs(approx_a - approx_b)
            if approx_b != 0:
                ratio = approx_a / approx_b

        return ComparisonResult(
            name_a=model_a.func_expr or model_a.x_expr or "Superficie A",
            name_b=model_b.func_expr or model_b.x_expr or "Superficie B",
            result_a=result_a,
            result_b=result_b,
            difference=difference,
            ratio=ratio,
        )
