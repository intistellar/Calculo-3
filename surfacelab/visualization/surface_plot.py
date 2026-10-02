from __future__ import annotations

from typing import Optional, Tuple

import numpy as np
import sympy as sp

from surfacelab.core.parametrization import ParametricSurface
from surfacelab.core.surface import CartesianSurface
from surfacelab.models.surface_model import SurfaceModel
from surfacelab.utils.parser import numeric_lambda


class SurfacePlot:
    @staticmethod
    def build_mesh(model: SurfaceModel, resolution: int = 40):
        system = model.system.value
        if system == "cartesian":
            return SurfacePlot._cartesian_mesh(model, resolution)
        if system == "parametric":
            return SurfacePlot._parametric_mesh(model, resolution)
        if system == "polar":
            return SurfacePlot._polar_mesh(model, resolution)
        if system == "cylindrical":
            return SurfacePlot._cylindrical_mesh(model, resolution)
        if system == "spherical":
            return SurfacePlot._spherical_mesh(model, resolution)
        raise NotImplementedError(f"Visualización no implementada para '{system}' en Fase 7.")

    @staticmethod
    def _cartesian_mesh(model: SurfaceModel, resolution: int):
        surf = CartesianSurface(model)
        u_min, u_max, v_min, v_max = model.limits.as_tuple()
        u = np.linspace(u_min, u_max, resolution)
        v = np.linspace(v_min, v_max, resolution)
        x, y, z = surf.parametrization(u, v)
        X, Y = np.meshgrid(x, y, indexing="ij")
        Z = np.broadcast_to(np.asarray(z, dtype=float), X.shape)
        return X, Y, Z

    @staticmethod
    def _parametric_mesh(model: SurfaceModel, resolution: int):
        surf = ParametricSurface(model)
        u_min, u_max, v_min, v_max = model.limits.as_tuple()
        u = np.linspace(u_min, u_max, resolution)
        v = np.linspace(v_min, v_max, resolution)
        x, y, z = surf.parametrization(u, v)
        return x, y, z

    @staticmethod
    def _polar_mesh(model: SurfaceModel, resolution: int):
        from surfacelab.core.parametrization import PolarSurface

        polar = PolarSurface(model)
        polar._prepare_polar()
        return SurfacePlot._parametric_mesh(model, resolution)

    @staticmethod
    def _cylindrical_mesh(model: SurfaceModel, resolution: int):
        from surfacelab.core.parametrization import CylindricalSurface

        cyl = CylindricalSurface(model)
        cyl._prepare_cylindrical()
        return SurfacePlot._parametric_mesh(model, resolution)

    @staticmethod
    def _spherical_mesh(model: SurfaceModel, resolution: int):
        from surfacelab.core.parametrization import SphericalSurface

        sph = SphericalSurface(model)
        sph._prepare_sphere(float(model.limits.u_min) if model.limits else 1.0)
        return SurfacePlot._parametric_mesh(model, resolution)


class VectorPlot:
    @staticmethod
    def normal_vectors(model: SurfaceModel, resolution: int = 10, scale: float = 0.4):
        system = model.system.value
        if system == "cartesian":
            surf = CartesianSurface(model)
        elif system in {"parametric", "polar", "cylindrical", "spherical"}:
            if system == "polar":
                from surfacelab.core.parametrization import PolarSurface
                surf = PolarSurface(model)
            elif system == "cylindrical":
                from surfacelab.core.parametrization import CylindricalSurface
                surf = CylindricalSurface(model)
            elif system == "spherical":
                from surfacelab.core.parametrization import SphericalSurface
                surf = SphericalSurface(model)
            else:
                surf = ParametricSurface(model)
        else:
            return None, None, None, None, None, None

        u_min, u_max, v_min, v_max = model.limits.as_tuple()
        u = np.linspace(u_min, u_max, resolution)
        v = np.linspace(v_min, v_max, resolution)
        x, y, z = surf.parametrization(u, v)
        nx, ny, nz = surf.normal(u, v)
        return x, y, z, nx * scale, ny * scale, nz * scale

    @staticmethod
    def flux_field(model: SurfaceModel, resolution: int = 10, scale: float = 0.5):
        if model.flux_components is None:
            return None, None, None, None, None, None
        system = model.system.value
        if system in {"parametric", "polar", "cylindrical", "spherical"}:
            from surfacelab.core.parametrization import (
                CylindricalSurface,
                ParametricSurface,
                PolarSurface,
                SphericalSurface,
            )

            if system == "polar":
                surf = PolarSurface(model)
            elif system == "cylindrical":
                surf = CylindricalSurface(model)
            elif system == "spherical":
                surf = SphericalSurface(model)
            else:
                surf = ParametricSurface(model)

            u_min, u_max, v_min, v_max = model.limits.as_tuple()
            u = np.linspace(u_min, u_max, resolution)
            v = np.linspace(v_min, v_max, resolution)
            U, V = np.meshgrid(u, v, indexing="ij")
            x, y, z = surf.parametrization(u, v)
            P, Q, R = model.flux_components
            p_fn = numeric_lambda(P, [sp.Symbol("u"), sp.Symbol("v")])
            q_fn = numeric_lambda(Q, [sp.Symbol("u"), sp.Symbol("v")])
            r_fn = numeric_lambda(R, [sp.Symbol("u"), sp.Symbol("v")])
            fx = p_fn(U, V) * scale
            fy = q_fn(U, V) * scale
            fz = r_fn(U, V) * scale
            return x, y, z, fx, fy, fz
        return None, None, None, None, None, None
