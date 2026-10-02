"""
Módulo de validación en tiempo real y feedback visual para SURFACELAB.
"""

from __future__ import annotations

import re
from typing import Optional, Tuple

import sympy as sp


class ExpressionValidator:
    """Validador de expresiones matemáticas en tiempo real."""

    # Variables válidas por sistema de coordenadas
    VALID_VARIABLES = {
        "cartesian": ["x", "y", "z"],
        "parametric": ["u", "v"],
        "polar": ["r", "theta"],
        "cylindrical": ["r", "theta", "z"],
        "spherical": ["rho", "theta", "phi", "ρ", "θ", "φ"],
    }

    # Funciones matemáticas válidas
    VALID_FUNCTIONS = [
        "sin", "cos", "tan", "cot", "sec", "csc",
        "asin", "acos", "atan", "acot", "asec", "acsc",
        "sinh", "cosh", "tanh", "asinh", "acosh", "atanh",
        "sqrt", "cbrt", "exp", "log", "ln", "log10", "log2",
        "abs", "sign", "floor", "ceil",
        "pi", "e", "E",
    ]

    # Constantes y operadores
    VALID_CONSTANTS = ["pi", "e", "E", "I"]
    VALID_OPERATORS = ["+", "-", "*", "/", "**", "^", "(", ")"]

    @classmethod
    def validate_expression(
        cls,
        expr: str,
        system: str = "cartesian",
    ) -> Tuple[bool, Optional[str], Optional[sp.Expr]]:
        """
        Validar una expresión matemática.
        
        Returns:
            (is_valid, error_message, parsed_expression)
        """
        if not expr or not expr.strip():
            return False, "Expresión vacía", None

        expr = expr.strip()

        # Obtener variables válidas
        valid_vars = cls.VALID_VARIABLES.get(system.lower(), cls.VALID_VARIABLES["cartesian"])
        all_valid = valid_vars + cls.VALID_FUNCTIONS + cls.VALID_CONSTANTS

        # Crear diccionario local para parsing
        local_dict = {}
        for var in valid_vars:
            local_dict[var] = sp.Symbol(var)
        for func in cls.VALID_FUNCTIONS:
            local_dict[func] = getattr(sp, func, None)

        try:
            parsed = sp.parse_expr(expr, local_dict=local_dict, transformations="all")

            # Verificar que solo tenga variables válidas
            free_symbols = {str(s) for s in parsed.free_symbols}
            invalid_vars = free_symbols - set(all_valid)

            if invalid_vars:
                return False, f"Variables no válidas: {invalid_vars}", None

            # Simplificar para verificar que es válida
            simplified = sp.simplify(parsed)
            return True, None, simplified

        except sp.SympifyError as e:
            return False, f"Error de sintaxis: {str(e)[:50]}", None
        except Exception as e:
            return False, f"Error: {str(e)[:50]}", None

    @classmethod
    def validate_vector_field(
        cls,
        field_expr: str,
        system: str = "cartesian",
    ) -> Tuple[bool, Optional[str]]:
        """Validar expresión de campo vectorial (3 componentes)."""
        if not field_expr or not field_expr.strip():
            return False, "Campo vectorial vacío"

        components = [c.strip() for c in field_expr.split(",")]
        if len(components) != 3:
            return False, f"Debe tener 3 componentes, tiene {len(components)}"

        for i, comp in enumerate(components):
            is_valid, error, _ = cls.validate_expression(comp, system)
            if not is_valid:
                return False, f"Componente {i+1}: {error}"

        return True, None

    @classmethod
    def validate_limits(
        cls,
        u_min: str,
        u_max: str,
        v_min: str,
        v_max: str,
    ) -> Tuple[bool, Optional[str]]:
        """Validar límites de integración."""
        try:
            um, uM = float(u_min), float(u_max)
            vm, vM = float(v_min), float(v_max)

            if um >= uM:
                return False, "u_min debe ser menor que u_max"
            if vm >= vM:
                return False, "v_min debe ser menor que v_max"

            return True, None
        except ValueError:
            return False, "Los límites deben ser números válidos"

    @classmethod
    def suggest_correction(cls, expr: str) -> Optional[str]:
        """Sugerir corrección para expresiones comunes con errores."""
        # Corregir乘法
        if ".." in expr:
            expr = expr.replace("..", "**")

        # Corregir multiplication implícita
        expr = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', expr)
        expr = re.sub(r'([a-zA-Z])(\d)', r'\1*\2', expr)
        expr = re.sub(r'([a-zA-Z])\(', r'\1*(', expr)

        # Corregir nombres de funciones comunes
        replacements = {
            "sen": "sin",
            "tg": "tan",
            "ctg": "cot",
            "log10": "log10",
            "ln": "log",
            "π": "pi",
        }
        for old, new in replacements.items():
            if old in expr.lower():
                expr = expr.replace(old, new).replace(old.upper(), new)

        return expr if expr != "" else None


