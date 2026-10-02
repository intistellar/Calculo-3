"""
Visualizador de campos vectoriales 3D para SURFACELAB.
Implementa visualización de divergencia, rotacional, gradiente y campos vectoriales.
"""

from __future__ import annotations

from typing import List, Optional, Tuple

import numpy as np
import sympy as sp
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D

from surfacelab.core.vector_calculus import VectorOperator
from surfacelab.models.surface_model import SurfaceModel


class VectorFieldPlotter:
    """Clase para visualizar campos vectoriales en 3D."""

    @staticmethod
    def generate_field_grid(
        x_range: Tuple[float, float] = (-2, 2),
        y_range: Tuple[float, float] = (-2, 2),
        z_range: Tuple[float, float] = (-2, 2),
        resolution: int = 8,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Generar grid 3D para evaluar campos vectoriales."""
        x = np.linspace(x_range[0], x_range[1], resolution)
        y = np.linspace(y_range[0], y_range[1], resolution)
        z = np.linspace(z_range[0], z_range[1], resolution)
        X, Y, Z = np.meshgrid(x, y, z, indexing="ij")
        return X, Y, Z

    @staticmethod
    def evaluate_vector_field(
        field_expr: str,
        X: np.ndarray,
        Y: np.ndarray,
        Z: np.ndarray,
        system: str = "cartesian",
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Evaluar campo vectorial en grid 3D."""
        try:
            lambdas = VectorOperator.field_to_lambda(field_expr, system, is_vector=True)
            U = lambdas[0](X, Y, Z)
            V = lambdas[1](X, Y, Z)
            W = lambdas[2](X, Y, Z)
            return U, V, W
        except Exception as e:
            raise ValueError(f"Error al evaluar campo: {e}")

    @staticmethod
    def plot_quiver_3d(
        field_expr: str,
        ax: Axes3D,
        x_range: Tuple[float, float] = (-2, 2),
        y_range: Tuple[float, float] = (-2, 2),
        z_range: Tuple[float, float] = (-2, 2),
        resolution: int = 6,
        scale: float = 0.5,
        color: str = "blue",
        label: str = None,
    ) -> None:
        """Graficar campo vectorial con quiver 3D."""
        X, Y, Z = VectorFieldPlotter.generate_field_grid(x_range, y_range, z_range, resolution)
        U, V, W = VectorFieldPlotter.evaluate_vector_field(field_expr, X, Y, Z)

        # Normalizar para mejor visualización
        magnitude = np.sqrt(U**2 + V**2 + W**2)
        magnitude = np.where(magnitude == 0, 1, magnitude)

        ax.quiver(
            X, Y, Z,
            U / magnitude * scale,
            V / magnitude * scale,
            W / magnitude * scale,
            length=0.3,
            normalize=False,
            color=color,
            alpha=0.8,
            arrow_length_ratio=0.3,
        )
        if label:
            ax.text2D(0.02, 0.98, label, transform=ax.transAxes, fontsize=9, color=color)

    @staticmethod
    def plot_streamlines_3d(
        field_expr: str,
        ax: Axes3D,
        x_range: Tuple[float, float] = (-2, 2),
        y_range: Tuple[float, float] = (-2, 2),
        z_range: Tuple[float, float] = (-2, 2),
        seed: int = 42,
        n_lines: int = 15,
        color: str = "blue",
    ) -> None:
        """Graficar streamlines (líneas de flujo) del campo vectorial."""
        try:
            lambdas = VectorOperator.field_to_lambda(field_expr, "cartesian", is_vector=True)

            # Puntos iniciales para las streamlines
            np.random.seed(seed)
            x0 = np.random.uniform(x_range[0], x_range[1], n_lines)
            y0 = np.random.uniform(y_range[0], y_range[1], n_lines)
            z0 = np.random.uniform(z_range[0], z_range[1], n_lines)

            from mpl_toolkits.mplot3d import axes3d

            # Crear grid para interpolación
            X, Y, Z = VectorFieldPlotter.generate_field_grid(x_range, y_range, z_range, 20)
            U, V, W = VectorFieldPlotter.evaluate_vector_field(field_expr, X, Y, Z)

            # Dibujar puntos iniciales
            ax.scatter(x0, y0, z0, c=color, s=10, alpha=0.5)

        except Exception:
            pass  # Streamlines es opcional, no falla si no funciona

    @staticmethod
    def plot_divergence(
        vector_field: str,
        ax: Axes3D,
        x_range: Tuple[float, float] = (-2, 2),
        y_range: Tuple[float, float] = (-2, 2],
        resolution: int = 20,
        colorbar: bool = True,
    ) -> None:
        """Visualizar divergencia como heatmap en plano z=0."""
        div_expr = VectorOperator.divergence(vector_field, "cartesian")
        x_sym, y_sym, z_sym = sp.Symbol("x"), sp.Symbol("y"), sp.Symbol("z")
        div_lambda = sp.lambdify((x_sym, y_sym, z_sym), div_expr, modules="numpy")

        x = np.linspace(x_range[0], x_range[1], resolution)
        y = np.linspace(y_range[0], y_range[1], resolution)
        X, Y = np.meshgrid(x, y)
        Z = np.zeros_like(X)

        div_values = div_lambda(X, Y, Z)

        cmap = ax.contourf(X, Y, div_values, levels=20, cmap="RdBu_r", alpha=0.7)
        if colorbar:
            ax.figure.colorbar(cmap, ax=ax, label="Divergencia ∇·F")
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_title(f"Divergencia: ∇·F = {div_expr}")
        ax.set_aspect("equal")

    @staticmethod
    def plot_curl(
        vector_field: str,
        ax: Axes3D,
        x_range: Tuple[float, float] = (-2, 2),
        y_range: Tuple[float, float] = (-2, 2),
        z_range: Tuple[float, float] = (-2, 2),
        resolution: int = 6,
        scale: float = 0.5,
    ) -> None:
        """Visualizar rotacional como campo vectorial."""
        curl_x, curl_y, curl_z = VectorOperator.curl(vector_field, "cartesian")
        curl_expr = f"{curl_x}, {curl_y}, {curl_z}"

        VectorFieldPlotter.plot_quiver_3d(
            curl_expr, ax, x_range, y_range, z_range,
            resolution=resolution, scale=scale, color="red",
            label=f"Rotacional (∇×F)"
        )
        ax.set_title("Campo Rotacional ∇×F")

    @staticmethod
    def plot_gradient(
        scalar_field: str,
        ax: Axes3D,
        x_range: Tuple[float, float] = (-2, 2),
        y_range: Tuple[float, float] = (-2, 2),
        z_range: Tuple[float, float] = (-2, 2),
        resolution: int = 6,
        scale: float = 0.5,
    ) -> None:
        """Visualizar gradiente como campo vectorial."""
        grad_x, grad_y, grad_z = VectorOperator.gradient(scalar_field, "cartesian")
        grad_expr = f"{grad_x}, {grad_y}, {grad_z}"

        VectorFieldPlotter.plot_quiver_3d(
            grad_expr, ax, x_range, y_range, z_range,
            resolution=resolution, scale=scale, color="green",
            label=f"Gradiente (∇f)"
        )
        ax.set_title(f"Campo Gradiente: f = {scalar_field}")


class VectorFieldRenderer:
    """Renderer completo para visualizaciones vectoriales avanzadas."""

    @staticmethod
    def render_full_analysis(
        model: SurfaceModel,
        vector_field: Optional[str] = None,
        scalar_field: Optional[str] = None,
        resolution: int = 40,
        show_surface: bool = True,
        show_field: bool = False,
        show_curl: bool = False,
        show_divergence: bool = False,
        show_gradient: bool = False,
        show_normals: bool = False,
        colormap: str = "viridis",
        alpha: float = 0.85,
    ) -> Figure:
        """Renderizar análisis completo con múltiples visualizaciones."""
        from surfacelab.visualization.surface_plot import SurfacePlot
        from surfacelab.visualization.vector_plot import VectorPlot

        fig = Figure(figsize=(12, 8), dpi=100)

        # Determinar configuración de subplots
        n_plots = 1
        if show_surface: n_plots = 1
        if show_curl and not show_surface: n_plots = 1
        if show_divergence: n_plots = 2

        ax = fig.add_subplot(111, projection="3d")

        # Superficie base
        if show_surface:
            try:
                X, Y, Z = SurfacePlot.build_mesh(model, resolution)
                surf = ax.plot_surface(X, Y, Z, alpha=alpha, cmap=colormap, edgecolor="none")
                fig.colorbar(surf, ax=ax, shrink=0.5, aspect=10)
            except Exception:
                pass

        # Campo vectorial F
        if show_field and vector_field:
            try:
                VectorFieldPlotter.plot_quiver_3d(
                    vector_field, ax,
                    x_range=(model.limits.u_min, model.limits.u_max),
                    y_range=(model.limits.v_min, model.limits.v_max),
                    resolution=8, scale=0.4, color="blue", label="Campo F"
                )
            except Exception:
                pass

        # Rotacional
        if show_curl and vector_field:
            try:
                VectorFieldPlotter.plot_curl(
                    vector_field, ax,
                    x_range=(model.limits.u_min, model.limits.u_max),
                    y_range=(model.limits.v_min, model.limits.v_max),
                    resolution=8, scale=0.4
                )
            except Exception:
                pass

        # Gradiente
        if show_gradient and scalar_field:
            try:
                VectorFieldPlotter.plot_gradient(
                    scalar_field, ax,
                    x_range=(model.limits.u_min, model.limits.u_max),
                    y_range=(model.limits.v_min, model.limits.v_max),
                    resolution=8, scale=0.4
                )
            except Exception:
                pass

        # Normales
        if show_normals:
            try:
                x, y, z, nx, ny, nz = VectorPlot.normal_vectors(model, resolution=12, scale=0.4)
                if x is not None:
                    ax.quiver(x, y, z, nx, ny, nz, length=1.0, normalize=False, color="red", linewidth=1)
            except Exception:
                pass

        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")
        ax.set_title("Análisis de Campo Vectorial")

        return fig

    @staticmethod
    def create_comparison_figure(
        surface_models: List[SurfaceModel],
        titles: List[str] = None,
        resolution: int = 30,
    ) -> Figure:
        """Crear figura comparativa de múltiples superficies."""
        n = len(surface_models)
        if n == 0:
            raise ValueError("Se requiere al menos una superficie")
        if titles is None:
            titles = [f"Superficie {i+1}" for i in range(n)]

        cols = min(n, 3)
        rows = (n + cols - 1) // cols

        fig = Figure(figsize=(5 * cols, 4 * rows), dpi=100)

        for i, (model, title) in enumerate(zip(surface_models, titles)):
            ax = fig.add_subplot(rows, cols, i + 1, projection="3d")
            try:
                from surfacelab.visualization.surface_plot import SurfacePlot
                X, Y, Z = SurfacePlot.build_mesh(model, resolution)
                ax.plot_surface(X, Y, Z, alpha=0.85, cmap="viridis", edgecolor="none")
            except Exception:
                ax.text(0.5, 0.5, "Error", ha="center", va="center")
            ax.set_title(title)
            ax.set_xlabel("X")
            ax.set_ylabel("Y")
            ax.set_zlabel("Z")

        fig.tight_layout()
        return fig