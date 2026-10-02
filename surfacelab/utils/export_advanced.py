"""
Módulo de exportación avanzada para SURFACELAB.
Incluye exportación a PDF, LaTeX, y reportes completos.
"""

from __future__ import annotations

import os
from datetime import datetime
from typing import Optional

from matplotlib.figure import Figure


class AdvancedExporter:
    """Exportador avanzado de resultados y visualizaciones."""

    @staticmethod
    def export_pdf_report(
        result: dict,
        fig: Figure,
        path: str,
        title: str = "SURFACELAB Report",
        include_latex: bool = True,
    ):
        """
        Exportar reporte completo a PDF.
        
        Args:
            result: Diccionario con resultados del cálculo
            fig: Figura de matplotlib para incluir
            path: Ruta del archivo PDF de salida
            title: Título del reporte
            include_latex: Si True, incluye código LaTeX
        """
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.platypus import (
                SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle
            )
            from reportlab.lib import colors

            doc = SimpleDocTemplate(path, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
            story = []
            styles = getSampleStyleSheet()

            # Título
            title_style = ParagraphStyle(
                "CustomTitle",
                parent=styles["Heading1"],
                fontSize=24,
                textColor=colors.HexColor("#1a73e8"),
                spaceAfter=30,
            )
            story.append(Paragraph(title, title_style))
            story.append(Spacer(1, 0.2*inch))

            # Fecha
            date_style = ParagraphStyle(
                "Date",
                parent=styles["Normal"],
                fontSize=10,
                textColor=colors.gray,
            )
            story.append(Paragraph(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", date_style))
            story.append(Spacer(1, 0.3*inch))

            # Resultados
            if result.get("success"):
                story.append(Paragraph("Resultados", styles["Heading2"]))
                
                if result.get("exact"):
                    story.append(Paragraph(f"<b>Resultado exacto:</b> {result['exact']}", styles["Normal"]))
                if result.get("approximate"):
                    story.append(Paragraph(f"<b>Resultado numérico:</b> {result['approximate']:.6f}", styles["Normal"]))
                if result.get("method"):
                    story.append(Paragraph(f"<b>Método:</b> {result['method']}", styles["Normal"]))

                story.append(Spacer(1, 0.2*inch))

                # Procedimiento
                story.append(Paragraph("Procedimiento", styles["Heading2"]))
                for step in result.get("procedure", []):
                    story.append(Paragraph(f"• {step}", styles["Normal"]))
                    story.append(Spacer(1, 0.1*inch))
            else:
                story.append(Paragraph(f"<b>Error:</b> {result.get('error_message', 'Desconocido')}", styles["Normal"]))

            story.append(PageBreak())

            # Imagen
            # Guardar figura temporalmente
            import tempfile
            temp_img = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
            fig.savefig(temp_img.name, dpi=150, bbox_inches="tight")
            temp_img.close()

            story.append(Paragraph("Visualización", styles["Heading2"]))
            img = Image(temp_img.name, width=6*inch, height=4.5*inch)
            story.append(img)

            # Código LaTeX opcional
            if include_latex and result.get("success"):
                story.append(PageBreak())
                story.append(Paragraph("Código LaTeX", styles["Heading2"]))
                
                latex_code = AdvancedExporter._generate_latex(result)
                code_style = ParagraphStyle(
                    "Code",
                    parent=styles["Code"],
                    fontSize=9,
                    leftIndent=20,
                    backgroundColor=colors.HexColor("#f5f5f5"),
                )
                story.append(Paragraph(latex_code, code_style))

                # Limpiar archivo temporal
                os.unlink(temp_img.name)

            # Construir PDF
            doc.build(story)

        except ImportError:
            # Si reportlab no está instalado, usar alternativa simple
            AdvancedExporter._export_simple_pdf(result, fig, path, title)

    @staticmethod
    def _export_simple_pdf(result: dict, fig: Figure, path: str, title: str):
        """Exportación simple a PDF sin dependencias extra."""
        # Guardar como imagen primero
        base, _ = os.path.splitext(path)
        img_path = f"{base}.png"
        fig.savefig(img_path, dpi=150, bbox_inches="tight")

        # Crear archivo de texto con información
        txt_path = f"{base}_info.txt"
        lines = [
            "="*60,
            title,
            "="*60,
            f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "-"*60,
        ]
        if result.get("success"):
            if result.get("exact"):
                lines.append(f"Resultado exacto: {result['exact']}")
            if result.get("approximate"):
                lines.append(f"Resultado numérico: {result['approximate']:.6f}")
            lines.append("-"*60)
            lines.append("PROCEDIMIENTO:")
            for step in result.get("procedure", []):
                lines.append(f"  {step}")
        else:
            lines.append(f"Error: {result.get('error_message', 'Desconocido')}")
        lines.append("="*60)
        lines.append(f"Imagen guardada en: {img_path}")

        with open(txt_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    @staticmethod
    def _generate_latex(result: dict) -> str:
        """Generar código LaTeX del resultado."""
        lines = []

        if result.get("exact"):
            exact_str = str(result["exact"])
            lines.append(f"% Resultado exacto")
            lines.append(f"\\[
            A = {exact_str}
            \\]")

        if result.get("procedure"):
            lines.append("% Procedimiento")
            lines.append("\\begin{enumerate}")
            for step in result.get("procedure", []):
                step_tex = step.replace("^", "\\textasciicircum ").replace("_", "\\_")
                lines.append(f"\\item ${step_tex}$")
            lines.append("\\end{enumerate}")

        return "\\n".join(lines)

    @staticmethod
    def export_latex_document(
        result: dict,
        path: str,
        title: str = "Surface Integral Report",
    ):
        """Exportar documento LaTeX completo."""
        latex_content = f"""\\documentclass[12pt]{{article}}
\\usepackage[utf8]{{inputenc}}
\\usepackage[spanish]{{babel}}
\\usepackage{{amsmath}}
\\usepackage{{amssymb}}
\\usepackage{{graphicx}}
\\usepackage{{geometry}}

\\geometry{{margin=1in}}

\\title{{{title}}}
\\author{{SURFACELAB}}
\\date{{\\today}}

\\begin{{document}}

\\maketitle

\\section*{{Resultados}}

"""
        if result.get("exact"):
            latex_content += f"\\textbf{{Resultado exacto:}} ${result['exact']}$\\\\\n"
        if result.get("approximate"):
            latex_content += f"\\textbf{{Resultado numérico:}} ${result['approximate']:.6f}$\\\\\n"
        if result.get("method"):
            latex_content += f"\\textbf{{Método:}} {result['method']}\\\\\n"

        latex_content += """
\section*{Procedimiento}

\\begin{enumerate}
"""
        for step in result.get("procedure", []):
            latex_content += f"\\item ${step}$\n"

        latex_content += """\\end{enumerate}

\\end{document}
"""
        with open(path, "w", encoding="utf-8") as f:
            f.write(latex_content)

    @staticmethod
    def export_html_report(
        result: dict,
        fig: Figure,
        path: str,
        title: str = "SURFACELAB Report",
    ):
        """Exportar reporte en formato HTML."""
        import tempfile

        # Guardar imagen
        temp_img = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        fig.savefig(temp_img.name, dpi=150, bbox_inches="tight")
        temp_img.close()
        img_data = open(temp_img.name, "rb").read()
        import base64
        img_b64 = base64.b64encode(img_data).decode()
        os.unlink(temp_img.name)

        html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1 {{ color: #1a73e8; }}
        h2 {{ color: #333; border-bottom: 2px solid #1a73e8; }}
        .result {{ background: #f5f5f5; padding: 15px; border-radius: 5px; }}
        .procedure {{ margin-left: 20px; }}
        img {{ max-width: 100%; border: 1px solid #ddd; }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <p>Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    
    <h2>Resultados</h2>
    <div class="result">
"""
        if result.get("exact"):
            html += f"<p><b>Resultado exacto:</b> {result['exact']}</p>"
        if result.get("approximate"):
            html += f"<p><b>Resultado numérico:</b> {result['approximate']:.6f}</p>"
        if result.get("method"):
            html += f"<p><b>Método:</b> {result['method']}</p>"

        html += """
    </div>
    
    <h2>Procedimiento</h2>
    <div class="procedure">
        <ol>
"""
        for step in result.get("procedure", []):
            html += f"            <li>{step}</li>\n"

        html += """        </ol>
    </div>
    
    <h2>Visualización</h2>
    <img src="data:image/png;base64,""" + img_b64 + """" alt="Superficie">
    
    <footer>
        <p>Generado por SURFACELAB</p>
    </footer>
</body>
</html>
"""
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)