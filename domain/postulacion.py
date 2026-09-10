"""
Modelos de dominio y esquemas Pydantic para el Motor de Postulaciones y Subastas.
"""

from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field

from domain.maquina_estados import MaquinaEstadosBase

TARIFA_MINIMA_POSTULACION_CLP: float = 5000.0


class EstadoPostulacion(StrEnum):
    """Estados del ciclo de vida de una postulacion."""

    BORRADOR = "BORRADOR"
    POSTULADA = "POSTULADA"
    SELECCIONADA = "SELECCIONADA"
    RECHAZADA = "RECHAZADA"


class MaquinaEstadoPostulacion(MaquinaEstadosBase[EstadoPostulacion]):
    """Control de transiciones permitidas para el ciclo de vida de una postulacion."""

    TRANSICIONES_PERMITIDAS: dict[EstadoPostulacion, set[EstadoPostulacion]] = {
        EstadoPostulacion.BORRADOR: {
            EstadoPostulacion.POSTULADA,
        },
        EstadoPostulacion.POSTULADA: {
            EstadoPostulacion.RECHAZADA,
            EstadoPostulacion.SELECCIONADA,
        },
        EstadoPostulacion.RECHAZADA: {
            EstadoPostulacion.SELECCIONADA,
        },
        EstadoPostulacion.SELECCIONADA: {
            EstadoPostulacion.RECHAZADA,
        },
    }


class PostulacionBase(BaseModel):
    """Esquema base para datos enviados en una postulacion."""

    carga_id: UUID = Field(..., description="ID de la carga o contrato publicado")
    transportista_id: UUID = Field(..., description="ID del transportista que postula")
    precio_oferta: float = Field(
        ...,
        ge=TARIFA_MINIMA_POSTULACION_CLP,
        description=f"Tarifa ofrecida por el viaje (Minimo: {int(TARIFA_MINIMA_POSTULACION_CLP)} CLP)",
    )
    tiempo_entrega_horas: float = Field(..., gt=0, description="Tiempo estimado de entrega en horas")
    comentario: str | None = Field(None, max_length=500, description="Nota o comentario adicional del transportista")

    model_config = ConfigDict(str_strip_whitespace=True)


class PostulacionCrear(PostulacionBase):
    """Modelo DTO para la creacion de una postulacion."""

    pass


class PostulacionModelo(PostulacionBase):
    """Modelo completo de entidad y persistencia de una postulacion."""

    id: UUID = Field(default_factory=uuid4, description="ID unico de la postulacion")
    estado: EstadoPostulacion = Field(
        default=EstadoPostulacion.POSTULADA, description="Estado actual de la postulacion"
    )
    creado_en: AwareDatetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Fecha y hora de creacion UTC",
    )
