"""
Modulo de control de estados y transiciones permitidas del dominio.
Proporciona una clase base generica para maquinas de estados y la logica de contratos.
"""

try:
    from enum import StrEnum
except ImportError:
    from enum import Enum
    class StrEnum(str, Enum):
        pass
from typing import Optional, Set, Dict, Any
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Dict, Generic, Optional, Set, TypeVar
from uuid import UUID

S = TypeVar("S", bound=StrEnum)


class MaquinaEstadosBase(Generic[S]):
    """Clase base reutilizable para control de transiciones de estados."""

    TRANSICIONES_PERMITIDAS: Dict[S, Set[S]] = {}

    @classmethod
    def vali_transicion(cls, estado_actual: S, nuevo_estado: S) -> bool:
        """Verifica si la transicion entre dos estados esta permitida."""
        estados_posibles = cls.TRANSICIONES_PERMITIDAS.get(estado_actual, set())
        return nuevo_estado in estados_posibles

    @classmethod
    def obt_estados(cls, estado_actual: S) -> Set[S]:
        """Retorna el conjunto de estados a los que se puede transicionar desde el estado actual."""
        return cls.TRANSICIONES_PERMITIDAS.get(estado_actual, set()).copy()

    @classmethod
    def estado_terminal(cls, estado: S) -> bool:
        """Indica si un estado no permite transiciones posteriores."""
        return len(cls.TRANSICIONES_PERMITIDAS.get(estado, set())) == 0


class EstadoContrato(StrEnum):
    """Estados del ciclo de vida de un contrato de transporte."""
    BORRADOR = "BORRADOR"
    PUBLICADO = "PUBLICADO"
    EN_SUBASTA = "EN_SUBASTA"
    EN_POSTULACION = "EN_POSTULACION"
    ADJUDICADO = "ADJUDICADO"
    EN_TRANSITO = "EN_TRANSITO"
    ENTREGADO = "ENTREGADO"
    FINALIZADO = "FINALIZADO"
    CANCELADO = "CANCELADO"
    EN_DISPUTA = "EN_DISPUTA"


class MaquinaEstadosContrato(MaquinaEstadosBase[EstadoContrato]):
    """Maquina de estados para el ciclo de vida de Contratos."""

    TRANSICIONES_PERMITIDAS: Dict[EstadoContrato, Set[EstadoContrato]] = {
        EstadoContrato.BORRADOR: {
            EstadoContrato.PUBLICADO,
            EstadoContrato.EN_SUBASTA,
            EstadoContrato.CANCELADO,
        },
        EstadoContrato.PUBLICADO: {
            EstadoContrato.EN_SUBASTA,
            EstadoContrato.EN_POSTULACION,
            EstadoContrato.ADJUDICADO,
            EstadoContrato.CANCELADO,
        },
        EstadoContrato.EN_SUBASTA: {
            EstadoContrato.EN_POSTULACION,
            EstadoContrato.ADJUDICADO,
            EstadoContrato.CANCELADO,
        },
        EstadoContrato.EN_POSTULACION: {
            EstadoContrato.ADJUDICADO,
            EstadoContrato.CANCELADO,
        },
        EstadoContrato.ADJUDICADO: {
            EstadoContrato.EN_TRANSITO,
            EstadoContrato.CANCELADO,
        },
        EstadoContrato.EN_TRANSITO: {
            EstadoContrato.ENTREGADO,
            EstadoContrato.EN_DISPUTA,
        },
        EstadoContrato.ENTREGADO: {
            EstadoContrato.FINALIZADO,
            EstadoContrato.EN_DISPUTA,
        },
        EstadoContrato.CANCELADO: set(),
        EstadoContrato.FINALIZADO: set(),
        EstadoContrato.EN_DISPUTA: {
            EstadoContrato.FINALIZADO,
            EstadoContrato.CANCELADO,
        },
    }

    @classmethod
    def cambiar_estado(
        cls,
        contrato_data: Any,
        nuevo_estado: EstadoContrato,
        id_transportista: Optional[UUID] = None,
        id_camion: Optional[UUID] = None,
    ) -> Any:
        """
        Aplica la transicion de estado validando invariantes y reglas de negocio.
        """
        if not cls.vali_transicion(contrato_data.estado, nuevo_estado):
            raise ValueError(
                f"Transicion de estado no permitida, no se puede pasar de {contrato_data.estado.value} a {nuevo_estado.value}"
            )

        if nuevo_estado in (EstadoContrato.PUBLICADO, EstadoContrato.EN_SUBASTA):
            if getattr(contrato_data, "id_transportista", None) is not None:
                raise ValueError("Un contrato en subasta o publicado no puede tener un transportista asignado previo.")
            if not getattr(contrato_data, "fecha_publicacion", None):
                contrato_data.fecha_publicacion = datetime.now(timezone.utc)

        elif nuevo_estado == EstadoContrato.ADJUDICADO:
            if not id_transportista:
                raise ValueError(
                    "Para adjudicar un contrato se requiere indicar obligatoriamente 'id_transportista'"
                )
            contrato_data.id_transportista = id_transportista
            if id_camion:
                contrato_data.id_camion = id_camion

        contrato_data.estado = nuevo_estado
        return contrato_data