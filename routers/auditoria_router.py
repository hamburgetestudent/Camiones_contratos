"""Endpoints de consulta historica y correcciones de auditoria."""

from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Header, Query, status

from domain.auditoria import (
    EstadoTransporteHistorico,
    EventoAuditoria,
    ResultadoIntegridadAuditoria,
    SolicitudCorreccionAuditoria,
)
from routers.comun import ServicioAuditoriaDep, manejar_excepcion_http

router = APIRouter(prefix="/auditoria", tags=["Auditoría"])


@router.get(
    "/transportes/{transporte_id}/eventos",
    response_model=list[EventoAuditoria],
    status_code=status.HTTP_200_OK,
    summary="Consultar el historial inmutable de un transporte",
)
def listar_eventos_transporte(
    transporte_id: UUID,
    auditoria_service: ServicioAuditoriaDep,
    hasta: Annotated[
        datetime | None,
        Query(description="Fecha de corte ISO 8601 con zona horaria"),
    ] = None,
) -> list[EventoAuditoria]:
    """Retorna todos los eventos conservados hasta la fecha solicitada."""
    try:
        return auditoria_service.listar_eventos(transporte_id, hasta)
    except Exception as error:
        raise manejar_excepcion_http(error)


@router.get(
    "/transportes/{transporte_id}/reconstruccion",
    response_model=EstadoTransporteHistorico,
    status_code=status.HTTP_200_OK,
    summary="Reconstruir el estado exacto de un transporte",
)
def reconstruir_transporte(
    transporte_id: UUID,
    auditoria_service: ServicioAuditoriaDep,
    hasta: Annotated[
        datetime | None,
        Query(description="Fecha de corte ISO 8601 con zona horaria"),
    ] = None,
) -> EstadoTransporteHistorico:
    """Reconstruye contrato, ofertas, revisiones, decisiones y bases vigentes."""
    try:
        return auditoria_service.reconstruir_estado(transporte_id, hasta)
    except Exception as error:
        raise manejar_excepcion_http(error)


@router.post(
    "/correcciones",
    response_model=EventoAuditoria,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar una correccion sin alterar el evento original",
)
def registrar_correccion(
    payload: SolicitudCorreccionAuditoria,
    auditoria_service: ServicioAuditoriaDep,
    actor_id: Annotated[
        UUID,
        Header(alias="X-User-Id", description="Usuario responsable de la correccion"),
    ],
) -> EventoAuditoria:
    """Anexa la rectificacion y la enlaza criptograficamente al historial."""
    try:
        return auditoria_service.registrar_correccion(payload, actor_id)
    except Exception as error:
        raise manejar_excepcion_http(error)


@router.get(
    "/integridad",
    response_model=ResultadoIntegridadAuditoria,
    status_code=status.HTTP_200_OK,
    summary="Verificar la integridad del registro de auditoria",
)
def verificar_integridad(auditoria_service: ServicioAuditoriaDep) -> ResultadoIntegridadAuditoria:
    """Recalcula la cadena SHA-256 y reporta cualquier alteracion."""
    return auditoria_service.verificar_integridad()
