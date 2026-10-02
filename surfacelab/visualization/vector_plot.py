from __future__ import annotations

from typing import Optional

import numpy as np
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
    ) -> Figure:
        X, Y, Z = SurfacePlot.build_mesh(model, resolution)
        fig = Figure(figsize=(8, 6), dpi=100)
        ax = fig.add_subplot(111, projection="3d")
        surf = ax.plot_surface(X, Y, Z, alpha=alpha, cmap=colormap, edgecolor="none")
        fig.colorbar(surf, ax=ax, shrink=0.5)

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
        return fig

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
