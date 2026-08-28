"""
Modelos de dominio y esquemas Pydantic para el Motor de Postulaciones y Subastas.
"""

from datetime import datetime, timezone
from enum import StrEnum
from typing import Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, AwareDatetime


class EstadoPostulacion(StrEnum):
    POSTULADA = "POSTULADA"
    SELECCIONADA = "SELECCIONADA"
    RECHAZADA = "RECHAZADA"


class PostulacionBase(BaseModel):
    """Esquema base para datos enviados en una postulación."""
    carga_id: UUID = Field(..., description="ID de la carga o contrato publicado")
    transportista_id: UUID = Field(..., description="ID del transportista que postula")
    precio_oferta: float = Field(..., ge=5000, description="Tarifa ofrecida por el viaje (Mínimo: 5000 CLP)")
    tiempo_entrega_horas: float = Field(..., gt=0, description="Tiempo estimado de entrega en horas")
    comentario: Optional[str] = Field(None, max_length=500, description="Nota o comentario adicional del transportista")


class PostulacionCrear(PostulacionBase):
    """Modelo DTO para la creación de una postulación."""
    pass


class PostulacionModelo(PostulacionBase):
    """Modelo completo de entidad y persistencia de una postulación."""
    id: UUID = Field(default_factory=uuid4, description="ID único de la postulación")
    estado: EstadoPostulacion = Field(default=EstadoPostulacion.POSTULADA, description="Estado actual de la postulación")
    created_at: AwareDatetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Fecha y hora de creación")