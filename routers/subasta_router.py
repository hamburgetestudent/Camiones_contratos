"""Router HTTP para los endpoints de Postulaciones y Subastas de Carga."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, status
from pydantic import BaseModel, ConfigDict, Field

from domain.modelos import ContratoModelo
from domain.postulacion import PostulacionCrear, PostulacionModelo
from routers.comun import ServicioSubastaDep, manejar_excepcion_http

router = APIRouter(prefix="/subastas", tags=["Subastas y Postulaciones"])


class SolicitudAdjudicacion(BaseModel):
    """Esquema de solicitud JSON para adjudicar una subasta a una postulacion ganadora.

    Attributes:
        carga_id (UUID): Identificador unico del contrato o carga subastada.
        postulacion_id (UUID): Identificador unico de la postulacion de oferta ganadora.
    """

    carga_id: UUID = Field(..., description="Identificador unico de la carga o contrato")
    postulacion_id: UUID = Field(..., description="Identificador unico de la postulacion ganadora")

    model_config = ConfigDict(extra="forbid")


@router.get(
    "/cargas",
    response_model=list[ContratoModelo],
    status_code=status.HTTP_200_OK,
    summary="Explorar cargas disponibles para subasta",
)
def explorar_cargas(
    subasta_service: ServicioSubastaDep,
    region: Annotated[str | None, Query(description="Filtro por origen o destino (comuna/region)")] = None,
    tipo_carroceria: Annotated[str | None, Query(description="Filtro por tipo de carga o carroceria")] = None,
    distancia_max_km: Annotated[float | None, Query(gt=0, description="Filtro por distancia maxima simulada")] = None,
) -> list[ContratoModelo]:
    """Retorna el listado de cargas publicadas o en subasta que cumplen con los filtros especificados."""
    return subasta_service.explorar_cargas(
        region=region,
        tipo_carroceria=tipo_carroceria,
        distancia_max_km=distancia_max_km,
    )


@router.post(
    "/postular",
    response_model=PostulacionModelo,
    status_code=status.HTTP_201_CREATED,
    summary="Enviar una postulacion/oferta a una carga en subasta",
)
def postular_a_carga(
    datos: PostulacionCrear,
    subasta_service: ServicioSubastaDep,
    onboarding_aprobado: Annotated[
        bool, Query(description="Verificacion de onboarding APROBADO del transportista")
    ] = True,
) -> PostulacionModelo:
    """Registra la oferta de un transportista para una carga dada."""
    try:
        return subasta_service.postular_a_carga(
            datos_postulacion=datos,
            onboarding_aprobado=onboarding_aprobado,
        )
    except Exception as error:
        raise manejar_excepcion_http(error)


@router.get(
    "/cargas/{carga_id}/postulaciones",
    response_model=list[PostulacionModelo],
    status_code=status.HTTP_200_OK,
    summary="Listar postulaciones recibidas para una carga",
)
def listar_postulaciones_carga(
    carga_id: UUID,
    subasta_service: ServicioSubastaDep,
) -> list[PostulacionModelo]:
    """Retorna todas las postulaciones enviadas a una carga especifica."""
    return subasta_service.listar_postulaciones_carga(carga_id)


@router.post(
    "/adjudicar",
    response_model=PostulacionModelo,
    status_code=status.HTTP_200_OK,
    summary="Adjudicar la oferta ganadora de una subasta",
)
def adjudicar_subasta(
    payload: SolicitudAdjudicacion,
    subasta_service: ServicioSubastaDep,
) -> PostulacionModelo:
    """El dador selecciona la postulacion ganadora, cambiando la carga a ADJUDICADO y rechazando el resto."""
    try:
        return subasta_service.adjudicar_subasta(
            carga_id=payload.carga_id,
            postulacion_id=payload.postulacion_id,
        )
    except Exception as error:
        raise manejar_excepcion_http(error)
