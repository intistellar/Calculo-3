from __future__ import annotations

from typing import Optional, Tuple

import numpy as np
import sympy as sp
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from mpl_toolkits.mplot3d import Axes3D  # noqa

from surfacelab.models.surface_model import SurfaceModel
from surfacelab.visualization.surface_plot import SurfacePlot, VectorPlot


class MatplotlibSurfaceRenderer:
    @staticmethod
    def render(
        model: SurfaceModel,
        resolution: int = 40,
        show_normals: bool = False,
        show_flux_field: bool = False,
        normal_scale: float = 0.4,
        flux_scale: float = 0.5,
        alpha: float = 0.85,
        colormap: str = "viridis",
        show_wireframe: bool = False,
        show_axes: bool = True,
        show_contour: bool = False,
        contour_projection: str = "xy",
    ) -> Figure:
        X, Y, Z = SurfacePlot.build_mesh(model, resolution)
        fig = Figure(figsize=(8, 6), dpi=100)
        ax = fig.add_subplot(111, projection="3d")
        
        # Superficie base
        if show_wireframe:
            # Wireframe (malla)
            ax.plot_wireframe(X, Y, Z, alpha=alpha, color="gray", linewidth=0.3)
        else:
            surf = ax.plot_surface(X, Y, Z, alpha=alpha, cmap=colormap, edgecolor="none")
            fig.colorbar(surf, ax=ax, shrink=0.5)

        # Contour lines (líneas de nivel)
        if show_contour:
            if contour_projection == "xy":
                ax.contour(X, Y, Z, zdir='z', offset=np.min(Z), cmap=colormap, alpha=0.5)
            elif contour_projection == "xz":
                ax.contour(X, Y, Z, zdir='y', offset=np.max(Y), cmap=colormap, alpha=0.5)
            elif contour_projection == "yz":
                ax.contour(X, Y, Z, zdir='x', offset=np.min(X), cmap=colormap, alpha=0.5)

        # Ejes de coordenadas
        if show_axes:
            MatplotlibSurfaceRenderer._add_axes(ax)

        if show_normals:
            x, y, z, nx, ny, nz = VectorPlot.normal_vectors(model, resolution=12, scale=normal_scale)
            if x is not None:
                ax.quiver(x, y, z, nx, ny, nz, length=1.0, normalize=False, color="red", linewidth=1)

        if show_flux_field and model.flux_components is not None:
            x, y, z, fx, fy, fz = VectorPlot.flux_field(model, resolution=12, scale=flux_scale)
            if x is not None:
                ax.quiver(x, y, z, fx, fy, fz, length=1.0, normalize=False, color="blue", linewidth=1)

        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")
        ax.set_title("Superficie")
        
        # Habilitar interactividad
        ax.mouse_init()
        
        return fig

    @staticmethod
    def _add_axes(ax):
        """Añadir ejes de coordenadas coloreados."""
        # Obtener límites actuales
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        zlim = ax.get_zlim()
        
        # Longitud de los ejes
        max_range = max(xlim[1]-xlim[0], ylim[1]-ylim[0], zlim[1]-zlim[0])
        origin = (
            xlim[0] + (xlim[1]-xlim[0])*0.05,
            ylim[0] + (ylim[1]-ylim[0])*0.05,
            zlim[0] + (zlim[1]-zlim[0])*0.05
        )
        
        # Dibujar ejes
        ax.quiver(origin[0], origin[1], origin[2], max_range*0.15, 0, 0, color='red', arrow_length_ratio=0.5)
        ax.quiver(origin[0], origin[1], origin[2], 0, max_range*0.15, 0, color='green', arrow_length_ratio=0.5)
        ax.quiver(origin[0], origin[1], origin[2], 0, 0, max_range*0.15, color='blue', arrow_length_ratio=0.5)
        
        # Etiquetas
        ax.text(max_range*0.18, origin[1], origin[2], 'X', color='red', fontsize=10)
        ax.text(origin[0], max_range*0.18, origin[2], 'Y', color='green', fontsize=10)
        ax.text(origin[0], origin[1], max_range*0.18, 'Z', color='blue', fontsize=10)

    @staticmethod
    def save(fig: Figure, path: str):
        fig.savefig(path, bbox_inches="tight")

    @staticmethod
    def to_image(fig: Figure) -> "PIL.Image.Image":
        import io
        from PIL import Image

        canvas = FigureCanvas(fig)
        canvas.draw()
        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight")
        buf.seek(0)
        return Image.open(buf)
