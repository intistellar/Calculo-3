from __future__ import annotations

import sys
from typing import Optional

import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from surfacelab.calculators.coordinate_calculators import IntegralCalculator
from surfacelab.models.examples import Examples
from surfacelab.models.integral_model import IntegralModel
from surfacelab.models.parameter_model import ParameterModel
from surfacelab.models.surface_model import Limits, SurfaceSystem
from surfacelab.utils.export import ResultExporter
from surfacelab.utils.theory import TheoryPanel
from surfacelab.visualization.vector_plot import MatplotlibSurfaceRenderer

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("SURFACELAB - Calculadora de Integrales de Superficie")
        self.geometry("1200x720")

        self.model: Optional[IntegralModel] = None
        self.result: Optional[dict] = None
        self.parameter_model = ParameterModel()

        self._build_layout()

    def _build_layout(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        sidebar = ctk.CTkScrollableFrame(self, width=340, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")

        content = ctk.CTkFrame(self, corner_radius=0)
        content.grid(row=0, column=1, sticky="nsew")
        content.grid_rowconfigure(0, weight=1)
        content.grid_columnconfigure(0, weight=1)

        self._build_sidebar(sidebar)
        self.plot_frame = ctk.CTkFrame(content, corner_radius=0)
        self.plot_frame.grid(row=0, column=0, sticky="nsew")
        self.plot_frame.grid_rowconfigure(0, weight=1)
        self.plot_frame.grid_columnconfigure(0, weight=1)

        self.figure = Figure(figsize=(6, 5), dpi=100)
        self.ax = self.figure.add_subplot(111, projection="3d")
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.plot_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

        self.result_text = ctk.CTkTextbox(content, height=220, font=ctk.CTkFont(size=12))
        self.result_text.grid(row=1, column=0, sticky="ew", padx=8, pady=8)

    def _build_sidebar(self, parent):
        title = ctk.CTkLabel(parent, text="SURFACELAB", font=ctk.CTkFont(size=22, weight="bold"))
        title.pack(pady=(16, 4), padx=12, anchor="w")

        subtitle = ctk.CTkLabel(parent, text="Integrales de Superficie", font=ctk.CTkFont(size=12), text_color="gray")
        subtitle.pack(pady=(0, 16), padx=12, anchor="w")

        ctk.CTkLabel(parent, text="Sistema de representación").pack(padx=12, pady=(8, 4), anchor="w")
        self.system_combo = ctk.CTkOptionMenu(parent, values=[s.value for s in SurfaceSystem])
        self.system_combo.set(SurfaceSystem.CARTESIAN.value)
        self.system_combo.pack(padx=12, pady=(0, 12), fill="x")
        self.system_combo.configure(command=self._on_system_changed)

        ctk.CTkLabel(parent, text="Tipo de integral").pack(padx=12, pady=(8, 4), anchor="w")
        self.integral_combo = ctk.CTkOptionMenu(parent, values=["area", "scalar", "flux"])
        self.integral_combo.set("area")
        self.integral_combo.pack(padx=12, pady=(0, 12), fill="x")

        self.inputs_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.inputs_frame.pack(padx=12, pady=(0, 12), fill="x")
        self._build_dynamic_inputs()

        ctk.CTkLabel(parent, text="Límites").pack(padx=12, pady=(8, 4), anchor="w")
        self.entry_u_min = self._limit_entry(parent, "u / x / r min", "-1")
        self.entry_u_max = self._limit_entry(parent, "u / x / r max", "1")
        self.entry_v_min = self._limit_entry(parent, "v / y / theta min", "-1")
        self.entry_v_max = self._limit_entry(parent, "v / y / theta max", "1")

        ctk.CTkButton(parent, text="Visualizar", command=self._visualize).pack(padx=12, pady=(12, 6), fill="x")
        ctk.CTkButton(parent, text="Calcular", command=self._calculate).pack(padx=12, pady=(0, 12), fill="x")

        ctk.CTkLabel(parent, text="Ejemplos").pack(padx=12, pady=(8, 4), anchor="w")
        self.example_combo = ctk.CTkOptionMenu(parent, values=[e.name for e in Examples.list_examples()])
        self.example_combo.set("")
        self.example_combo.pack(padx=12, pady=(0, 12), fill="x")
        ctk.CTkButton(parent, text="Cargar ejemplo", command=self._load_example).pack(padx=12, pady=(0, 12), fill="x")

        ctk.CTkButton(parent, text="Exportar texto", command=self._export_text).pack(padx=12, pady=(0, 6), fill="x")
        ctk.CTkButton(parent, text="Exportar imagen", command=self._export_image).pack(padx=12, pady=(0, 12), fill="x")

        ctk.CTkButton(parent, text="Teoría", command=self._show_theory).pack(padx=12, pady=(0, 12), fill="x")

    def _limit_entry(self, parent, label, default):
        ctk.CTkLabel(parent, text=label).pack(padx=12, pady=(8, 4), anchor="w")
        entry = ctk.CTkEntry(parent)
        entry.insert(0, default)
        entry.pack(padx=12, pady=(0, 8), fill="x")
        return entry

    def _build_dynamic_inputs(self):
        for widget in self.inputs_frame.winfo_children():
            widget.destroy()

        system = self.system_combo.get()
        integral = self.integral_combo.get()

        if system == SurfaceSystem.CARTESIAN.value:
            ctk.CTkLabel(self.inputs_frame, text="z = f(x,y)").pack(anchor="w")
            self.entry_func = ctk.CTkEntry(self.inputs_frame)
            self.entry_func.insert(0, "x**2 + y**2")
            self.entry_func.pack(fill="x", pady=(0, 8))
        elif system == SurfaceSystem.PARAMETRIC.value:
            ctk.CTkLabel(self.inputs_frame, text="x(u,v)").pack(anchor="w")
            self.entry_x = ctk.CTkEntry(self.inputs_frame)
            self.entry_x.insert(0, "u")
            self.entry_x.pack(fill="x", pady=(0, 4))

            ctk.CTkLabel(self.inputs_frame, text="y(u,v)").pack(anchor="w")
            self.entry_y = ctk.CTkEntry(self.inputs_frame)
            self.entry_y.insert(0, "v")
            self.entry_y.pack(fill="x", pady=(0, 4))

            ctk.CTkLabel(self.inputs_frame, text="z(u,v)").pack(anchor="w")
            self.entry_z = ctk.CTkEntry(self.inputs_frame)
            self.entry_z.insert(0, "u**2 + v**2")
            self.entry_z.pack(fill="x", pady=(0, 8))
        elif system in {SurfaceSystem.POLAR.value, SurfaceSystem.CYLINDRICAL.value}:
            ctk.CTkLabel(self.inputs_frame, text="z = f(r, theta)").pack(anchor="w")
            self.entry_func = ctk.CTkEntry(self.inputs_frame)
            self.entry_func.insert(0, "r")
            self.entry_func.pack(fill="x", pady=(0, 8))
        elif system == SurfaceSystem.SPHERICAL.value:
            ctk.CTkLabel(self.inputs_frame, text="rho = f(phi) o constante").pack(anchor="w")
            self.entry_func = ctk.CTkEntry(self.inputs_frame)
            self.entry_func.insert(0, "2")
            self.entry_func.pack(fill="x", pady=(0, 8))

        if integral == "scalar":
            ctk.CTkLabel(self.inputs_frame, text="g(x,y,z) =").pack(anchor="w")
            self.entry_scalar = ctk.CTkEntry(self.inputs_frame)
            self.entry_scalar.insert(0, "1")
            self.entry_scalar.pack(fill="x", pady=(0, 8))
        elif integral == "flux":
            ctk.CTkLabel(self.inputs_frame, text="F = (P, Q, R)").pack(anchor="w")
            self.entry_flux = ctk.CTkEntry(self.inputs_frame)
            self.entry_flux.insert(0, "0, 0, 1")
            self.entry_flux.pack(fill="x", pady=(0, 8))

    def _on_system_changed(self, value):
        self._build_dynamic_inputs()

    def _read_model(self) -> IntegralModel:
        system = self.system_combo.get()
        integral = self.integral_combo.get()
        func_expr = None
        x_expr = None
        y_expr = None
        z_expr = None
        scalar_expr = None
        flux_expr = None

        if system == SurfaceSystem.CARTESIAN.value:
            func_expr = self.entry_func.get()
        elif system == SurfaceSystem.PARAMETRIC.value:
            x_expr = self.entry_x.get()
            y_expr = self.entry_y.get()
            z_expr = self.entry_z.get()
        elif system in {SurfaceSystem.POLAR.value, SurfaceSystem.CYLINDRICAL.value, SurfaceSystem.SPHERICAL.value}:
            func_expr = self.entry_func.get()

        if integral == "scalar":
            scalar_expr = self.entry_scalar.get()
        elif integral == "flux":
            flux_expr = self.entry_flux.get()

        limits = Limits(
            float(self.entry_u_min.get()),
            float(self.entry_u_max.get()),
            float(self.entry_v_min.get()),
            float(self.entry_v_max.get()),
        )

        return IntegralModel.create(
            system=system,
            func_expr=func_expr,
            x_expr=x_expr,
            y_expr=y_expr,
            z_expr=z_expr,
            limits=limits,
            integral_type=integral,
            scalar_expr=scalar_expr,
            flux_expr=flux_expr,
        )

    def _visualize(self):
        try:
            self.model = self._read_model()
            fig = MatplotlibSurfaceRenderer.render(
                self.model.model,
                resolution=self.parameter_model.resolution,
                show_normals=self.parameter_model.show_normals,
                show_flux_field=self.parameter_model.show_flux_field,
                normal_scale=self.parameter_model.normal_scale,
                flux_scale=self.parameter_model.flux_scale,
                alpha=self.parameter_model.alpha,
                colormap=self.parameter_model.colormap,
            )
            self._draw_figure(fig)
        except Exception as exc:
            self.result_text.delete("0.0", "end")
            self.result_text.insert("0.0", f"Error al visualizar: {exc}")

    def _calculate(self):
        try:
            self.model = self._read_model()
            self.result = IntegralCalculator.calculate(self.model.model, self.integral_combo.get())
            text = []
            if self.result.get("success"):
                if self.result.get("exact") is not None:
                    text.append(f"Resultado exacto: {self.result['exact']}")
                if self.result.get("approximate") is not None:
                    text.append(f"Resultado numérico: {self.result['approximate']}")
                text.append(f"Método: {self.result.get('method', 'N/A')}")
                text.append("")
                text.append("Procedimiento:")
                for step in self.result.get("procedure", []):
                    text.append(f"- {step}")
            else:
                text.append(f"Error: {self.result.get('error_message', 'Desconocido')}")
            self.result_text.delete("0.0", "end")
            self.result_text.insert("0.0", "\n".join(text))
        except Exception as exc:
            self.result_text.delete("0.0", "end")
            self.result_text.insert("0.0", f"Error al calcular: {exc}")

    def _load_example(self):
        name = self.example_combo.get()
        if not name:
            return
        model = Examples.load_example(name)
        if model is None:
            return
        self.system_combo.set(model.model.system.value)
        self.integral_combo.set("area")
        self._build_dynamic_inputs()
        self.model = model

    def _export_text(self):
        if self.result is None:
            return
        path = ctk.filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text", "*.txt")])
        if path:
            ResultExporter.export_text(self.result, path, "SURFACELAB")

    def _export_image(self):
        path = ctk.filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png")])
        if path:
            fig = MatplotlibSurfaceRenderer.render(self.model.model, resolution=self.parameter_model.resolution)
            ResultExporter.export_image(fig, path)

    def _show_theory(self):
        text = TheoryPanel.get_theory(self.system_combo.get())
        self.result_text.delete("0.0", "end")
        self.result_text.insert("0.0", text)

    def _draw_figure(self, fig):
        self.ax.clear()
        self.figure = fig
        self.canvas.get_tk_widget().destroy()
        self.canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        self.canvas.draw()


def main():
    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    main()
