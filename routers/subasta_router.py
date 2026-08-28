"""
Router HTTP para los endpoints de Postulaciones y Subastas de Carga.
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, HTTPException, Query, status, Depends
from pydantic import BaseModel, ValidationError

from domain.modelos import ContratoModelo
from domain.postulacion import PostulacionCrear, PostulacionModelo
from services.subasta_service import SubastaService
from services.dependencies import get_subasta_service

router = APIRouter(prefix="/subastas", tags=["Subastas y Postulaciones"])


class SolicitudAdjudicacion(BaseModel):
    carga_id: UUID
    postulacion_id: UUID


@router.get(
    "/cargas",
    response_model=List[ContratoModelo],
    summary="Explorar cargas disponibles para subasta",
)
def explorar_cargas(
    region: Optional[str] = Query(None, description="Filtro por origen o destino (comuna/región)"),
    tipo_carroceria: Optional[str] = Query(None, description="Filtro por tipo de carga o carrocería"),
    distancia_max_km: Optional[float] = Query(None, gt=0, description="Filtro por distancia máxima simulada"),
    subasta_service: SubastaService = Depends(get_subasta_service),
):
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
    summary="Enviar una postulación/oferta a una carga en subasta",
)
def postular_a_carga(
    datos: PostulacionCrear,
    onboarding_aprobado: bool = Query(True, description="Simulación de verificación de onboarding APROBADO"),
    subasta_service: SubastaService = Depends(get_subasta_service),
):
    """Registra la oferta de un transportista para una carga dada."""
    try:
        return subasta_service.postular_a_carga(datos_postulacion=datos, onboarding_aprobado=onboarding_aprobado)
    except (ValueError, ValidationError) as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )


@router.get(
    "/cargas/{carga_id}/postulaciones",
    response_model=List[PostulacionModelo],
    summary="Listar postulaciones recibidas para una carga",
)
def listar_postulaciones_carga(
    carga_id: UUID,
    subasta_service: SubastaService = Depends(get_subasta_service),
):
    """Retorna todas las postulaciones enviadas a una carga específica."""
    return subasta_service.listar_postulaciones_carga(carga_id)


@router.post(
    "/adjudicar",
    response_model=PostulacionModelo,
    summary="Adjudicar la oferta ganadora de una subasta",
)
def adjudicar_subasta(
    payload: SolicitudAdjudicacion,
    subasta_service: SubastaService = Depends(get_subasta_service),
):
    """El dador selecciona la postulación ganadora, cambiando la carga a ADJUDICADO y rechazando el resto."""
    try:
        return subasta_service.adjudicar_subasta(carga_id=payload.carga_id, postulacion_id=payload.postulacion_id)
    except ValueError as error:
        detail_str = str(error)
        if "no fue encontrad" in detail_str or "no existe" in detail_str:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail_str)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail_str)
