from __future__ import annotations

import warnings
from typing import Optional, Tuple

import numpy as np
import sympy as sp

from surfacelab.models.surface_model import Limits, SurfaceModel
from surfacelab.utils.parser import available_variables


class SurfaceDefinitionError(Exception):
    pass


class Surface:
    def __init__(self, model: SurfaceModel):
        self.model = model
        self._lambda_cache: dict = {}

    def variables(self):
        return available_variables(self.model.system.value)

    def parametrization(self, u: np.ndarray, v: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        raise NotImplementedError()

    def differential_area(self, u: np.ndarray, v: np.ndarray) -> np.ndarray:
        raise NotImplementedError()

    def normal(self, u: np.ndarray, v: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        raise NotImplementedError()


class CartesianSurface(Surface):
    def parametrization(self, u: np.ndarray, v: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        x, y = u, v
        f = self.model.func_expr
        if f is None:
            raise SurfaceDefinitionError("Falta z = f(x,y).")
        x_sym, y_sym = sp.Symbol("x"), sp.Symbol("y")
        z_fn = sp.lambdify((x_sym, y_sym), f, modules="numpy")
        z = z_fn(x, y)
        return np.asarray(x, dtype=float), np.asarray(y, dtype=float), np.asarray(z, dtype=float)

    def differential_area(self, u: np.ndarray, v: np.ndarray) -> np.ndarray:
        x_sym, y_sym = sp.Symbol("x"), sp.Symbol("y")
        f = self.model.func_expr
        fx = sp.diff(f, x_sym) if f is not None else None
        fy = sp.diff(f, y_sym) if f is not None else None
        if fx is None or fy is None:
            raise SurfaceDefinitionError("No se pudo derivar z = f(x,y).")
        fx_fn = sp.lambdify((x_sym, y_sym), fx, modules="numpy")
        fy_fn = sp.lambdify((x_sym, y_sym), fy, modules="numpy")
        fx_val = fx_fn(u, v)
        fy_val = fy_fn(u, v)
        return np.sqrt(1.0 + fx_val ** 2 + fy_val ** 2).astype(float)

    def normal(self, u: np.ndarray, v: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        x_sym, y_sym = sp.Symbol("x"), sp.Symbol("y")
        f = self.model.func_expr
        fx = sp.diff(f, x_sym) if f is not None else None
        fy = sp.diff(f, y_sym) if f is not None else None
        if fx is None or fy is None:
            raise SurfaceDefinitionError("No se pudo derivar z = f(x,y).")
        fx_fn = sp.lambdify((x_sym, y_sym), fx, modules="numpy")
        fy_fn = sp.lambdify((x_sym, y_sym), fy, modules="numpy")
        fx_val = fx_fn(u, v)
        fy_val = fy_fn(u, v)
        nx = -fx_val
        ny = -fy_val
        nz = np.ones_like(u, dtype=float)
        norm = np.sqrt(nx ** 2 + ny ** 2 + nz ** 2)
        return nx / norm, ny / norm, nz / norm

