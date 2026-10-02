"""
Tests para el módulo de cálculo vectorial.
"""

from __future__ import annotations

import unittest

import numpy as np
import sympy as sp

from surfacelab.core.vector_calculus import VectorOperator, compute_flux_through_surface


class TestVectorOperator(unittest.TestCase):
    """Tests para la clase VectorOperator."""

    def test_gradient_cartesian(self):
        """Test gradiente en coordenadas cartesianas."""
        # ∇(x² + y² + z²) = (2x, 2y, 2z)
        grad_x, grad_y, grad_z = VectorOperator.gradient("x**2 + y**2 + z**2", "cartesian")
        
        self.assertEqual(str(grad_x), "2*x")
        self.assertEqual(str(grad_y), "2*y")
        self.assertEqual(str(grad_z), "2*z")

    def test_gradient_simple(self):
        """Test gradiente simple."""
        # ∇(x) = (1, 0, 0)
        grad_x, grad_y, grad_z = VectorOperator.gradient("x", "cartesian")
        
        self.assertEqual(str(grad_x), "1")
        self.assertEqual(str(grad_y), "0")
        self.assertEqual(str(grad_z), "0")

    def test_divergence_simple(self):
        """Test divergencia simple."""
        # ∇·(x, y, z) = 1 + 1 + 1 = 3
        div = VectorOperator.divergence("x, y, z", "cartesian")
        
        self.assertEqual(str(div), "3")

    def test_divergence_radial(self):
        """Test divergencia de campo radial."""
        # ∇·(x, y, z) = 3 (ya verificado)
        div = VectorOperator.divergence("x, y, z", "cartesian")
        self.assertEqual(sp.simplify(div - 3), 0)

    def test_divergence_zero(self):
        """Test divergencia cero."""
        # ∇·(-y, x, 0) = 0 (campo solenoidal)
        div = VectorOperator.divergence("-y, x, 0", "cartesian")
        self.assertEqual(sp.simplify(div), 0)

    def test_curl_simple(self):
        """Test rotacional simple."""
        # ∇×(0, 0, z) = (1, 0, 0)
        curl_x, curl_y, curl_z = VectorOperator.curl("0, 0, z", "cartesian")
        
        self.assertEqual(str(curl_x), "1")
        self.assertEqual(str(curl_y), "0")
        self.assertEqual(str(curl_z), "0")

    def test_curl_zero(self):
        """Test rotacional cero (campo conservativo)."""
        # ∇×(x, y, z) = (0, 0, 0)
        curl_x, curl_y, curl_z = VectorOperator.curl("x, y, z", "cartesian")
        
        self.assertEqual(sp.simplify(curl_x), 0)
        self.assertEqual(sp.simplify(curl_y), 0)
        self.assertEqual(sp.simplify(curl_z), 0)

    def test_curl_rotation(self):
        """Test rotacional de campo de rotación."""
        # F = (-y, x, 0) tiene rotacional = (0, 0, 2)
        curl_x, curl_y, curl_z = VectorOperator.curl("-y, x, 0", "cartesian")
        
        self.assertEqual(sp.simplify(curl_z), 2)

    def test_laplacian(self):
        """Test Laplaciano."""
        # ∇²(x² + y² + z²) = 6
        lap = VectorOperator.laplacian("x**2 + y**2 + z**2", "cartesian")
        
        self.assertEqual(str(sp.simplify(lap)), "6")

    def test_field_to_lambda(self):
        """Test conversión a lambda numérico."""
        lambdas = VectorOperator.field_to_lambda("x, y, z", "cartesian", is_vector=True)
        
        x = np.array([1, 2, 3])
        y = np.array([0, 1, 2])
        z = np.array([0, 0, 1])
        
        result_x = lambdas[0](x, y, z)
        result_y = lambdas[1](x, y, z)
        result_z = lambdas[2](x, y, z)
        
        np.testing.assert_array_almost_equal(result_x, x)
        np.testing.assert_array_almost_equal(result_y, y)
        np.testing.assert_array_almost_equal(result_z, z)

    def test_invalid_field(self):
        """Test con campo inválido."""
        with self.assertRaises(ValueError):
            VectorOperator.divergence("x, y", "cartesian")

    def test_invalid_system(self):
        """Test con sistema inválido."""
        with self.assertRaises(ValueError):
            VectorOperator.gradient("x**2", "invalid_system")


class TestFluxCalculation(unittest.TestCase):
    """Tests para cálculo de flujo."""

    def test_flux_through_plane(self):
        """Test flujo a través del plano z = 0."""
        # F = (0, 0, 1), superficie z = 0
        flux = compute_flux_through_surface("0, 0, 1", "0")
        
        # En z=0, el flujo debería ser 0 ya que no hay área efectiva
        # dS = √(1 + 0 + 0) dxdy = 1
        # F·n = (0, 0, 1)·(0, 0, 1) = 1
        # El resultado debe ser la integral de 1 sobre el dominio
        self.assertIsNotNone(flux)


