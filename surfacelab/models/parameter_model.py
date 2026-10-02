from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import sympy as sp

from surfacelab.models.surface_model import SurfaceSystem


@dataclass
class ParameterModel:
    system: SurfaceSystem = SurfaceSystem.CARTESIAN
    resolution: int = 40
    subdivisions: int = 200
    show_normals: bool = False
    show_flux_field: bool = False
    normal_scale: float = 0.4
    flux_scale: float = 0.5
    colormap: str = "viridis"
    alpha: float = 0.85

    def validate(self) -> list[str]:
        errors = []
        if self.resolution < 4:
            errors.append("La resolución debe ser al menos 4.")
        if self.subdivisions < 10:
            errors.append("Las subdivisiones deben ser al menos 10.")
        if not (0.0 <= self.alpha <= 1.0):
            errors.append("La transparencia debe estar entre 0 y 1.")
        if self.normal_scale <= 0:
            errors.append("La escala de normales debe ser positiva.")
        if self.flux_scale <= 0:
            errors.append("La escala del campo debe ser positiva.")
        return errors
