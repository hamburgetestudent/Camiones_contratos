"""Estados y transiciones permitidas del ciclo de vida de un contrato."""

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from app.core.maquina_estados import MaquinaEstadosBase


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

    TRANSICIONES_PERMITIDAS: dict[EstadoContrato, set[EstadoContrato]] = {
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
        id_transportista: UUID | None = None,
        id_camion: UUID | None = None,
    ) -> Any:
        """Aplica la transicion de estado validando invariantes y reglas de negocio.

        Precondiciones:
            - ``nuevo_estado`` figura en ``TRANSICIONES_PERMITIDAS[estado_actual]``.
            - Hacia PUBLICADO / EN_SUBASTA: el contrato no tiene transportista asignado.
            - Hacia ADJUDICADO: ``id_transportista`` es obligatorio.

        Postcondiciones:
            - ``contrato_data.estado == nuevo_estado``.
            - Hacia PUBLICADO / EN_SUBASTA: ``fecha_publicacion`` queda definida.
            - Hacia ADJUDICADO: ``id_transportista`` (y ``id_camion`` si se informo) quedan asignados.

        Invariantes:
            - CANCELADO y FINALIZADO son estados terminales (no admiten transiciones).
            - Un contrato EN_SUBASTA o PUBLICADO nunca tiene transportista asignado.

        Raises:
            ValueError: Si se viola alguna precondicion (el contrato no se modifica).
        """
        if not cls.validar_transicion(contrato_data.estado, nuevo_estado):
            raise ValueError(
                "Transicion de estado no permitida, no se puede pasar de "
                f"{contrato_data.estado.value} a {nuevo_estado.value}"
            )

        if nuevo_estado in (EstadoContrato.PUBLICADO, EstadoContrato.EN_SUBASTA):
            if getattr(contrato_data, "id_transportista", None) is not None:
                raise ValueError(
                    "Un contrato en subasta o publicado no puede tener un transportista asignado previo."
                )
            if not getattr(contrato_data, "fecha_publicacion", None):
                contrato_data.fecha_publicacion = datetime.now(UTC)

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
