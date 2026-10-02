from __future__ import annotations

import io
import os
from datetime import datetime
from typing import Optional

from surfacelab.visualization.vector_plot import MatplotlibSurfaceRenderer


class ResultExporter:
    @staticmethod
    def export_text(result: dict, path: str, title: str = "Resultado"):
        lines = [
            "=" * 60,
            title,
            "=" * 60,
            f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "-" * 60,
        ]
        if result.get("success"):
            if result.get("exact") is not None:
                lines.append(f"Resultado exacto: {result['exact']}")
            if result.get("approximate") is not None:
                lines.append(f"Resultado aproximado: {result['approximate']}")
            lines.append(f"Método: {result.get('method', 'N/A')}")
        else:
            lines.append(f"Error: {result.get('error_message', 'Desconocido')}")
        lines.append("-" * 60)
        lines.append("PROCEDIMIENTO:")
        for step in result.get("procedure", []):
            lines.append(f"  {step}")
        lines.append("=" * 60)

        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    @staticmethod
    def export_image(fig, path: str):
        MatplotlibSurfaceRenderer.save(fig, path)

    @staticmethod
    def export_report(result: dict, fig, path: str, title: str = "Reporte"):
        base, ext = os.path.splitext(path)
        text_path = f"{base}_reporte.txt"
        image_path = f"{base}_imagen.png"

        ResultExporter.export_text(result, text_path, title)
        ResultExporter.export_image(fig, image_path)
