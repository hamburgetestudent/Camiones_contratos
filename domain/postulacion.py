"""
Modelos de dominio y esquemas Pydantic para el Motor de Postulaciones y Subastas.
"""

from datetime import datetime, timezone
from enum import StrEnum
from typing import Optional, Dict, Set
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, AwareDatetime


class EstadoPostulacion(StrEnum):
    BORRADOR = "BORRADOR"
    POSTULADA = "POSTULADA"
    SELECCIONADA = "SELECCIONADA"
    RECHAZADA = "RECHAZADA"


class MaquinaEstadoPostulacion:
    """Control de transiciones permitidas para el ciclo de vida de una postulacion."""

    TRANSICIONES_PERMITIDAS: Dict[EstadoPostulacion, Set[EstadoPostulacion]] = {
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

    @classmethod
    def validar_transicion(
        cls,
        estado_actual: EstadoPostulacion,
        nuevo_estado: EstadoPostulacion,
    ) -> bool:
        """Verifica si la transicion entre dos estados de postulacion esta permitida."""
        estados_posibles = cls.TRANSICIONES_PERMITIDAS.get(estado_actual, set())
        return nuevo_estado in estados_posibles


class PostulacionBase(BaseModel):
    """Esquema base para datos enviados en una postulacion."""
    carga_id: UUID = Field(..., description="ID de la carga o contrato publicado")
    transportista_id: UUID = Field(..., description="ID del transportista que postula")
    precio_oferta: float = Field(..., ge=5000, description="Tarifa ofrecida por el viaje (Minimo: 5000 CLP)")
    tiempo_entrega_horas: float = Field(..., gt=0, description="Tiempo estimado de entrega en horas")
    comentario: Optional[str] = Field(None, max_length=500, description="Nota o comentario adicional del transportista")


class PostulacionCrear(PostulacionBase):
    """Modelo DTO para la creacion de una postulacion."""
    pass


class PostulacionModelo(PostulacionBase):
    """Modelo completo de entidad y persistencia de una postulacion."""
    id: UUID = Field(default_factory=uuid4, description="ID unico de la postulacion")
    estado: EstadoPostulacion = Field(default=EstadoPostulacion.POSTULADA, description="Estado actual de la postulacion")
    created_at: AwareDatetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Fecha y hora de creacion")