class FeedbackManager:
    """Gestor de feedback visual para la interfaz."""

    @staticmethod
    def get_error_color(validation_error: bool) -> str:
        """Obtener color para estado de validación."""
        return "#FF6B6B" if validation_error else "#4ECDC4"

    @staticmethod
    def format_result_display(result: dict) -> str:
        """Formatear resultado para mostrar en la UI."""
        if not result.get("success"):
            return f"❌ Error: {result.get('error_message', 'Desconocido')}"

        lines = []
        if result.get("exact") is not None:
            lines.append(f"📐 Exact: {result['exact']}")
        if result.get("approximate") is not None:
            lines.append(f"🔢 Numérico: {result['approximate']:.6f}")
        if result.get("method"):
            lines.append(f"📊 Método: {result['method']}")

        return "\n".join(lines)

    @staticmethod
    def get_operator_explanation(operator: str, value: str) -> str:
        """Obtener explicación pedagógica de operadores."""
        explanations = {
            "divergence": """
DIVERGENCIA (∇·F)
• Mide el flujo saliente por unidad de volumen
• Si ∇·F > 0: El campo tiene fuentes (fluye hacia afuera)
• Si ∇·F < 0: El campo tiene sumideros (fluye hacia adentro)
• Si ∇·F = 0: Campo solenoidal (sin fuentes ni sumideros)
• Interpretación física: Tasa de expansión/compresión del campo
""",
            "curl": """
ROTACIONAL (∇×F)
• Mide la tendencia del campo a producir rotación
• Si ∇×F ≠ 0: Campo no conservativo (no se puede expresar como gradiente)
• Si ∇×F = 0: Campo conservativo (existe potencial)
• La dirección del rotacional indica el eje de rotación
• Interpretación física: Torque por unidad de área
""",
            "gradient": """
GRADIENTE (∇f)
• Apunta en la dirección de máximo crecimiento de f
• Es siempre perpendicular a las superficies de nivel
• Su magnitud indica la pendiente máxima
• Es un campo vectorial siempre conservativo
• Relacionado con la derivada direccional máxima
""",
            "laplacian": """
LAPLACIANO (∇²f)
• Es la divergencia del gradiente: ∇²f = ∇·∇f
• En física: describe difusión, conducción de calor, potencial
• ∇²f = 0 significa función armónica
• Relacionado con la curvatura promedio de la superficie
""",
        }
        return explanations.get(operator, "Operador no disponible")


class CachingManager:
    """Gestor de caché para cálculos costosos."""

    _cache = {}

    @classmethod
    def get_cache_key(cls, model_hash: int, operation: str) -> str:
        """Generar clave de caché."""
        return f"{model_hash}_{operation}"

    @classmethod
    def get_cached_result(cls, model_hash: int, operation: str):
        """Obtener resultado de caché."""
        key = cls.get_cache_key(model_hash, operation)
        return cls._cache.get(key)

    @classmethod
    def set_cached_result(cls, model_hash: int, operation: str, result):
        """Guardar resultado en caché."""
        key = cls.get_cache_key(model_hash, operation)
        cls._cache[key] = result

    @classmethod
    def clear_cache(cls):
        """Limpiar todo el caché."""
        cls._cache.clear()

    @classmethod
    def get_cache_size(cls) -> int:
        """Obtener tamaño del caché."""
        return len(cls._cache)