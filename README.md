# SURFACELAB

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Completado-success.svg)

**Calculadora y visualizador de integrales de superficie para Cálculo III**

</div>

---

## 📋 Descripción

SURFACELAB es una herramienta educativa interactiva diseñada para el cálculo y visualización de integrales de superficie en tres dimensiones. Permite a estudiantes de ingeniería y matemáticas explorar conceptos de cálculo vectorial mediante una interfaz gráfica intuitiva y resultados numéricos exactos.

### ✨ Características

- 🧮 **5 Sistemas de coordenadas**: Cartesiano, Paramétrico, Polar, Cilíndrico y Esférico
- 📊 **3 tipos de integrales**: Área de superficie, Integrales escalares, Flujo vectorial
- 📈 **Visualización 3D** interactiva con matplotlib
- 📝 **Procedimiento paso a paso** con simplificación simbólica
- 📤 **Exportación** de resultados (texto e imagen)
- 📚 **Panel de teoría** con fórmulas y conceptos clave
- 💡 **Ejemplos predefinidos** para practicar

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
```

### Dependencias

```
customtkinter>=5.2.2   # Interfaz gráfica moderna
numpy>=1.26            # Cálculos numéricos
scipy>=1.11            # Integración numérica
sympy>=1.12            # Cálculo simbólico
matplotlib>=3.8        # Visualización 3D
pillow>=10.0           # Procesamiento de imágenes
```

---

## 🚀 Uso

### Ejecutar la aplicación

```bash
python -m surfacelab.main
```

### Flujo de trabajo básico

1. **Seleccionar sistema** de coordenadas (Cartesiano, Paramétrico, etc.)
2. **Elegir tipo de integral** (area, scalar, flux)
3. **Ingresar la función** de la superficie según el sistema
4. **Definir límites** de integración para u y v
5. **Clic en "Visualizar"** para ver la superficie en 3D
6. **Clic en "Calcular"** para obtener el resultado exacto y numérico
7. **Ver procedimiento** paso a paso en el panel de resultados

### Ejemplos incluidos

- Paraboloide circular z = x² + y²
- Plano z = 2x + 3y
- Cilindro paramétrico
- Esfera de radio constante
- Superficies definidas en coordenadas polares

---

## 📁 Estructura del proyecto

```
surfacelab/
├── main.py                      # Punto de entrada de la aplicación
├── ui/
│   └── main_window.py          # Ventana principal con GUI
├── core/
│   ├── surface.py              # Clases base de superficies
│   ├── parametrization.py      # Parametrización de superficies
│   ├── differential.py         # Operadores diferenciales
│   ├── normals.py              # Cálculo de normales
│   └── validation.py           # Validación de entradas
├── calculators/
│   ├── surface_area.py         # Calculadora de área
│   ├── scalar_surface_integral.py
│   ├── flux_integral.py        # Calculadora de flujo
│   ├── coordinate_calculators.py
│   └── procedure_builder.py    # Generador de pasos
├── visualization/
│   ├── surface_plot.py         # Renderizado 3D
│   └── vector_plot.py          # Visualización de campos
├── models/
│   ├── surface_model.py        # Modelo de superficie
│   ├── integral_model.py       # Modelo de integral
│   ├── parameter_model.py      # Parámetros de visualización
│   ├── examples.py             # Ejemplos predefinidos
│   └── comparison.py           # Comparación de resultados
├── utils/
│   ├── parser.py               # Parsing de expresiones
│   ├── export.py               # Exportación de resultados
│   └── theory.py               # Contenido teórico
└── tests/
    ├── test_phase1_smoke.py
    ├── test_phase2_engine.py
    ├── test_phase3_cartesian.py
    ├── test_phase4_parametric.py
    ├── test_phase5_polar.py
    ├── test_phase6_cylindrical.py
    ├── test_phase7_spherical.py
    ├── test_phase8_flux.py
    ├── test_phase9_procedure.py
    ├── test_phase10_examples.py
    ├── test_phase11_comparison.py
    └── test_phase12_export.py
```

---

## 🧪 Pruebas

Ejecutar todos los tests:

```bash
python -m unittest discover -s surfacelab/tests -v
```

Tests por fase (ejemplo):

```bash
python -m unittest surfacelab.tests.test_phase3_cartesian -v
python -m unittest surfacelab.tests.test_phase8_flux -v
```

---

## 📖 Teoría

La aplicación cubre los siguientes conceptos de Cálculo Vectorial:

### Integral de Superficie (Área)
```
A = ∬_S dS = ∬_D |r_u × r_v| du dv
```

### Integral Escalar de Superficie
```
∬_S f(x,y,z) dS
```

### Flujo de un campo vectorial
```
Φ = ∬_S F · n dS = ∬_D F(r(u,v)) · (r_u × r_v) du dv
```

Presiona el botón **"Teoría"** en la interfaz para ver fórmulas detalladas por sistema de coordenadas.

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

Distribuido bajo la licencia MIT. Ver `LICENSE` para más información.

---

## 👤 Autor

**intistellar**  
GitHub: [@intistellar](https://github.com/intistellar)  
Email: intistellar@users.noreply.github.com

---

<div align="center">

**¡Gracias por usar SURFACELAB!**

</div>