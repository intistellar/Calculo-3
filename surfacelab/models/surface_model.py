from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Tuple

import sympy as sp


class IntegralType(str, Enum):
    AREA = "area"
    SCALAR = "scalar"
    FLUX = "flux"


class SurfaceSystem(str, Enum):
    CARTESIAN = "cartesian"
    PARAMETRIC = "parametric"
    POLAR = "polar"
    CYLINDRICAL = "cylindrical"
    SPHERICAL = "spherical"


@dataclass
class Limits:
    u_min: float = 0.0
    u_max: float = 1.0
    v_min: float = 0.0
    v_max: float = 1.0

    def as_tuple(self) -> Tuple[float, float, float, float]:
        return (self.u_min, self.u_max, self.v_min, self.v_max)


@dataclass
class SurfaceModel:
    system: SurfaceSystem = SurfaceSystem.CARTESIAN
    func_expr: Optional[sp.Expr] = None
    x_expr: Optional[sp.Expr] = None
    y_expr: Optional[sp.Expr] = None
    z_expr: Optional[sp.Expr] = None
    limits: Limits = field(default_factory=Limits)
    scalar_expr: Optional[sp.Expr] = None
    flux_expr: Optional[sp.Expr] = None
    flux_components: Optional[Tuple[sp.Expr, sp.Expr, sp.Expr]] = None
    orientation: str = "positive"
    resolution: int = 40


@dataclass
class IntegralResult:
    exact: Optional[sp.Expr] = None
    approximate: Optional[float] = None
    method: str = ""
    procedure: List[str] = field(default_factory=list)
    success: bool = False
    error_message: str = ""
