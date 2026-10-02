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
# Métodos adicionales para visualización de cálculo vectorial

from surfacelab.core.vector_calculus import VectorOperator


class VectorCalculusPlot:
    """Clase para visualizar operadores vectoriales sobre superficies."""

    @staticmethod
    def plot_curl_over_surface(
        model,
        vector_field: str,
        resolution: int = 10,
        scale: float = 0.4,
        color: str = "red",
    ):
        """Calcular y visualizar el rotacional sobre la superficie."""
        try:
            curl_x, curl_y, curl_z = VectorOperator.curl(vector_field, "cartesian")
            return {
                "curl_x": str(curl_x),
                "curl_y": str(curl_y),
                "curl_z": str(curl_z),
                "expression": f"({curl_x}, {curl_y}, {curl_z})",
            }
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def plot_divergence_over_surface(
        model,
        vector_field: str,
    ):
        """Calcular divergencia del campo sobre la superficie."""
        try:
            div = VectorOperator.divergence(vector_field, "cartesian")
            return {"divergence": str(div), "expression": div}
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def plot_gradient_over_surface(
        model,
        scalar_field: str,
    ):
        """Calcular gradiente del campo escalar."""
        try:
            grad_x, grad_y, grad_z = VectorOperator.gradient(scalar_field, "cartesian")
            return {
                "grad_x": str(grad_x),
                "grad_y": str(grad_y),
                "grad_z": str(grad_z),
                "expression": f"({grad_x}, {grad_y}, {grad_z})",
            }
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def compute_surface_divergence(
        model,
        vector_field: str,
    ):
        """Calcular flujo saliente en superficie cerrada."""
        try:
            flux = VectorOperator.compute_flux_through_surface(
                vector_field, str(model.func_expr)
            )
            return {"flux_expression": str(flux), "expression": flux}
        except Exception as e:
            return {"error": str(e)}