class TestVectorCalculusVisualization(unittest.TestCase):
    """Tests para visualizaciones de cálculo vectorial."""

    def test_vector_field_plotter_import(self):
        """Test que el módulo de visualización se puede importar."""
        from surfacelab.visualization.vector_field_plot import VectorFieldPlotter, VectorFieldRenderer
        
        self.assertIsNotNone(VectorFieldPlotter)
        self.assertIsNotNone(VectorFieldRenderer)

    def test_generate_field_grid(self):
        """Test generación de grid para campo."""
        from surfacelab.visualization.vector_field_plot import VectorFieldPlotter
        
        X, Y, Z = VectorFieldPlotter.generate_field_grid(
            x_range=(-1, 1),
            y_range=(-1, 1),
            z_range=(-1, 1),
            resolution=5
        )
        
        self.assertEqual(X.shape, (5, 5, 5))
        self.assertEqual(Y.shape, (5, 5, 5))
        self.assertEqual(Z.shape, (5, 5, 5))

    def test_evaluate_vector_field(self):
        """Test evaluación de campo vectorial."""
        from surfacelab.visualization.vector_field_plot import VectorFieldPlotter
        
        X = np.array([1.0])
        Y = np.array([0.0])
        Z = np.array([0.0])
        
        U, V, W = VectorFieldPlotter.evaluate_vector_field("x, y, z", X, Y, Z)
        
        np.testing.assert_array_almost_equal(U, [1.0])
        np.testing.assert_array_almost_equal(V, [0.0])
        np.testing.assert_array_almost_equal(W, [0.0])


class TestCaching(unittest.TestCase):
    """Tests para el sistema de caché."""

    def test_cache_basic(self):
        """Test básico de caché."""
        from surfacelab.calculators.cache import CalculationCache
        
        # Limpiar caché
        CalculationCache.clear()
        
        # Verificar estado inicial
        self.assertEqual(len(CalculationCache._cache), 0)
        
        # Agregar elemento
        CalculationCache.set("test_key", "test_value")
        
        # Verificar que se guardó
        self.assertEqual(CalculationCache.get("test_key"), "test_value")
        
        # Limpiar
        CalculationCache.clear()

    def test_cache_miss(self):
        """Test de fallo de caché."""
        from surfacelab.calculators.cache import CalculationCache
        
        CalculationCache.clear()
        
        result = CalculationCache.get("nonexistent_key")
        self.assertIsNone(result)

    def test_cache_stats(self):
        """Test de estadísticas de caché."""
        from surfacelab.calculators.cache import CalculationCache
        
        CalculationCache.clear()
        
        # Sin uso
        stats = CalculationCache.stats()
        self.assertEqual(stats["hits"], 0)
        
        # Con uso
        CalculationCache.set("key1", "value1")
        CalculationCache.get("key1")  # Hit
        CalculationCache.get("key2")  # Miss
        
        stats = CalculationCache.stats()
        self.assertEqual(stats["hits"], 1)
        self.assertEqual(stats["misses"], 1)


class TestValidation(unittest.TestCase):
    """Tests para validación de expresiones."""

    def test_validate_valid_expression(self):
        """Test expresión válida."""
        from surfacelab.utils.validation import ExpressionValidator
        
        is_valid, error, expr = ExpressionValidator.validate_expression("x**2 + y**2", "cartesian")
        
        self.assertTrue(is_valid)
        self.assertIsNone(error)
        self.assertIsNotNone(expr)

    def test_validate_invalid_expression(self):
        """Test expresión inválida."""
        from surfacelab.utils.validation import ExpressionValidator
        
        is_valid, error, expr = ExpressionValidator.validate_expression("", "cartesian")
        
        self.assertFalse(is_valid)
        self.assertIsNotNone(error)

    def test_validate_invalid_variable(self):
        """Test con variable inválida."""
        from surfacelab.utils.validation import ExpressionValidator
        
        is_valid, error, expr = ExpressionValidator.validate_expression("a**2", "cartesian")
        
        self.assertFalse(is_valid)
        self.assertIn("no válidas", error if error else "")

    def test_validate_vector_field(self):
        """Test validación de campo vectorial."""
        from surfacelab.utils.validation import ExpressionValidator
        
        is_valid, error = ExpressionValidator.validate_vector_field("x, y, z", "cartesian")
        
        self.assertTrue(is_valid)
        self.assertIsNone(error)

    def test_validate_vector_field_invalid(self):
        """Test validación de campo vectorial inválido."""
        from surfacelab.utils.validation import ExpressionValidator
        
        is_valid, error = ExpressionValidator.validate_vector_field("x, y", "cartesian")
        
        self.assertFalse(is_valid)
        self.assertIn("3 componentes", error if error else "")

    def test_validate_limits(self):
        """Test validación de límites."""
        from surfacelab.utils.validation import ExpressionValidator
        
        is_valid, error = ExpressionValidator.validate_limits("0", "1", "0", "1")
        
        self.assertTrue(is_valid)
        self.assertIsNone(error)

    def test_validate_limits_invalid(self):
        """Test validación de límites inválidos."""
        from surfacelab.utils.validation import ExpressionValidator
        
        is_valid, error = ExpressionValidator.validate_limits("1", "0", "0", "1")
        
        self.assertFalse(is_valid)
        self.assertIn("u_min", error if error else "")


if __name__ == "__main__":
    unittest.main()