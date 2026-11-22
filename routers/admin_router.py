"""Operaciones reservadas al rol administrativo."""

from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict

from routers.comun import confirmar_operacion
from routers.sesion import UsuarioActual, administrador_actual
from services import admin_service
from services.admin_service import TipoElemento

router = APIRouter(
    prefix="/admin",
    tags=["Administración"],
)


class OperacionAdministrativa(BaseModel):
    """El responsable proviene de la sesión, nunca del cuerpo de la solicitud."""

    model_config = ConfigDict(extra="forbid")
    motivo: str = ""
    confirmado: bool = False


@router.get("/resumen", dependencies=[Depends(administrador_actual)])
def resumen():
    return admin_service.resumen()


@router.get("/elementos/{tipo}", dependencies=[Depends(administrador_actual)])
def elementos(
    tipo: TipoElemento, incluir_eliminados: bool = False, estado: str | None = None
):
    return admin_service.listar_elementos(tipo, incluir_eliminados, estado)


@router.post("/elementos/{tipo}/{elemento_id}/eliminar")
def eliminar(
    tipo: TipoElemento,
    elemento_id: UUID,
    baja: OperacionAdministrativa,
    actor: UsuarioActual,
):
    return confirmar_operacion(
        admin_service.eliminar, tipo, elemento_id, actor, baja.motivo, baja.confirmado
    )


@router.post("/elementos/contrato/{contrato_id}/cancelar")
def cancelar(
    contrato_id: UUID, solicitud: OperacionAdministrativa, actor: UsuarioActual
):
    return confirmar_operacion(
        admin_service.cancelar_contrato,
        contrato_id,
        actor,
        solicitud.motivo,
        solicitud.confirmado,
    )


@router.get("/historial", dependencies=[Depends(administrador_actual)])
def historial(
    desde: date | None = None,
    hasta: date | None = None,
    administrador: str | None = None,
    accion: str | None = None,
    resultado: str | None = None,
    tipo: TipoElemento | None = None,
    elemento_id: UUID | None = None,
):
    if desde and hasta and desde > hasta:
        raise HTTPException(422, "La fecha inicial supera la final.")
    return admin_service.historial(
        desde, hasta, administrador, accion, resultado, tipo, elemento_id
    )
