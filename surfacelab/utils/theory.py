from __future__ import annotations

from typing import Dict


class TheoryPanel:
    THEORY: Dict[str, str] = {
        "cartesian": """
SUPERFICIE CARTESIANA EXPLÍCITA
z = f(x,y)

Elemento diferencial:
dS = √(1 + (∂f/∂x)² + (∂f/∂y)²) dx dy

Área:
A = ∬_D √(1 + (∂f/∂x)² + (∂f/∂y)²) dx dy

Integral escalar:
∬_S g(x,y,z) dS = ∬_D g(x,y,f(x,y)) √(1 + (∂f/∂x)² + (∂f/∂y)²) dx dy
""",
        "parametric": """
SUPERFICIE PARAMÉTRICA
r(u,v) = (x(u,v), y(u,v), z(u,v))

Derivadas parciales:
r_u = ∂r/∂u, r_v = ∂r/∂v

Vector normal:
N = r_u × r_v

Elemento diferencial:
dS = |r_u × r_v| du dv

Área:
A = ∬_D |r_u × r_v| du dv

Integral escalar:
∬_S g dS = ∬_D g(r(u,v)) |r_u × r_v| du dv

Flujo:
Φ = ∬_S F · n dS = ∬_D F(r(u,v)) · (r_u × r_v) du dv
""",
        "polar": """
COORDENADAS POLARES
x = r cos(θ), y = r sin(θ)
Jacobiano: dA = r dr dθ

Para z = f(r,θ):
dS = √(1 + (∂f/∂r)² + (∂f/∂θ)²/r²) · r dr dθ
""",
        "cylindrical": """
COORDENADAS CILÍNDRICAS
x = r cos(θ), y = r sin(θ), z = z

Parametrización para z = f(r,θ):
r(r,θ) = (r cos(θ), r sin(θ), f(r,θ))

dS = √(1 + (∂f/∂r)² + (∂f/∂θ)²/r²) · r dr dθ
""",
        "spherical": """
COORDENADAS ESFÉRICAS
x = ρ sin(φ) cos(θ)
y = ρ sin(φ) sin(θ)
z = ρ cos(φ)

Esfera ρ = R:
r(θ,φ) = (R sin(φ) cos(θ), R sin(φ) sin(θ), R cos(φ))

dS = R² sin(φ) dθ dφ

Área de la esfera:
A = 4πR²
""",
    }

    @classmethod
    def get_theory(cls, system: str) -> str:
        return cls.THEORY.get(system, "Teoría no disponible para este sistema.")
