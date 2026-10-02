from __future__ import annotations

from typing import Optional, Tuple

import numpy as np
import sympy as sp

from surfacelab.core.surface import Surface, SurfaceDefinitionError
from surfacelab.models.surface_model import SurfaceModel


class ParametricSurface(Surface):
    def _prepare(self, u: np.ndarray, v: np.ndarray):
        U, V = np.meshgrid(u, v, indexing="ij")
        return U.astype(float), V.astype(float)

    def _component(self, expr: Optional[sp.Expr], u: np.ndarray, v: np.ndarray) -> np.ndarray:
        if expr is None:
            raise SurfaceDefinitionError("Falta componente de la parametrización.")
        U, V = self._prepare(u, v)
        u_sym, v_sym = sp.Symbol("u"), sp.Symbol("v")
        fn = sp.lambdify((u_sym, v_sym), expr, modules="numpy")
        return fn(U, V)

    def parametrization(self, u: np.ndarray, v: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        return (
            self._component(self.model.x_expr, u, v),
            self._component(self.model.y_expr, u, v),
            self._component(self.model.z_expr, u, v),
        )

    def _cross_magnitude(self, u: np.ndarray, v: np.ndarray) -> np.ndarray:
        x_expr, y_expr, z_expr = self.model.x_expr, self.model.y_expr, self.model.z_expr
        if x_expr is None or y_expr is None or z_expr is None:
            raise SurfaceDefinitionError("Parametrización incompleta.")
        U, V = self._prepare(u, v)
        u_sym, v_sym = sp.Symbol("u"), sp.Symbol("v")
        rx = sp.Matrix([x_expr, y_expr, z_expr])
        ru = sp.diff(rx, u_sym)
        rv = sp.diff(rx, v_sym)
        cross = ru.cross(rv)
        magnitude = sp.sqrt(cross.dot(cross))
        magnitude = sp.simplify(magnitude)
        fn = sp.lambdify((u_sym, v_sym), magnitude, modules="numpy")
        return fn(U, V)

    def differential_area(self, u: np.ndarray, v: np.ndarray) -> np.ndarray:
        return self._cross_magnitude(u, v)

    def normal(self, u: np.ndarray, v: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        x_expr, y_expr, z_expr = self.model.x_expr, self.model.y_expr, self.model.z_expr
        U, V = self._prepare(u, v)
        u_sym, v_sym = sp.Symbol("u"), sp.Symbol("v")
        rx = sp.Matrix([x_expr, y_expr, z_expr])
        ru = sp.diff(rx, u_sym)
        rv = sp.diff(rx, v_sym)
        cross = ru.cross(rv)
        fn_x = sp.lambdify((u_sym, v_sym), cross[0], modules="numpy")
        fn_y = sp.lambdify((u_sym, v_sym), cross[1], modules="numpy")
        fn_z = sp.lambdify((u_sym, v_sym), cross[2], modules="numpy")
        nx, ny, nz = fn_x(U, V), fn_y(U, V), fn_z(U, V)
        norm = np.sqrt(nx ** 2 + ny ** 2 + nz ** 2)
        norm = np.where(norm == 0, 1.0, norm)
        return nx / norm, ny / norm, nz / norm


class PolarSurface(ParametricSurface):
    def _prepare_polar(self):
        if self.model.func_expr is None:
            raise SurfaceDefinitionError("Falta z = f(r, theta).")
        r_sym, th_sym = sp.Symbol("r"), sp.Symbol("theta")
        u_sym, v_sym = sp.Symbol("u"), sp.Symbol("v")
        if self.model.x_expr is None:
            self.model.x_expr = (r_sym * sp.cos(th_sym)).subs({r_sym: u_sym, th_sym: v_sym})
        if self.model.y_expr is None:
            self.model.y_expr = (r_sym * sp.sin(th_sym)).subs({r_sym: u_sym, th_sym: v_sym})
        if self.model.z_expr is None:
            self.model.z_expr = self.model.func_expr.subs({r_sym: u_sym, th_sym: v_sym})

    def parametrization(self, u: np.ndarray, v: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        self._prepare_polar()
        return super().parametrization(u, v)

    def differential_area(self, u: np.ndarray, v: np.ndarray) -> np.ndarray:
        self._prepare_polar()
        return super().differential_area(u, v)

    def normal(self, u: np.ndarray, v: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        self._prepare_polar()
        return super().normal(u, v)


class CylindricalSurface(ParametricSurface):
    def _prepare_cylindrical(self):
        r_sym, th_sym, z_sym = sp.Symbol("r"), sp.Symbol("theta"), sp.Symbol("z")
        u_sym, v_sym = sp.Symbol("u"), sp.Symbol("v")
        if self.model.func_expr is not None and self.model.x_expr is None:
            self.model.x_expr = (r_sym * sp.cos(th_sym)).subs({r_sym: u_sym, th_sym: v_sym})
            self.model.y_expr = (r_sym * sp.sin(th_sym)).subs({r_sym: u_sym, th_sym: v_sym})
            self.model.z_expr = self.model.func_expr.subs({r_sym: u_sym, th_sym: v_sym})
        elif self.model.x_expr is None and self.model.y_expr is None and self.model.z_expr is None:
            raise SurfaceDefinitionError("Falta parametrización cilíndrica.")

    def parametrization(self, u: np.ndarray, v: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        self._prepare_cylindrical()
        return super().parametrization(u, v)

    def differential_area(self, u: np.ndarray, v: np.ndarray) -> np.ndarray:
        self._prepare_cylindrical()
        return super().differential_area(u, v)

    def normal(self, u: np.ndarray, v: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        self._prepare_cylindrical()
        return super().normal(u, v)


class SphericalSurface(ParametricSurface):
    def _prepare_sphere(self, radius: float):
        u_sym, v_sym = sp.Symbol("u"), sp.Symbol("v")
        if self.model.x_expr is None:
            self.model.x_expr = radius * sp.sin(v_sym) * sp.cos(u_sym)
        if self.model.y_expr is None:
            self.model.y_expr = radius * sp.sin(v_sym) * sp.sin(u_sym)
        if self.model.z_expr is None:
            self.model.z_expr = radius * sp.cos(v_sym)

    def _prepare_spherical(self):
        rho_sym, th_sym, phi_sym = sp.Symbol("rho"), sp.Symbol("theta"), sp.Symbol("phi")
        u_sym, v_sym = sp.Symbol("u"), sp.Symbol("v")
        if self.model.func_expr is not None and self.model.x_expr is None:
            self.model.x_expr = (rho_sym * sp.sin(phi_sym) * sp.cos(th_sym)).subs({rho_sym: u_sym, phi_sym: v_sym, th_sym: u_sym})
            self.model.y_expr = (rho_sym * sp.sin(phi_sym) * sp.sin(th_sym)).subs({rho_sym: u_sym, phi_sym: v_sym, th_sym: u_sym})
            self.model.z_expr = (rho_sym * sp.cos(phi_sym)).subs({rho_sym: u_sym, phi_sym: v_sym})
        elif self.model.x_expr is None and self.model.y_expr is None and self.model.z_expr is None:
            raise SurfaceDefinitionError("Falta parametrización esférica.")

    def parametrization(self, u: np.ndarray, v: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        if self.model.func_expr is not None:
            self._prepare_spherical()
        else:
            self._prepare_sphere(float(self.model.limits.u_min) if self.model.limits else 1.0)
        return super().parametrization(u, v)

    def differential_area(self, u: np.ndarray, v: np.ndarray) -> np.ndarray:
        if self.model.func_expr is not None:
            self._prepare_spherical()
        else:
            self._prepare_sphere(float(self.model.limits.u_min) if self.model.limits else 1.0)
        return super().differential_area(u, v)

    def normal(self, u: np.ndarray, v: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        if self.model.func_expr is not None:
            self._prepare_spherical()
        else:
            self._prepare_sphere(float(self.model.limits.u_min) if self.model.limits else 1.0)
        return super().normal(u, v)
