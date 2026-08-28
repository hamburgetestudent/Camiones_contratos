"""
Modulo de control de estados y transiciones permitidas para los contratos.
"""

from enum import StrEnum
from typing import Optional, Set, Dict, Any
from datetime import datetime, timezone
from uuid import UUID


class EstadoContrato(StrEnum):
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


class MaquinaEstadosContrato:
    """Clase encargada de controlar y permitir transiciones válidas de estado."""

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
    def validar_transicion(
        cls,
        estado_actual: EstadoContrato,
        nuevo_estado: EstadoContrato,
    ) -> bool:
        """Verifica si la transicion entre dos estados esta permitida."""
        estados_posibles = cls.TRANSICIONES_PERMITIDAS.get(estado_actual, set())
        return nuevo_estado in estados_posibles

    @classmethod
    def cambiar_estado(
        cls,
        contrato_data: Any,
        nuevo_estado: EstadoContrato,
        id_transportista: Optional[UUID] = None,
        id_camion: Optional[UUID] = None,
    ) -> Any:
        """
        Aplica la transicion de estado validando reglas de negocio requeridas por cada estado.
        """
        if not cls.validar_transicion(contrato_data.estado, nuevo_estado):
            raise ValueError(
                f"Transicion de estado no permitida, no se puede pasar de {contrato_data.estado.value} a {nuevo_estado.value}"
            )

        if nuevo_estado in (EstadoContrato.PUBLICADO, EstadoContrato.EN_SUBASTA):
            if contrato_data.id_transportista is not None:
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
