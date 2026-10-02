"""
Módulo de caché para cálculos costosos en SURFACELAB.
"""

from __future__ import annotations

import functools
import hashlib
import inspect
from typing import Any, Callable, Optional
import sympy as sp


class CalculationCache:
    """Caché para resultados de cálculos matemáticos."""

    _cache: dict = {}
    _max_size: int = 100
    _hits: int = 0
    _misses: int = 0

    @classmethod
    def _make_hash(cls, *args, **kwargs) -> str:
        """Crear hash único para los argumentos."""
        hasher = hashlib.md5()
        
        for arg in args:
            try:
                hasher.update(str(arg).encode())
            except:
                pass
        
        for k, v in sorted(kwargs.items()):
            try:
                hasher.update(f"{k}={v}".encode())
            except:
                pass
        
        return hasher.hexdigest()

    @classmethod
    def get(cls, key: str) -> Optional[Any]:
        """Obtener valor del caché."""
        if key in cls._cache:
            cls._hits += 1
            return cls._cache[key]
        cls._misses += 1
        return None

    @classmethod
    def set(cls, key: str, value: Any):
        """Guardar valor en caché."""
        # Limpiar caché si está lleno
        if len(cls._cache) >= cls._max_size:
            # Eliminar la mitad más antigua
            keys_to_remove = list(cls._cache.keys())[:cls._max_size // 2]
            for k in keys_to_remove:
                del cls._cache[k]
        
        cls._cache[key] = value

    @classmethod
    def clear(cls):
        """Limpiar tutto el caché."""
        cls._cache.clear()
        cls._hits = 0
        cls._misses = 0

    @classmethod
    def stats(cls) -> dict:
        """Obtener estadísticas del caché."""
        total = cls._hits + cls._misses
        hit_rate = (cls._hits / total * 100) if total > 0 else 0
        return {
            "size": len(cls._cache),
            "hits": cls._hits,
            "misses": cls._misses,
            "hit_rate": f"{hit_rate:.1f}%",
        }


def cached_calculation(func: Callable) -> Callable:
    """Decorador para cachear cálculos."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Crear clave de caché
        cache_key = CalculationCache._make_hash(func.__name__, *args, **kwargs)
        
        # Verificar caché
        cached_result = CalculationCache.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        # Calcular y guardar en caché
        result = func(*args, **kwargs)
        CalculationCache.set(cache_key, result)
        
        return result
    
    # Agregar método para limpiar caché específico
    wrapper.clear_cache = lambda: CalculationCache.clear()
    wrapper.cache_stats = lambda: CalculationCache.stats()
    
    return wrapper


class SurfaceModelHasher:
    """Hasher para modelos de superficie."""

    @staticmethod
    def hash_model(model) -> str:
        """Crear hash único para un SurfaceModel."""
        hasher = hashlib.md5()
        
        if hasattr(model, 'system'):
            hasher.update(str(model.system.value).encode())
        if hasattr(model, 'func_expr') and model.func_expr:
            hasher.update(str(model.func_expr).encode())
        if hasattr(model, 'x_expr') and model.x_expr:
            hasher.update(str(model.x_expr).encode())
        if hasattr(model, 'y_expr') and model.y_expr:
            hasher.update(str(model.y_expr).encode())
        if hasattr(model, 'z_expr') and model.z_expr:
            hasher.update(str(model.z_expr).encode())
        if hasattr(model, 'limits') and model.limits:
            hasher.update(str(model.limits.as_tuple()).encode())
        if hasattr(model, 'flux_components') and model.flux_components:
            for fc in model.flux_components:
                hasher.update(str(fc).encode())
        
        return hasher.hexdigest()


class LazyEvaluator:
    """Evaluador perezoso para expresiones simbólicas."""

    @staticmethod
    def evaluate_if_needed(expr: sp.Expr, max_terms: int = 100) -> sp.Expr:
        """Evaluar expresión solo si es necesario."""
        if expr is None:
            return None
        
        try:
            # Verificar si es una expresión grande
            if hasattr(expr, 'args') and len(expr.args) > max_terms:
                # No evaluar expresiones grandes
                return expr
            
            return sp.simplify(expr)
        except:
            return expr

    @staticmethod
    def numeric_eval_safe(expr: sp.Expr, variables: list, values: list, default: float = 0.0) -> float:
        """Evaluación numérica segura."""
        try:
            func = sp.lambdify(variables, expr, modules="numpy")
            return float(func(*values))
        except:
            return default


class MemoizedFunction:
    """Wrapper para funciones con memoización."""

    def __init__(self, func: Callable):
        self.func = func
        self.memo = {}
        self.call_count = 0

    def __call__(self, *args, **kwargs):
        key = str(args) + str(sorted(kwargs.items()))
        
        if key in self.memo:
            return self.memo[key]
        
        self.call_count += 1
        result = self.func(*args, **kwargs)
        self.memo[key] = result
        
        return result

    def clear(self):
        """Limpiar memoria."""
        self.memo.clear()
        self.call_count = 0

    def stats(self) -> dict:
        """Obtener estadísticas."""
        return {
            "calls": self.call_count,
            "cached": len(self.memo),
        }