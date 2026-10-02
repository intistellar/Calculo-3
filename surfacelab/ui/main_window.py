from __future__ import annotations

import sys
from typing import Optional

import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from surfacelab.calculators.coordinate_calculators import IntegralCalculator
from surfacelab.core.vector_calculus import VectorOperator
from surfacelab.models.examples import Examples
from surfacelab.models.integral_model import IntegralModel
from surfacelab.models.parameter_model import ParameterModel
from surfacelab.models.surface_model import Limits, SurfaceSystem
from surfacelab.utils.export import ResultExporter
from surfacelab.utils.theory import TheoryPanel
from surfacelab.visualization.vector_plot import MatplotlibSurfaceRenderer
from surfacelab.visualization.surface_plot import SurfacePlot, SurfaceAnalyzer

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("SURFACELAB - Calculadora de Integrales de Superficie")
        self.geometry("1400x800")

        self.model: Optional[IntegralModel] = None
        self.result: Optional[dict] = None
        self.parameter_model = ParameterModel()

        # Variables para checkboxes de visualización vectorial
        self.var_show_normals = ctk.BooleanVar(value=False)
        self.var_show_field = ctk.BooleanVar(value=False)
        self.var_show_curl = ctk.BooleanVar(value=False)
        self.var_show_gradient = ctk.BooleanVar(value=False)
        self.var_show_divergence = ctk.BooleanVar(value=False)
        
        # Variables para visualización avanzada
        self.var_show_wireframe = ctk.BooleanVar(value=False)
        self.var_show_axes = ctk.BooleanVar(value=True)
        self.var_show_contour = ctk.BooleanVar(value=False)

        # Variables para campos
        self.vector_field_expr = "x, y, z"
        self.scalar_field_expr = "x**2 + y**2 + z**2"

        # Variables para modo
        self.dark_mode = True

        self._build_layout()

        # Configurar atajos de teclado
        self.bind("<Control-r>", lambda e: self._visualize())
        self.bind("<Control-R>", lambda e: self._visualize())
        self.bind("<Control-c>", lambda e: self._calculate())
        self.bind("<Control-C>", lambda e: self._calculate())
        self.bind("<Control-e>", lambda e: self._export_text())
        self.bind("<Control-E>", lambda e: self._export_text())
        self.bind("<Control-t>", lambda e: self._show_theory())
        self.bind("<Control-T>", lambda e: self._show_theory())
        self.bind("<Control-d>", lambda e: self._toggle_dark_mode())
        self.bind("<Control-D>", lambda e: self._toggle_dark_mode())

    def _build_layout(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        sidebar = ctk.CTkScrollableFrame(self, width=400, corner_radius=0)
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

        self.figure = Figure(figsize=(8, 6), dpi=100)
        self.ax = self.figure.add_subplot(111, projection="3d")
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.plot_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

        self.result_text = ctk.CTkTextbox(content, height=200, font=ctk.CTkFont(size=12))
        self.result_text.grid(row=1, column=0, sticky="ew", padx=8, pady=8)

    def _build_sidebar(self, parent):
        # Título
        title = ctk.CTkLabel(parent, text="SURFACELAB", font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(pady=(16, 4), padx=12, anchor="w")

        subtitle = ctk.CTkLabel(parent, text="Integrales de Superficie + Cálculo Vectorial", 
                               font=ctk.CTkFont(size=11), text_color="gray")
        subtitle.pack(pady=(0, 16), padx=12, anchor="w")

        # === Sección: Sistema de coordenadas ===
        ctk.CTkLabel(parent, text="Sistema de coordenadas", font=ctk.CTkFont(weight="bold")).pack(padx=12, pady=(8, 4), anchor="w")
        self.system_combo = ctk.CTkOptionMenu(parent, values=[s.value for s in SurfaceSystem])
        self.system_combo.set(SurfaceSystem.CARTESIAN.value)
        self.system_combo.pack(padx=12, pady=(0, 8), fill="x")
        self.system_combo.configure(command=self._on_system_changed)

        # === Sección: Tipo de integral ===
        ctk.CTkLabel(parent, text="Tipo de cálculo", font=ctk.CTkFont(weight="bold")).pack(padx=12, pady=(8, 4), anchor="w")
        self.integral_combo = ctk.CTkOptionMenu(parent, values=["area", "scalar", "flux", "divergence", "curl", "gradient"])
        self.integral_combo.set("area")
        self.integral_combo.pack(padx=12, pady=(0, 8), fill="x")

        # === Sección: Función de la superficie ===
        self.inputs_frame = ctk.CTkFrame(parent)
        self.inputs_frame.pack(padx=12, pady=(0, 8), fill="x")
        self._build_dynamic_inputs()

        # === Sección: Límites ===
        ctk.CTkLabel(parent, text="Límites de integración", font=ctk.CTkFont(weight="bold")).pack(padx=12, pady=(8, 4), anchor="w")
        self.entry_u_min = self._limit_entry(parent, "u / x / r  min", "-2")
        self.entry_u_max = self._limit_entry(parent, "u / x / r  max", "2")
        self.entry_v_min = self._limit_entry(parent, "v / y / θ min", "-2")
        self.entry_v_max = self._limit_entry(parent, "v / y / θ max", "2")

        # === Sección: Campo vectorial ===
        field_frame = ctk.CTkFrame(parent)
        field_frame.pack(padx=12, pady=(8, 8), fill="x")
        ctk.CTkLabel(field_frame, text="Campo Vectorial F = (P, Q, R)", font=ctk.CTkFont(weight="bold")).pack(padx=12, pady=(8, 4), anchor="w")
        ctk.CTkLabel(field_frame, text="Ej: x, y, z  o  -y, x, 0", font=ctk.CTkFont(size=10), text_color="gray").pack(padx=12, pady=(0, 4), anchor="w")
        self.entry_flux = ctk.CTkEntry(field_frame)
        self.entry_flux.insert(0, "x, y, z")
        self.entry_flux.pack(padx=12, pady=(0, 8), fill="x")

        # Campo escalar para gradiente
        ctk.CTkLabel(field_frame, text="Campo Escalar f(x,y,z)", font=ctk.CTkFont(weight="bold")).pack(padx=12, pady=(8, 4), anchor="w")
        self.entry_scalar = ctk.CTkEntry(field_frame)
        self.entry_scalar.insert(0, "x**2 + y**2 + z**2")
        self.entry_scalar.pack(padx=12, pady=(0, 8), fill="x")

        # === Botones principales ===
        btn_frame = ctk.CTkFrame(parent, fg_color="transparent")
        btn_frame.pack(padx=12, pady=(8, 8), fill="x")
        ctk.CTkButton(btn_frame, text="🎨 Visualizar", command=self._visualize, height=36).pack(padx=4, pady=4, fill="x", side="left")
        ctk.CTkButton(btn_frame, text="🧮 Calcular", command=self._calculate, height=36).pack(padx=4, pady=4, fill="x", side="left")

        # === Sección: Controles de visualización ===
        viz_frame = ctk.CTkFrame(parent)
        viz_frame.pack(padx=12, pady=(8, 8), fill="x")
        ctk.CTkLabel(viz_frame, text="Visualización Vectorial", font=ctk.CTkFont(weight="bold")).pack(padx=12, pady=(8, 4), anchor="w")

        ctk.CTkCheckBox(viz_frame, text="Mostrar normales", variable=self.var_show_normals).pack(padx=12, pady=2, anchor="w")
        ctk.CTkCheckBox(viz_frame, text="Mostrar campo F", variable=self.var_show_field).pack(padx=12, pady=2, anchor="w")
        ctk.CTkCheckBox(viz_frame, text="Mostrar rotacional (∇×F)", variable=self.var_show_curl).pack(padx=12, pady=2, anchor="w")
        ctk.CTkCheckBox(viz_frame, text="Mostrar gradiente (∇f)", variable=self.var_show_gradient).pack(padx=12, pady=2, anchor="w")
        ctk.CTkCheckBox(viz_frame, text="Mostrar divergencia (∇·F)", variable=self.var_show_divergence).pack(padx=12, pady=2, anchor="w")
        
        # === Visualización avanzada ===
        adv_viz_frame = ctk.CTkFrame(parent)
        adv_viz_frame.pack(padx=12, pady=(8, 8), fill="x")
        ctk.CTkLabel(adv_viz_frame, text="Visualización Avanzada", font=ctk.CTkFont(weight="bold")).pack(padx=12, pady=(8, 4), anchor="w")
        
        ctk.CTkCheckBox(adv_viz_frame, text="Mostrar wireframe (malla)", variable=self.var_show_wireframe).pack(padx=12, pady=2, anchor="w")
        ctk.CTkCheckBox(adv_viz_frame, text="Mostrar ejes (XYZ)", variable=self.var_show_axes).pack(padx=12, pady=2, anchor="w")
        ctk.CTkCheckBox(adv_viz_frame, text="Mostrar contour (líneas nivel)", variable=self.var_show_contour).pack(padx=12, pady=2, anchor="w")
        
        # Selector de proyección para contour
        ctk.CTkLabel(adv_viz_frame, text="Proyección contour:", font=ctk.CTkFont(size=10)).pack(padx=12, pady=(4, 0), anchor="w")
        self.contour_projection = ctk.CTkOptionMenu(adv_viz_frame, values=["xy", "xz", "yz"])
        self.contour_projection.set("xy")
        self.contour_projection.pack(padx=12, pady=(0, 8), fill="x")
        
        # Vistas predefinidas
        ctk.CTkLabel(adv_viz_frame, text="Vista predefinida:", font=ctk.CTkFont(size=10)).pack(padx=12, pady=(4, 0), anchor="w")
        view_btn_frame = ctk.CTkFrame(adv_viz_frame, fg_color="transparent")
        view_btn_frame.pack(padx=12, pady=4, fill="x")
        ctk.CTkButton(view_btn_frame, text="Iso", command=lambda: self._set_view("iso"), width=50).pack(padx=2, side="left")
        ctk.CTkButton(view_btn_frame, text="Arriba", command=lambda: self._set_view("top"), width=50).pack(padx=2, side="left")
        ctk.CTkButton(view_btn_frame, text="Frente", command=lambda: self._set_view("front"), width=50).pack(padx=2, side="left")
        ctk.CTkButton(view_btn_frame, text="Lado", command=lambda: self._set_view("side"), width=50).pack(padx=2, side="left")

        # === Control de resolución ===
        res_frame = ctk.CTkFrame(parent)
        res_frame.pack(padx=12, pady=(8, 8), fill="x")
        ctk.CTkLabel(res_frame, text="Resolución de malla", font=ctk.CTkFont(weight="bold")).pack(padx=12, pady=(8, 4), anchor="w")
        self.resolution_slider = ctk.CTkSlider(res_frame, from_=10, to=80, number_of_steps=70)
        self.resolution_slider.set(40)
        self.resolution_slider.pack(padx=12, pady=(0, 4), fill="x")
        self.resolution_label = ctk.CTkLabel(res_frame, text="40", font=ctk.CTkFont(size=10))
        self.resolution_label.pack(padx=12, pady=(0, 8))
        self.resolution_slider.configure(command=self._on_resolution_changed)

        # === Selector de color ===
        ctk.CTkLabel(res_frame, text="Colormap", font=ctk.CTkFont(weight="bold")).pack(padx=12, pady=(8, 4), anchor="w")
        self.colormap_combo = ctk.CTkOptionMenu(res_frame, values=["viridis", "plasma", "inferno", "magma", "coolwarm", "RdBu", "seismic"])
        self.colormap_combo.set("viridis")
        self.colormap_combo.pack(padx=12, pady=(0, 8), fill="x")

        # === Sección: Ejemplos ===
        ctk.CTkLabel(parent, text="Ejemplos", font=ctk.CTkFont(weight="bold")).pack(padx=12, pady=(8, 4), anchor="w")
        self.example_combo = ctk.CTkOptionMenu(parent, values=[e.name for e in Examples.list_examples()] + ["Toro", "Hiperboloide", "Cono", "Casquete"])
        self.example_combo.pack(padx=12, pady=(0, 8), fill="x")
        ctk.CTkButton(parent, text="Cargar ejemplo", command=self._load_example).pack(padx=12, pady=(0, 8), fill="x")

        # === Sección: Exportación y teoría ===
        ctk.CTkLabel(parent, text="Acciones", font=ctk.CTkFont(weight="bold")).pack(padx=12, pady=(8, 4), anchor="w")
        ctk.CTkButton(parent, text="📄 Exportar texto", command=self._export_text).pack(padx=12, pady=4, fill="x")
        ctk.CTkButton(parent, text="🖼️ Exportar imagen", command=self._export_image).pack(padx=12, pady=4, fill="x")
        ctk.CTkButton(parent, text="📋 Copiar al portapapeles", command=self._copy_to_clipboard).pack(padx=12, pady=4, fill="x")
        
        # === Sesión ===
        session_frame = ctk.CTkFrame(parent)
        session_frame.pack(padx=12, pady=(8, 8), fill="x")
        ctk.CTkLabel(session_frame, text="Sesión", font=ctk.CTkFont(weight="bold")).pack(padx=12, pady=(8, 4), anchor="w")
        ctk.CTkButton(session_frame, text="💾 Guardar sesión", command=self._save_session).pack(padx=12, pady=2, fill="x")
        ctk.CTkButton(session_frame, text="📂 Cargar sesión", command=self._load_session).pack(padx=12, pady=2, fill="x")
        
        # === Análisis avanzado ===
        analysis_frame = ctk.CTkFrame(parent)
        analysis_frame.pack(padx=12, pady=(8, 12), fill="x")
        ctk.CTkLabel(analysis_frame, text="Análisis Avanzado", font=ctk.CTkFont(weight="bold")).pack(padx=12, pady=(8, 4), anchor="w")
        ctk.CTkButton(analysis_frame, text="🔍 Detectar singularidades", command=self._detect_singularities).pack(padx=12, pady=2, fill="x")
        ctk.CTkButton(analysis_frame, text="📐 Calcular curvatura", command=self._calculate_curvature).pack(padx=12, pady=2, fill="x")
        ctk.CTkButton(analysis_frame, text="📚 Teoría", command=self._show_theory).pack(padx=12, pady=4, fill="x")

        # === Sección: Calculadora vectorial rápida ===
        calc_frame = ctk.CTkFrame(parent)
        calc_frame.pack(padx=12, pady=(8, 12), fill="x")
        ctk.CTkLabel(calc_frame, text="Calculadora Vectorial", font=ctk.CTkFont(weight="bold")).pack(padx=12, pady=(8, 4), anchor="w")
        ctk.CTkButton(calc_frame, text="∇·F (Divergencia)", command=self._calc_divergence).pack(padx=12, pady=2, fill="x")
        ctk.CTkButton(calc_frame, text="∇×F (Rotacional)", command=self._calc_curl).pack(padx=12, pady=2, fill="x")
        ctk.CTkButton(calc_frame, text="∇f (Gradiente)", command=self._calc_gradient).pack(padx=12, pady=2, fill="x")

    def _limit_entry(self, parent, label, default):
        ctk.CTkLabel(parent, text=label, font=ctk.CTkFont(size=11)).pack(padx=12, pady=(4, 2), anchor="w")
        entry = ctk.CTkEntry(parent, height=30)
        entry.insert(0, default)
        entry.pack(padx=12, pady=(0, 4), fill="x")
        return entry

    def _build_dynamic_inputs(self):
        for widget in self.inputs_frame.winfo_children():
            widget.destroy()

        system = self.system_combo.get()
        integral = self.integral_combo.get()

        if system == SurfaceSystem.CARTESIAN.value:
            ctk.CTkLabel(self.inputs_frame, text="z = f(x,y)", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
            self.entry_func = ctk.CTkEntry(self.inputs_frame, height=32)
            self.entry_func.insert(0, "x**2 + y**2")
            self.entry_func.pack(fill="x", pady=(0, 8))
        elif system == SurfaceSystem.PARAMETRIC.value:
            ctk.CTkLabel(self.inputs_frame, text="x(u,v)", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
            self.entry_x = ctk.CTkEntry(self.inputs_frame, height=32)
            self.entry_x.insert(0, "u")
            self.entry_x.pack(fill="x", pady=(0, 4))

            ctk.CTkLabel(self.inputs_frame, text="y(u,v)").pack(anchor="w")
            self.entry_y = ctk.CTkEntry(self.inputs_frame, height=32)
            self.entry_y.insert(0, "v")
            self.entry_y.pack(fill="x", pady=(0, 4))

            ctk.CTkLabel(self.inputs_frame, text="z(u,v)").pack(anchor="w")
            self.entry_z = ctk.CTkEntry(self.inputs_frame, height=32)
            self.entry_z.insert(0, "u**2 + v**2")
            self.entry_z.pack(fill="x", pady=(0, 8))
        elif system in {SurfaceSystem.POLAR.value, SurfaceSystem.CYLINDRICAL.value}:
            ctk.CTkLabel(self.inputs_frame, text="z = f(r, θ)", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
            self.entry_func = ctk.CTkEntry(self.inputs_frame, height=32)
            self.entry_func.insert(0, "r")
            self.entry_func.pack(fill="x", pady=(0, 8))
        elif system == SurfaceSystem.SPHERICAL.value:
            ctk.CTkLabel(self.inputs_frame, text="ρ = f(φ,θ) o constante", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
            self.entry_func = ctk.CTkEntry(self.inputs_frame, height=32)
            self.entry_func.insert(0, "2")
            self.entry_func.pack(fill="x", pady=(0, 8))

        if integral == "scalar":
            ctk.CTkLabel(self.inputs_frame, text="g(x,y,z) = (función a integrar)", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
            self.entry_scalar = ctk.CTkEntry(self.inputs_frame, height=32)
            self.entry_scalar.insert(0, "1")
            self.entry_scalar.pack(fill="x", pady=(0, 8))
        elif integral == "flux":
            ctk.CTkLabel(self.inputs_frame, text="F = (P, Q, R)", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
            self.entry_flux = ctk.CTkEntry(self.inputs_frame, height=32)
            self.entry_flux.insert(0, "0, 0, 1")
            self.entry_flux.pack(fill="x", pady=(0, 8))

    def _on_system_changed(self, value):
        self._build_dynamic_inputs()

    def _on_resolution_changed(self, value):
        self.resolution_label.configure(text=str(int(value)))

    def _read_model(self) -> IntegralModel:
        system = self.system_combo.get()
        integral = self.integral_combo.get()
        func_expr = None
        x_expr = None
        y_expr = None
        z_expr = None
        scalar_expr = None
        flux_expr = None

        try:
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
        except Exception as e:
            raise ValueError(f"Error al leer parámetros: {e}")

    def _visualize(self):
        try:
            resolution = int(self.resolution_slider.get())
            colormap = self.colormap_combo.get()
            contour_proj = self.contour_projection.get()

            self.model = self._read_model()

            # Usar MatplotlibSurfaceRenderer con opciones avanzadas
            fig = MatplotlibSurfaceRenderer.render(
                self.model.model,
                resolution=resolution,
                show_normals=self.var_show_normals.get(),
                show_flux_field=self.var_show_field.get(),
                normal_scale=0.4,
                flux_scale=0.5,
                alpha=0.85,
                colormap=colormap,
                show_wireframe=self.var_show_wireframe.get(),
                show_axes=self.var_show_axes.get(),
                show_contour=self.var_show_contour.get(),
                contour_projection=contour_proj,
            )
            self._draw_figure(fig)
            
            # Información de opciones activas
            info = f"✅ Superficie visualizada\n"
            info += f"Resolución: {resolution} | Colormap: {colormap}\n"
            opts = []
            if self.var_show_wireframe.get(): opts.append("wireframe")
            if self.var_show_axes.get(): opts.append("ejes")
            if self.var_show_contour.get(): opts.append("contour")
            if self.var_show_normals.get(): opts.append("normales")
            if self.var_show_field.get(): opts.append("campo")
            if opts:
                info += f"Activos: {', '.join(opts)}"
            else:
                info += "Sin opciones adicionales"
            
            self.result_text.delete("0.0", "end")
            self.result_text.insert("0.0", info)
        except Exception as exc:
            self.result_text.delete("0.0", "end")
            self.result_text.insert("0.0", f"❌ Error al visualizar: {exc}\n\nUse Visualizar para reintentar")

    def _calculate(self):
        try:
            self.model = self._read_model()
            integral_type = self.integral_combo.get()

            if integral_type in ["divergence", "curl", "gradient"]:
                self._calculate_vector_operator(integral_type)
            else:
                self.result = IntegralCalculator.calculate(self.model.model, integral_type)
                text = []
                if self.result.get("success"):
                    if self.result.get("exact") is not None:
                        text.append(f"📐 Resultado exacto: {self.result['exact']}")
                    if self.result.get("approximate") is not None:
                        text.append(f"🔢 Resultado numérico: {self.result['approximate']:.6f}")
                    text.append(f"📊 Método: {self.result.get('method', 'N/A')}")
                    text.append("")
                    text.append("📝 Procedimiento:")
                    for step in self.result.get("procedure", []):
                        text.append(f"  • {step}")
                else:
                    text.append(f"❌ Error: {self.result.get('error_message', 'Desconocido')}")
                self.result_text.delete("0.0", "end")
                self.result_text.insert("0.0", "\n".join(text))
        except Exception as exc:
            self.result_text.delete("0.0", "end")
            self.result_text.insert("0.0", f"❌ Error al calcular: {exc}")

    def _calculate_vector_operator(self, operator_type: str):
        field = self.entry_flux.get()
        scalar = self.entry_scalar.get()
        text = []

        try:
            if operator_type == "divergence":
                div = VectorOperator.divergence(field, "cartesian")
                text.append(f"🔴 DIVERGENCIA ∇·F")
                text.append(f"F = ({field})")
                text.append(f"∇·F = {div}")
                text.append("")
                text.append("Interpretación:")
                text.append("  • ∇·F > 0: Fuente (flujo saliente)")
                text.append("  • ∇·F < 0: Sumidero (flujo entrante)")
                text.append("  • ∇·F = 0: Campo solenoidal")

            elif operator_type == "curl":
                curl_x, curl_y, curl_z = VectorOperator.curl(field, "cartesian")
                text.append(f"🔄 ROTACIONAL ∇×F")
                text.append(f"F = ({field})")
                text.append(f"∇×F = ({curl_x}, {curl_y}, {curl_z})")
                text.append("")
                text.append("Interpretación:")
                text.append("  • ∇×F ≠ 0: Campo no conservativo")
                text.append("  • ∇×F = 0: Campo conservativo")

            elif operator_type == "gradient":
                grad_x, grad_y, grad_z = VectorOperator.gradient(scalar, "cartesian")
                text.append(f"🟢 GRADIENTE ∇f")
                text.append(f"f = {scalar}")
                text.append(f"∇f = ({grad_x}, {grad_y}, {grad_z})")
                text.append("")
                text.append("Interpretación:")
                text.append("  • Apunta en dirección de máximo crecimiento")
                text.append("  • Es siempre perpendicular a las superficies de nivel")

            self.result_text.delete("0.0", "end")
            self.result_text.insert("0.0", "\n".join(text))

        except Exception as e:
            self.result_text.delete("0.0", "end")
            self.result_text.insert("0.0", f"❌ Error al calcular {operator_type}: {e}")

    def _calc_divergence(self):
        try:
            field = self.entry_flux.get()
            div = VectorOperator.divergence(field, "cartesian")
            self.result_text.delete("0.0", "end")
            self.result_text.insert("0.0", f"🔴 DIVERGENCIA\n\nF = ({field})\n\n∇·F = {div}")
        except Exception as e:
            self.result_text.delete("0.0", "end")
            self.result_text.insert("0.0", f"❌ Error: {e}")

    def _calc_curl(self):
        try:
            field = self.entry_flux.get()
            curl_x, curl_y, curl_z = VectorOperator.curl(field, "cartesian")
            self.result_text.delete("0.0", "end")
            self.result_text.insert("0.0", f"🔄 ROTACIONAL\n\nF = ({field})\n\n∇×F = ({curl_x}, {curl_y}, {curl_z})")
        except Exception as e:
            self.result_text.delete("0.0", "end")
            self.result_text.insert("0.0", f"❌ Error: {e}")

    def _calc_gradient(self):
        try:
            scalar = self.entry_scalar.get()
            grad_x, grad_y, grad_z = VectorOperator.gradient(scalar, "cartesian")
            self.result_text.delete("0.0", "end")
            self.result_text.insert("0.0", f"🟢 GRADIENTE\n\nf = {scalar}\n\n∇f = ({grad_x}, {grad_y}, {grad_z})")
        except Exception as e:
            self.result_text.delete("0.0", "end")
            self.result_text.insert("0.0", f"❌ Error: {e}")

    def _load_example(self):
        name = self.example_combo.get()
        if not name:
            return

        # Mapeo de ejemplos avanzados
        example_map = {
            "Toro": ("parametric", "2*cos(u)", "2*sin(u)", "v", Limits(0, 6.28, -1, 1)),
            "Hiperboloide": ("parametric", "cosh(u)*cos(v)", "cosh(u)*sin(v)", "sinh(v)", Limits(-1, 1, 0, 6.28)),
            "Cono": ("cylindrical", "v", Limits(0, 1, 0, 6.28)),
            "Casquete": ("spherical", "2", Limits(0, 3.14, 0, 1.57)),
        }

        if name in example_map:
            params = example_map[name]
            if name in ["Toro", "Hiperboloide"]:
                self.system_combo.set("parametric")
                self._build_dynamic_inputs()
                self.entry_x.delete(0, "end")
                self.entry_x.insert(0, params[1])
                self.entry_y.delete(0, "end")
                self.entry_y.insert(0, params[2])
                self.entry_z.delete(0, "end")
                self.entry_z.insert(0, params[3])
                self.entry_u_min.delete(0, "end")
                self.entry_u_min.insert(0, str(params[4].u_min))
                self.entry_u_max.delete(0, "end")
                self.entry_u_max.insert(0, str(params[4].u_max))
                self.entry_v_min.delete(0, "end")
                self.entry_v_min.insert(0, str(params[4].v_min))
                self.entry_v_max.delete(0, "end")
                self.entry_v_max.insert(0, str(params[4].v_max))
            elif name in ["Cono"]:
                self.system_combo.set("cylindrical")
                self._build_dynamic_inputs()
                self.entry_func.delete(0, "end")
                self.entry_func.insert(0, "v")
                self.entry_u_min.delete(0, "end")
                self.entry_u_min.insert(0, str(params[2].u_min))
                self.entry_u_max.delete(0, "end")
                self.entry_u_max.insert(0, str(params[2].u_max))
                self.entry_v_min.delete(0, "end")
                self.entry_v_min.insert(0, str(params[2].v_min))
                self.entry_v_max.delete(0, "end")
                self.entry_v_max.insert(0, str(params[2].v_max))
            elif name == "Casquete":
                self.system_combo.set("spherical")
                self._build_dynamic_inputs()
                self.entry_func.delete(0, "end")
                self.entry_func.insert(0, params[1])
                self.entry_u_min.delete(0, "end")
                self.entry_u_min.insert(0, str(params[2].u_min))
                self.entry_u_max.delete(0, "end")
                self.entry_u_max.insert(0, str(params[2].u_max))
                self.entry_v_min.delete(0, "end")
                self.entry_v_min.insert(0, str(params[2].v_min))
                self.entry_v_max.delete(0, "end")
                self.entry_v_max.insert(0, str(params[2].v_max))

            self.result_text.delete("0.0", "end")
            self.result_text.insert("0.0", f"✅ Ejemplo '{name}' cargado")
            return

        # Ejemplos originales
        model = Examples.load_example(name)
        if model is None:
            return
        self.system_combo.set(model.model.system.value)
        self._build_dynamic_inputs()
        self.model = model
        self.result_text.delete("0.0", "end")
        self.result_text.insert("0.0", f"✅ Ejemplo '{name}' cargado")

    def _export_text(self):
        if self.result is None:
            self.result_text.delete("0.0", "end")
            self.result_text.insert("0.0", "⚠️ No hay resultado para exportar")
            return
        path = ctk.filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text", "*.txt")])
        if path:
            ResultExporter.export_text(self.result, path, "SURFACELAB")
            self.result_text.delete("0.0", "end")
            self.result_text.insert("0.0", f"✅ Exportado a {path}")

    def _export_image(self):
        path = ctk.filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png")])
        if path:
            resolution = int(self.resolution_slider.get())
            fig = MatplotlibSurfaceRenderer.render(self.model.model, resolution=resolution)
            ResultExporter.export_image(fig, path)
            self.result_text.delete("0.0", "end")
            self.result_text.insert("0.0", f"✅ Imagen exportada a {path}")

    def _show_theory(self):
        text = TheoryPanel.get_theory(self.system_combo.get())
        self.result_text.delete("0.0", "end")
        self.result_text.insert("0.0", text + "\n\n" + "="*50 + "\nOPERADORES VECTORIALES\n" + "="*50 + """

DIVERGENCIA (∇·F):
Mide el flujo saliente por unidad de volumen.
∇·F = ∂P/∂x + ∂Q/∂y + ∂R/∂z

ROTACIONAL (∇×F):
Mide la tendencia de F a producir rotación.
∇×F = (∂R/∂y - ∂Q/∂z, ∂P/∂z - ∂R/∂x, ∂Q/∂x - ∂P/∂y)

GRADIENTE (∇f):
Apunta en la dirección de máximo crecimiento de f.
∇f = (∂f/∂x, ∂f/∂y, ∂f/∂z)

LAPLACIANO (∇²f):
∇²f = ∂²f/∂x² + ∂²f/∂y² + ∂²f/∂z²
""")

    def _draw_figure(self, fig):
        self.ax.clear()
        self.figure = fig
        self.canvas.get_tk_widget().destroy()
        self.canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        self.canvas.draw()

    def _toggle_dark_mode(self):
        """Alternar entre modo oscuro y claro."""
        self.dark_mode = not self.dark_mode
        mode = "dark" if self.dark_mode else "light"
        ctk.set_appearance_mode(mode)
        
        self.result_text.delete("0.0", "end")
        self.result_text.insert("0.0", f"Modo {'oscuro' if self.dark_mode else 'claro'} activado (Ctrl+D)")

    def _set_view(self, view_type: str):
        """Establecer vista predefinida."""
        try:
            ax = self.ax
            if view_type == "iso":
                ax.view_init(elev=30, azim=45)
            elif view_type == "top":
                ax.view_init(elev=90, azim=0)
            elif view_type == "front":
                ax.view_init(elev=0, azim=0)
            elif view_type == "side":
                ax.view_init(elev=0, azim=90)
            self.canvas.draw()
            self.result_text.delete("0.0", "end")
            self.result_text.insert("0.0", f"Vista cambiada a: {view_type}")
        except Exception as e:
            self.result_text.delete("0.0", "end")
            self.result_text.insert("0.0", f"Error al cambiar vista: {e}")

    def _copy_to_clipboard(self):
        """Copiar resultado al portapapeles."""
        try:
            text = self.result_text.get("0.0", "end").strip()
            self.clipboard_clear()
            self.clipboard_append(text)
            self.result_text.delete("0.0", "end")
            self.result_text.insert("0.0", "✅ Resultado copiado al portapapeles")
        except Exception as e:
            self.result_text.delete("0.0", "end")
            self.result_text.insert("0.0", f"❌ Error al copiar: {e}")

    def _save_session(self):
        """Guardar sesión actual."""
        try:
            import json
            path = ctk.filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
            if path:
                session_data = {
                    "system": self.system_combo.get(),
                    "integral_type": self.integral_combo.get(),
                    "func_expr": self.entry_func.get() if hasattr(self, 'entry_func') else "",
                    "u_min": self.entry_u_min.get(),
                    "u_max": self.entry_u_max.get(),
                    "v_min": self.entry_v_min.get(),
                    "v_max": self.entry_v_max.get(),
                    "flux_expr": self.entry_flux.get(),
                    "scalar_expr": self.entry_scalar.get(),
                    "resolution": int(self.resolution_slider.get()),
                    "colormap": self.colormap_combo.get(),
                }
                with open(path, "w") as f:
                    json.dump(session_data, f)
                self.result_text.delete("0.0", "end")
                self.result_text.insert("0.0", f"✅ Sesión guardada en {path}")
        except Exception as e:
            self.result_text.delete("0.0", "end")
            self.result_text.insert("0.0", f"❌ Error al guardar: {e}")

    def _load_session(self):
        """Cargar sesión guardada."""
        try:
            import json
            path = ctk.filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
            if path:
                with open(path, "r") as f:
                    session_data = json.load(f)
                
                self.system_combo.set(session_data.get("system", "cartesian"))
                self._build_dynamic_inputs()
                self.integral_combo.set(session_data.get("integral_type", "area"))
                
                if hasattr(self, 'entry_func'):
                    self.entry_func.delete(0, "end")
                    self.entry_func.insert(0, session_data.get("func_expr", ""))
                
                self.entry_u_min.delete(0, "end")
                self.entry_u_min.insert(0, session_data.get("u_min", "-2"))
                self.entry_u_max.delete(0, "end")
                self.entry_u_max.insert(0, session_data.get("u_max", "2"))
                self.entry_v_min.delete(0, "end")
                self.entry_v_min.insert(0, session_data.get("v_min", "-2"))
                self.entry_v_max.delete(0, "end")
                self.entry_v_max.insert(0, session_data.get("v_max", "2"))
                
                self.entry_flux.delete(0, "end")
                self.entry_flux.insert(0, session_data.get("flux_expr", "x, y, z"))
                
                self.resolution_slider.set(session_data.get("resolution", 40))
                self.colormap_combo.set(session_data.get("colormap", "viridis"))
                
                self.result_text.delete("0.0", "end")
                self.result_text.insert("0.0", f"✅ Sesión cargada desde {path}")
        except Exception as e:
            self.result_text.delete("0.0", "end")
            self.result_text.insert("0.0", f"❌ Error al cargar: {e}")

    def _detect_singularities(self):
        """Detectar singularidades en la superficie."""
        try:
            if self.model is None:
                self.model = self._read_model()
            
            from surfacelab.visualization.surface_plot import SurfaceAnalyzer
            result = SurfaceAnalyzer.detect_singularities(self.model.model, resolution=30)
            
            msg = f"🔍 DETECCIÓN DE SINGULARIDADES\n\n"
            if result.get("has_singularities"):
                msg += f"⚠️ {result.get('message')}\n\n"
                if result.get("singular_points"):
                    msg += "Puntos singulares:\n"
                    for i, pt in enumerate(result["singular_points"][:5]):
                        msg += f"  {i+1}. ({pt[0]:.3f}, {pt[1]:.3f}, {pt[2]:.3f})\n"
            else:
                msg += f"✅ {result.get('message', 'No se detectaron problemas')}"
            
            self.result_text.delete("0.0", "end")
            self.result_text.insert("0.0", msg)
        except Exception as e:
            self.result_text.delete("0.0", "end")
            self.result_text.insert("0.0", f"❌ Error: {e}")

    def _calculate_curvature(self):
        """Calcular curvatura de la superficie."""
        try:
            if self.model is None:
                self.model = self._read_model()
            
            from surfacelab.visualization.surface_plot import SurfaceAnalyzer
            result = SurfaceAnalyzer.calculate_curvature(self.model.model)
            
            msg = "📐 CURVATURA DE SUPERFICIE\n\n"
            if "error" in result:
                msg += f"❌ {result['error']}"
            else:
                msg += f"Curvatura Gaussiana K = {result.get('gaussian_curvature', 'N/A')}\n\n"
                msg += f"Curvatura Media H = {result.get('mean_curvature', 'N/A')}\n\n"
                msg += "Primera forma fundamental:\n"
                msg += f"  E = {result.get('E', 'N/A')}\n"
                msg += f"  F = {result.get('F', 'N/A')}\n"
                msg += f"  G = {result.get('G', 'N/A')}\n\n"
                msg += "Segunda forma fundamental:\n"
                msg += f"  L = {result.get('L', 'N/A')}\n"
                msg += f"  M = {result.get('M', 'N/A')}\n"
                msg += f"  N = {result.get('N', 'N/A')}\n"
            
            self.result_text.delete("0.0", "end")
            self.result_text.insert("0.0", msg)
        except Exception as e:
            self.result_text.delete("0.0", "end")
            self.result_text.insert("0.0", f"❌ Error: {e}")


def main():
    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    main()