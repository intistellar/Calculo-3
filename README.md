# SURFACELAB

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Activo-success.svg)

**Calculadora y visualizador de integrales de superficie + Cálculo Vectorial para Cálculo III**

*Ahora con Divergencia, Rotacional, Gradiente y visualizaciones 3D avanzadas*

</div>

---

## 📋 Descripción

SURFACELAB es una herramienta educativa interactiva diseñada para el cálculo y visualización de integrales de superficie y operadores de cálculo vectorial en tres dimensiones. Permite a estudiantes de ingeniería y matemáticas explorar conceptos de cálculo multivariable mediante una interfaz gráfica intuitiva.

### ✨ Características

- 🧮 **5 Sistemas de coordenadas**: Cartesiano, Paramétrico, Polar, Cilíndrico y Esférico
- 📊 **3+ tipos de cálculos**: Área, Integrales escalares, Flujo vectorial
- 🌀 **Operadores Vectoriales**:
  - **Divergencia (∇·F)**: Calcula flujo saliente
  - **Rotacional (∇×F)**: Calcula tendencia a rotar
  - **Gradiente (∇f)**: Calcula dirección de máximo crecimiento
  - **Laplaciano (∇²f)**: Segunda derivada
- 📈 **Visualización 3D** interactiva con matplotlib
- 🎨 **Visualizaciones vectoriales**: Muestra campos, normales, rotacional, gradiente
- 📝 **Procedimiento paso a paso** con simplificación simbólica
- 📤 **Exportación** (texto, imagen, PDF, HTML, LaTeX)
- 📚 **Panel de teoría** con fórmulas completas
- 💡 **15+ ejemplos** incluyendo Toro, Hiperboloide, Cono, Casquete

---

## 🛠️ Instalación

### Requisitos previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Pasos de instalación

```bash
# Clonar el repositorio
git clone https://github.com/intistellar/Calculo-3.git
cd Calculo-3

# Crear y activar entorno virtual (opcional pero recomendado)
python -m venv .venv
.venv\Scripts\activate  # En Windows

# Instalar dependencias
pip install -r requirements.txt

# Instalar dependencias opcionales (para PDF)
pip install reportlab
```

### Dependencias

```
customtkinter>=5.2.2   # Interfaz gráfica moderna
numpy>=1.26            # Cálculos numéricos
scipy>=1.11            # Integración numérica
sympy>=1.12            # Cálculo simbólico
matplotlib>=3.8        # Visualización 3D
pillow>=10.0           # Procesamiento de imágenes
reportlab>=4.0         # Exportación a PDF (opcional)
```

---

## 🚀 Uso

### Ejecutar la aplicación

```bash
python -m surfacelab.main
```

### Atajos de teclado

| Atajo | Acción |
|-------|--------|
| `Ctrl+R` | Visualizar superficie |
| `Ctrl+C` | Calcular integral |
| `Ctrl+E` | Exportar texto |
| `Ctrl+T` | Mostrar teoría |
| `Ctrl+D` | Cambiar modo oscuro/claro |

### Flujo de trabajo básico

1. **Seleccionar sistema** de coordenadas (Cartesiano, Paramétrico, etc.)
2. **Elegir tipo de cálculo** (area, scalar, flux, divergence, curl, gradient)
3. **Ingresar la función** de la superficie según el sistema
4. **Ingresar campo vectorial F = (P, Q, R)** o campo escalar f(x,y,z)
5. **Definir límites** de integración para u y v
6. **Clic en "🎨 Visualizar"** para ver la superficie en 3D
7. **Clic en "🧮 Calcular"** para obtener el resultado
8. **Usar checkboxes** para ver normales, campo F, rotacional, gradiente

### Calculadora vectorial rápida

Usa los botones en la barra lateral:
- **∇·F (Divergencia)**: Calcula divergencia del campo
- **∇×F (Rotacional)**: Calcula rotacional del campo  
- **∇f (Gradiente)**: Calcula gradiente del campo escalar

### Ejemplos incluidos

**Básicos:**
- Paraboloide circular z = x² + y²
- Plano z = 2x + 3y
- Cilindro paramétrico
- Esfera de radio constante
- Superficies en coordenadas polares

**Avanzados (nuevo):**
- **Toro** - Donut paramétrico
- **Hiperboloide** - Una y dos hojas
- **Cono** - Coordenadas cilíndricas
- **Casquete** - Esfera parcial

---

## 📁 Estructura del proyecto

