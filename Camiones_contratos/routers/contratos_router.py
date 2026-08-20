"""
Router HTTP para los endpoints de ciclo de vida de los Contratos.
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, ValidationError

from Camiones_contratos.domain.modelos import ContratoCrear, ContratoModelo
from Camiones_contratos.domain.maquina_estados import EstadoContrato
from dao.contrato_dao import ContratoDAOInMemory
from services.contrato_service_borrador import ContratoService

router = APIRouter(prefix="/contratos", tags=["Contratos"])

# Instancia singleton del DAO y Servicio de Contratos para la aplicacion
contrato_dao = ContratoDAOInMemory()
contrato_service = ContratoService(dao=contrato_dao)


class SolicitudCambioEstado(BaseModel):
    nuevo_estado: EstadoContrato
    id_transportista: Optional[UUID] = None
    id_camion: Optional[UUID] = None


@router.post(
    "",
    response_model=ContratoModelo,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo contrato (Borrador)",
)
def crear_contrato(datos_contrato: ContratoCrear):
    """Crea un contrato aplicando las validaciones de negocio en el modelo Pydantic y persistiendo via DAO."""
    try:
        return contrato_service.crear_contrato(datos_contrato)
    except (ValueError, ValidationError) as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error en validacion de contrato: {str(error)}",
        )


@router.get(
    "/{contrato_id}",
    response_model=ContratoModelo,
    summary="Obtener un contrato por ID",
)
def obtener_contrato(contrato_id: UUID):
    """Recupera los detalles de un contrato por su ID unico."""
    try:
        return contrato_service.obtener_contrato(contrato_id)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )


@router.get(
    "",
    response_model=List[ContratoModelo],
    summary="Listar todos los contratos registrados",
)
def listar_contratos():
    """Retorna la lista de todos los contratos almacenados en el DAO."""
    return contrato_service.listar_contratos()


@router.patch(
    "/{contrato_id}/estado",
    response_model=ContratoModelo,
    summary="Transicion de estado del contrato",
)
def cambiar_estado_contrato(contrato_id: UUID, payload: SolicitudCambioEstado):
    """Aplica la maquina de estados para avanzar el contrato a un nuevo estado."""
    try:
        return contrato_service.cambiar_estado(
            contrato_id=contrato_id,
            nuevo_estado=payload.nuevo_estado,
            id_transportista=payload.id_transportista,
            id_camion=payload.id_camion,
        )
    except ValueError as error:
        detail_str = str(error)
        if "no fue encontrado" in detail_str:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail_str)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail_str)