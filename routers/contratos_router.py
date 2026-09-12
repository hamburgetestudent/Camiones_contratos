"""Router HTTP para los endpoints de ciclo de vida de los Contratos."""

from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from domain.maquina_estados import EstadoContrato
from domain.modelos import ContratoCrear, ContratoModelo
from routers.comun import ServicioContratoDep, manejar_excepcion_http

router = APIRouter(prefix="/contratos", tags=["Contratos"])


class SolicitudCambioEstado(BaseModel):
    """Esquema de solicitud para transicionar el estado en el ciclo de vida de un contrato.

    Attributes:
        nuevo_estado (EstadoContrato): Estado destino validado por la máquina de estados.
        id_transportista (Optional[UUID]): Identificador único del transportista asignado (obligatorio al adjudicar).
        id_camion (Optional[UUID]): Identificador del vehículo o camión asignado a la operación.
    """

    nuevo_estado: EstadoContrato = Field(..., description="Nuevo estado al que avanzara el contrato")
    id_transportista: UUID | None = Field(None, description="Identificador del transportista asignado")
    id_camion: UUID | None = Field(None, description="Identificador del camion asignado")

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
def obtener_contrato(
    contrato_id: UUID,
    contrato_service: ServicioContratoDep,
) -> ContratoModelo:
    """Recupera los detalles de un contrato por su ID unico."""
    try:
        return contrato_service.obtener_contrato(contrato_id)
    except Exception as error:
        raise manejar_excepcion_http(error)


# Alias para retrocompatibilidad
obt_contrato = obtener_contrato


@router.get(
    "",
    response_model=list[ContratoModelo],
    status_code=status.HTTP_200_OK,
    summary="Listar todos los contratos registrados",
)
def listar_contratos(
    contrato_service: ServicioContratoDep,
) -> list[ContratoModelo]:
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
    actor_id: UUID = Header(
        ...,
        alias="X-User-Id",
        description="Usuario responsable del cambio de estado",
    ),
) -> ContratoModelo:
    """Aplica la maquina de estados para avanzar el contrato a un nuevo estado."""
    try:
        return contrato_service.cambiar_estado(
            contrato_id=contrato_id,
            nuevo_estado=payload.nuevo_estado,
            id_transportista=payload.id_transportista,
            id_camion=payload.id_camion,
            actor_id=actor_id,
        )
    except Exception as error:
        raise manejar_excepcion_http(error)
