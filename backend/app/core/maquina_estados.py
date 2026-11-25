"""Clase base genérica para máquinas de estados.

Se reutiliza en los módulos de contratos y subastas.
"""

from enum import StrEnum
from typing import Generic, TypeVar

S = TypeVar("S", bound=StrEnum)


class MaquinaEstadosBase(Generic[S]):  # noqa: UP046
    """Clase base reutilizable para control de transiciones de estados."""

    TRANSICIONES_PERMITIDAS: dict[S, set[S]] = {}

    @classmethod
    def validar_transicion(cls, estado_actual: S, nuevo_estado: S) -> bool:
        """Verifica si la transicion entre dos estados esta permitida."""
        estados_posibles = cls.TRANSICIONES_PERMITIDAS.get(estado_actual, set())
        return nuevo_estado in estados_posibles

    @classmethod
    def obtener_estados(cls, estado_actual: S) -> set[S]:
        """Retorna el conjunto de estados a los que se puede transicionar desde el estado actual."""
        return cls.TRANSICIONES_PERMITIDAS.get(estado_actual, set()).copy()

    @classmethod
    def estado_terminal(cls, estado: S) -> bool:
        """Indica si un estado no permite transiciones posteriores."""
        return len(cls.TRANSICIONES_PERMITIDAS.get(estado, set())) == 0

    # Alias para retrocompatibilidad
    vali_transicion = validar_transicion
    obt_estados = obtener_estados
