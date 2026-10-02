# SURFACELAB

Calculadora y visualizador de integrales de superficie en Python.

## Estado actual

Fases 1-13 completadas: motor matemático, 5 sistemas de coordenadas, visualización 3D, flujo, ejemplos, comparación, exportación, teoría y pruebas.

## Estructura

```
surfacelab/
  main.py
  ui/
    main_window.py
  core/
    surface.py
    parametrization.py
    differential.py
    normals.py
    validation.py
  calculators/
    surface_area.py
    scalar_surface_integral.py
    flux_integral.py
    coordinate_calculators.py
    procedure_builder.py
  visualization/
    surface_plot.py
    vector_plot.py
  models/
    surface_model.py
    integral_model.py
    parameter_model.py
    examples.py
    comparison.py
  utils/
    parser.py
    export.py
    theory.py
  tests/
    test_phase1_smoke.py
    test_phase2_engine.py
    test_phase3_cartesian.py
    test_phase4_parametric.py
    test_phase5_polar.py
    test_phase6_cylindrical.py
    test_phase7_spherical.py
    test_phase8_flux.py
    test_phase9_procedure.py
    test_phase10_examples.py
    test_phase11_comparison.py
    test_phase12_export.py
```

## Ejecución

```bash
python -m surfacelab.main
```

## Pruebas

```bash
python -m unittest discover -s surfacelab/tests -v
```

## Requisitos

```bash
pip install -r requirements.txt
```
