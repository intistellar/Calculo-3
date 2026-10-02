from __future__ import annotations

from typing import Optional, Tuple

import numpy as np
import sympy as sp

from surfacelab.models.surface_model import SurfaceModel


class Normals:
    def __init__(self, model: SurfaceModel):
        self.model = model

    def symbolic_normal(self):
        system = self.model.system.value
        if system == "cartesian":
            return self._cartesian_normal()
        if system == "parametric":
            return self._parametric_normal()
        raise NotImplementedError(f"Normal no implementada para '{system}' en Fase 2.")

    def _cartesian_normal(self):
        x, y, z = sp.Symbol("x"), sp.Symbol("y"), sp.Symbol("z")
        f = self.model.func_expr
        fx = sp.diff(f, x)
        fy = sp.diff(f, y)
        return sp.Matrix([-fx, -fy, 1])

    def _parametric_normal(self):
        u, v = sp.Symbol("u"), sp.Symbol("v")
        rx = sp.Matrix([self.model.x_expr, self.model.y_expr, self.model.z_expr])
        ru = sp.diff(rx, u)
        rv = sp.diff(rx, v)
        normal = ru.cross(rv)
        if self.model.orientation == "negative":
            normal = -normal
        return sp.simplify(normal)
