from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from surfacelab.models.integral_model import IntegralModel
from surfacelab.models.surface_model import IntegralType, Limits, SurfaceSystem


@dataclass
class Example:
    name: str
    description: str
    system: str
    func_expr: Optional[str] = None
    x_expr: Optional[str] = None
    y_expr: Optional[str] = None
    z_expr: Optional[str] = None
    limits: Limits = None
    integral_type: str = "area"
    scalar_expr: Optional[str] = None
    flux_expr: Optional[str] = None
    expected_result: Optional[str] = None

    def __post_init__(self):
        if self.limits is None:
            self.limits = Limits()


class Examples:
    _examples = [
        Example(
            name="Plano",
            description="z = 0 sobre [0,2]×[0,3]",
            system="cartesian",
            func_expr="0",
            limits=Limits(0, 2, 0, 3),
            integral_type="area",
            expected_result="6",
        ),
        Example(
            name="Paraboloide",
            description="z = x² + y² sobre [-1,1]×[-1,1]",
            system="cartesian",
            func_expr="x**2 + y**2",
            limits=Limits(-1, 1, -1, 1),
            integral_type="area",
        ),
        Example(
            name="Cilindro",
            description="r(u,v) = (cos(u), sin(u), v)",
            system="parametric",
            x_expr="cos(u)",
            y_expr="sin(u)",
            z_expr="v",
            limits=Limits(0, 2 * 3.14159, 0, 1),
            integral_type="area",
        ),
        Example(
            name="Esfera",
            description="Esfera de radio 2",
            system="spherical",
            func_expr="2",
            limits=Limits(0, 2 * 3.14159, 0, 3.14159),
            integral_type="area",
            expected_result="16π",
        ),
        Example(
            name="Cono",
            description="z = r en coordenadas polares",
            system="polar",
            func_expr="r",
            limits=Limits(0, 1, 0, 2 * 3.14159),
            integral_type="area",
        ),
        Example(
            name="Superficie ondulada",
            description="z = sin(x) + cos(y)",
            system="cartesian",
            func_expr="sin(x) + cos(y)",
            limits=Limits(0, 3.14159, 0, 3.14159),
            integral_type="scalar",
            scalar_expr="1",
        ),
        Example(
            name="Flujo radial",
            description="F = (x, y, z) sobre esfera",
            system="spherical",
            func_expr="2",
            limits=Limits(0, 2 * 3.14159, 0, 3.14159),
            integral_type="flux",
            flux_expr="0, 0, 1",
        ),
        Example(
            name="Campo simple",
            description="F = (0, 0, 1) sobre paraboloide",
            system="parametric",
            x_expr="u",
            y_expr="v",
            z_expr="u**2 + v**2",
            limits=Limits(-1, 1, -1, 1),
            integral_type="flux",
            flux_expr="0, 0, 1",
        ),
    ]

    @classmethod
    def list_examples(cls) -> list[Example]:
        return list(cls._examples)

    @classmethod
    def get_example(cls, name: str) -> Optional[Example]:
        for ex in cls._examples:
            if ex.name == name:
                return ex
        return None

    @classmethod
    def load_example(cls, name: str) -> Optional[IntegralModel]:
        ex = cls.get_example(name)
        if ex is None:
            return None
        return IntegralModel.create(
            system=ex.system,
            func_expr=ex.func_expr,
            x_expr=ex.x_expr,
            y_expr=ex.y_expr,
            z_expr=ex.z_expr,
            limits=ex.limits,
            integral_type=ex.integral_type,
            scalar_expr=ex.scalar_expr,
            flux_expr=ex.flux_expr,
        )
