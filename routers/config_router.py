"""
Router HTTP para la configuracion y reglas de negocio globales.
"""

from typing import Any, Dict, Optional
from fastapi import APIRouter, status
from pydantic import BaseModel, ConfigDict, Field

from domain.reglas import ReglasNegocio
from routers.comun import manejar_excepcion_http

router = APIRouter(prefix="/configuracion", tags=["Configuración"])


class ActualizarConfiguracionNegocio(BaseModel):
    """Esquema de solicitud para actualizar parametros de negocio globales."""
    iva_porcentaje: Optional[float] = Field(
        None,
        ge=0,
        le=1,
        description="Porcentaje del IVA en valor decimal (ej: 0.19 para 19%)",
    )
    tolerancia_max: Optional[float] = Field(
        None,
        ge=0,
        description="Tolerancia maxima permitida en cuadratura financiera",
    )
    anticipacion_min_h: Optional[int] = Field(
        None,
        ge=0,
        description="Horas minimas de anticipacion requeridas para programar una salida",
    )

    model_config = ConfigDict(extra="forbid")


@router.get(
    "",
    response_model=Dict[str, Any],
    summary="Obtener las reglas de negocio actuales",
    status_code=status.HTTP_200_OK,
)
def get_configuracion() -> Dict[str, Any]:
    """Retorna la configuracion global parametrizable en memoria."""
    return ReglasNegocio.obtener_configuracion()


@router.patch(
    "",
    response_model=Dict[str, Any],
    summary="Modificar las reglas de negocio en ejecucion",
    status_code=status.HTTP_200_OK,
)
def actualizar_configuracion(payload: ActualizarConfiguracionNegocio) -> Dict[str, Any]:
    """Actualiza parametros como IVA, tolerancia financiera o anticipacion minima."""
    try:
        return ReglasNegocio.actualizar_configuracion(
            iva_porcentaje=payload.iva_porcentaje,
            tolerancia_max=payload.tolerancia_max,
            anticipacion_min_h=payload.anticipacion_min_h,
        )
    except ValueError as error:
        raise manejar_excepcion_http(error)