```
surfacelab/
├── main.py                      # Punto de entrada
├── ui/
│   └── main_window.py          # GUI con checkboxes, slider, examples
├── core/
│   ├── surface.py              # Clases base de superficies
│   ├── parametrization.py      # Parametrización de superficies
│   ├── differential.py         # Operadores diferenciales
│   ├── normals.py              # Cálculo de normales
│   ├── vector_calculus.py      # NUEVO: Divergencia, Rotacional, Gradiente
│   └── validation.py           # Validación de entradas
├── calculators/
│   ├── surface_area.py         # Calculadora de área
│   ├── scalar_surface_integral.py
│   ├── flux_integral.py        # Calculadora de flujo
│   ├── coordinate_calculators.py
│   ├── procedure_builder.py    # Generador de pasos
│   └── cache.py                # NUEVO: Sistema de caché
├── visualization/
│   ├── surface_plot.py         # Renderizado 3D + cálculo vectorial
│   ├── vector_plot.py          # Visualización de campos
│   └── vector_field_plot.py    # NUEVO: Visualizador de campos 3D
├── models/
│   ├── surface_model.py        # Modelo de superficie
│   ├── integral_model.py       # Modelo de integral
│   ├── parameter_model.py      # Parámetros de visualización
│   ├── examples.py             # 15+ ejemplos
│   └── comparison.py           # Comparación de resultados
├── utils/
│   ├── parser.py               # Parsing de expresiones
│   ├── export.py               # Exportación de resultados
│   ├── export_advanced.py      # NUEVO: PDF, HTML, LaTeX
│   ├── theory.py               # Teoría + operadores vectoriales
│   └── validation.py           # NUEVO: Validación en tiempo real
└── tests/
    ├── test_phase*.py          # Tests por fase
    └── test_vector_calculus.py # NUEVO: Tests de cálculo vectorial
```

---

## 🧪 Pruebas

Ejecutar todos los tests:

```bash
python -m unittest discover -s surfacelab/tests -v
```

Tests específicos:

```bash
# Tests de cálculo vectorial
python -m unittest surfacelab.tests.test_vector_calculus -v

# Tests de fase específica
python -m unittest surfacelab.tests.test_phase8_flux -v
```

---

## 📖 Teoría

### Operadores Vectoriales

La aplicación ahora incluye calculadora de:

**DIVERGENCIA (∇·F)**
```
∇·F = ∂P/∂x + ∂Q/∂y + ∂R/∂z
```
- Mide el flujo saliente por unidad de volumen
- ∇·F > 0: Fuente (fluye hacia afuera)
- ∇·F < 0: Sumidero (fluye hacia adentro)
- ∇·F = 0: Campo solenoidal

**ROTACIONAL (∇×F)**
```
∇×F = |i    j    k   |
      |∂/∂x ∂/∂y ∂/∂z|
      |P    Q    R   |
```
- Mide la tendencia del campo a producir rotación
- ∇×F ≠ 0: Campo no conservativo
- ∇×F = 0: Campo conservativo (existe potencial)

**GRADIENTE (∇f)**
```
∇f = (∂f/∂x, ∂f/∂y, ∂f/∂z)
```
- Apunta en la dirección de máximo crecimiento
- Es perpendicular a las superficies de nivel

### Integrales de Superficie

```
A = ∬_S dS = ∬_D |r_u × r_v| du dv

∬_S f dS = ∬_D f(r(u,v)) |r_u × r_v| du dv

Φ = ∬_S F · n dS = ∬_D F(r(u,v)) · (r_u × r_v) du dv
```

---

## 🎯 Fases de desarrollo

| Fase | Descripción | Estado |
|------|-------------|--------|
| 1 | Smoke test y configuración básica | ✅ |
| 2 | Motor matemático core | ✅ |
| 3 | Sistema Cartesiano | ✅ |
| 4 | Sistema Paramétrico | ✅ |
| 5 | Sistema Polar | ✅ |
| 6 | Sistema Cilíndrico | ✅ |
| 7 | Sistema Esférico | ✅ |
| 8 | Cálculo de flujo | ✅ |
| 9 | Generación de procedimiento | ✅ |
| 10 | Ejemplos predefinidos | ✅ |
| 11 | Comparación de resultados | ✅ |
| 12 | Exportación de resultados | ✅ |
| 13 | Panel de teoría y documentación | ✅ |
| 14 | **Cálculo vectorial (∇·, ∇×, ∇)** | ✅ |
| 15 | **Visualización de campos 3D** | ✅ |
| 16 | **UI mejorada (checkboxes, slider)** | ✅ |
| 17 | **Validación en tiempo real** | ✅ |
| 18 | **Exportación avanzada (PDF/HTML)** | ✅ |
| 19 | **Caching de cálculos** | ✅ |
| 20 | **Modo claro/oscuro + atajos** | ✅ |

---

## 🆕 Novedades v2.0

- ✅ Calculadora de divergencia, rotacional y gradiente
- ✅ Visualización de campos vectoriales en 3D
- ✅ Checkboxes para mostrar normales, campo F, rotacional, gradiente
- ✅ Slider de resolución (10-80)
- ✅ Selector de colormap (viridis, plasma, magma, etc.)
- ✅ 4 ejemplos nuevos (Toro, Hiperboloide, Cono, Casquete)
- ✅ Validación de expresiones en tiempo real
- ✅ Exportación a PDF, HTML, LaTeX
- ✅ Sistema de caché para cálculos
- ✅ Modo oscuro/claro con atajos de teclado

---

## 🤝 Contribuciones

Este proyecto es parte del curso de Cálculo III. Las contribuciones son bienvenidas.

1. Fork el repositorio
2. Crea una rama (`git checkout -b feature/nueva-funcionalidad`)
3. Haz tus cambios y commitea (`git commit -m 'Add feature'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

---

## 📄 Licencia

Distribuido bajo la licencia MIT.

---

## 👤 Autor

**intistellar**  
GitHub: [@intistellar](https://github.com/intistellar)  
Email: intistellar@users.noreply.github.com

---

<div align="center">

**¡Gracias por usar SURFACELAB!**  
*Ahora con Cálculo Vectorial completo* 🌀

</div>