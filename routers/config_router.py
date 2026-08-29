"""
Router HTTP para la configuracion y reglas de negocio globales.
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from domain.reglas import ReglasNegocio

router = APIRouter(prefix="/configuracion", tags=["Configuración"])


class ActualizarConfiguracionNegocio(BaseModel):
    iva_porcentaje: float | None = None
    tolerancia_max: float | None = None
    anticipacion_min_h: int | None = None


@router.get(
    "",
    summary="Obtener las reglas de negocio actuales",
)
def get_configuracion():
    """Retorna la configuracion global parametrizable en memoria."""
    return ReglasNegocio.obtener_configuracion()


@router.patch(
    "",
    summary="Modificar las reglas de negocio en ejecucion",
)
def actualizar_configuracion(payload: ActualizarConfiguracionNegocio):
    """Actualiza parametros como IVA, tolerancia financiera o anticipacion minima."""
    try:
        config_actualizada = ReglasNegocio.actualizar_configuracion(
            iva_porcentaje=payload.iva_porcentaje,
            tolerancia_max=payload.tolerancia_max,
            anticipacion_min_h=payload.anticipacion_min_h,
        )
        return config_actualizada
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )