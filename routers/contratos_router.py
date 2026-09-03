"""
Router HTTP para los endpoints de ciclo de vida de los Contratos.
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, status
from pydantic import BaseModel, ConfigDict, Field

from domain.maquina_estados import EstadoContrato
from domain.modelos import ContratoCrear, ContratoModelo
from routers.comun import ServicioContratoDep, manejar_excepcion_http

router = APIRouter(prefix="/contratos", tags=["Contratos"])


class SolicitudCambioEstado(BaseModel):
    """Esquema para la transicion de estado de un contrato."""
    nuevo_estado: EstadoContrato = Field(..., description="Nuevo estado al que avanzara el contrato")
    id_transportista: Optional[UUID] = Field(None, description="Identificador del transportista asignado")
    id_camion: Optional[UUID] = Field(None, description="Identificador del camion asignado")

    model_config = ConfigDict(extra="forbid")


@router.post(
    "",
    response_model=ContratoModelo,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo contrato (Borrador)",
)
def crear_contrato(
    datos_contrato: ContratoCrear,
    contrato_service: ServicioContratoDep,
) -> ContratoModelo:
    """Crea un contrato aplicando las validaciones de negocio en el modelo Pydantic y persistiendo via DAO."""
    try:
        return contrato_service.crear_contrato(datos_contrato)
    except PermissionError as error:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(error),
        )
    except (ValueError, ValidationError) as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error en validacion de contrato: {str(error)}",
        )


@router.get(
    "/{contrato_id}",
    response_model=ContratoModelo,
    status_code=status.HTTP_200_OK,
    summary="Obtener un contrato por ID",
)
def obt_contrato(
    contrato_id: UUID,
    contrato_service: ServicioContratoDep,
) -> ContratoModelo:
    """Recupera los detalles de un contrato por su ID unico."""
    try:
        return contrato_service.obtener_contrato(contrato_id)
    except Exception as error:
        raise manejar_excepcion_http(error)


@router.get(
    "",
    response_model=List[ContratoModelo],
    status_code=status.HTTP_200_OK,
    summary="Listar todos los contratos registrados",
)
def listar_contratos(
    contrato_service: ServicioContratoDep,
) -> List[ContratoModelo]:
    """Retorna la lista de todos los contratos almacenados en el DAO."""
    return contrato_service.listar_contratos()


@router.patch(
    "/{contrato_id}/estado",
    response_model=ContratoModelo,
    status_code=status.HTTP_200_OK,
    summary="Transicion de estado del contrato",
)
def cambiar_estado_contrato(
    contrato_id: UUID,
    payload: SolicitudCambioEstado,
    contrato_service: ServicioContratoDep,
) -> ContratoModelo:
    """Aplica la maquina de estados para avanzar el contrato a un nuevo estado."""
    try:
        return contrato_service.cambiar_estado(
            contrato_id=contrato_id,
            nuevo_estado=payload.nuevo_estado,
            id_transportista=payload.id_transportista,
            id_camion=payload.id_camion,
        )
    except Exception as error:
        raise manejar_excepcion_http(error)
