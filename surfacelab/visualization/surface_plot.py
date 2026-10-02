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
# Funciones adicionales de análisis de superficie


class SurfaceAnalyzer:
    """Analizador de propiedades de superficies."""

    @staticmethod
    def detect_singularities(model: SurfaceModel, resolution: int = 50) -> dict:
        """
        Detectar singularidades en la superficie.
        
        Returns:
            Dict con información sobre puntos singulares
        """
        try:
            X, Y, Z = SurfacePlot.build_mesh(model, resolution)
            
            # Calcular Jacobian (diferencial de área)
            if model.system.value == "cartesian":
                from surfacelab.core.surface import CartesianSurface
                surf = CartesianSurface(model)
                dS = surf.differential_area(X, Y)
            elif model.system.value == "parametric":
                from surfacelab.core.parametrization import ParametricSurface
                surf = ParametricSurface(model)
                dS = surf.differential_area(
                    np.linspace(model.limits.u_min, model.limits.u_max, resolution),
                    np.linspace(model.limits.v_min, model.limits.v_max, resolution)
                )
            else:
                return {"has_singularities": False, "message": "Sistema no soportado para detección de singularidades"}
            
            # Detectar dónde el Jacobian es cero o muy pequeño
            threshold = 1e-6
            singular_mask = np.abs(dS) < threshold
            singular_count = np.sum(singular_mask)
            
            if singular_count > 0:
                singular_coords = []
                for i in range(resolution):
                    for j in range(resolution):
                        if singular_mask[i, j]:
                            singular_coords.append((float(X[i,j]), float(Y[i,j]), float(Z[i,j])))
                
                return {
                    "has_singularities": True,
                    "singular_count": singular_count,
                    "singular_points": singular_coords[:10],  # Máximo 10 puntos
                    "message": f"Se detectaron {singular_count} puntos singulares"
                }
            
            return {"has_singularities": False, "message": "No se detectaron singularidades"}
            
        except Exception as e:
            return {"has_singularities": False, "error": str(e)}

    @staticmethod
    def calculate_curvature(model: SurfaceModel, resolution: int = 20) -> dict:
        """
        Calcular curvatura gaussiana y media de la superficie.
        
        Returns:
            Dict con curvaturas
        """
        try:
            if model.system.value != "cartesian":
                return {"error": "Solo se soporta curvatura para superficies cartesianas"}
            
            x_sym, y_sym = sp.Symbol("x"), sp.Symbol("y")
            f = model.func_expr
            
            if f is None:
                return {"error": "No hay función definida"}
            
            # Primeras derivadas
            fx = sp.diff(f, x_sym)
            fy = sp.diff(f, y_sym)
            
            # Segundas derivadas
            fxx = sp.diff(fx, x_sym)
            fyy = sp.diff(fy, y_sym)
            fxy = sp.diff(fx, y_sym)
            
            # Coeficientes de la primera forma fundamental
            E = 1 + fx**2
            G = 1 + fy**2
            F = fx * fy
            
            # Coeficientes de la segunda forma fundamental
            L = fxx / sp.sqrt(1 + fx**2 + fy**2)
            M = fxy / sp.sqrt(1 + fx**2 + fy**2)
            N = fyy / sp.sqrt(1 + fx**2 + fy**2)
            
            # Curvatura gaussiana K = (LN - M²) / (EG - F²)
            K = sp.simplify((L*N - M**2) / (E*G - F**2))
            
            # Curvatura media H = (EN - 2FM + GL) / 2(EG - F²)
            H = sp.simplify((E*N - 2*F*M + G*L) / (2*(E*G - F**2)))
            
            return {
                "gaussian_curvature": str(K),
                "mean_curvature": str(H),
                "E": str(E), "F": str(F), "G": str(G),
                "L": str(L), "M": str(M), "N": str(N),
            }
            
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def create_slice(model: SurfaceModel, axis: str = "x", value: float = 0.0, resolution: int = 50) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Crear un slice (corte) de la superficie.
        
        Args:
            axis: Eje del corte ("x", "y", o "z")
            value: Valor del plano de corte
            
        Returns:
            Tupla de arrays (X, Y, Z) del slice
        """
        X, Y, Z = SurfacePlot.build_mesh(model, resolution)
        
        if axis == "x":
            # Slice en plano YZ
            idx = np.argmin(np.abs(X[:, 0, 0] - value))
            return None, Y[idx, :], Z[idx, :]
        elif axis == "y":
            idx = np.argmin(np.abs(Y[0, :, 0] - value))
            return X[idx, :], None, Z[idx, :]
        elif axis == "z":
            idx = np.argmin(np.abs(Z[0, 0, :] - value))
            return X[:, :, idx], Y[:, :, idx], None
            
        return X, Y, Z