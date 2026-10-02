from __future__ import annotations

from typing import Optional

import sympy as sp

from surfacelab.models.surface_model import SurfaceModel


class Differential:
    def __init__(self, model: SurfaceModel):
        self.model = model

    def ds_expression(self):
        system = self.model.system.value
        if system == "cartesian":
            return self._cartesian_ds()
        if system == "parametric":
            return self._parametric_ds()
        raise NotImplementedError(f"dS no implementado para '{system}' en Fase 2.")

    def _cartesian_ds(self):
        x, y = sp.Symbol("x"), sp.Symbol("y")
        f = self.model.func_expr
        if f is None:
            raise ValueError("Falta z = f(x,y).")
        fx = sp.diff(f, x)
        fy = sp.diff(f, y)
        return sp.sqrt(1 + fx ** 2 + fy ** 2)

    def _parametric_ds(self):
        u, v = sp.Symbol("u"), sp.Symbol("v")
        rx = sp.Matrix([self.model.x_expr, self.model.y_expr, self.model.z_expr])
        ru = sp.diff(rx, u)
        rv = sp.diff(rx, v)
        cross = ru.cross(rv)
        magnitude = sp.sqrt(cross.dot(cross))
        return sp.simplify(magnitude)
