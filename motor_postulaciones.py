from pydantic import Field, BaseModel, AwareDatetime
from enum import StrEnum
from typing import Dict, Set, Optional
from uuid import uuid4, UUID
from datetime import datetime
class EstadoPostulacion(StrEnum):
    BORRADOR = "BORRADOR"
    POSTULADO = "POSTULADO"
    RECHAZADO = "RECHAZADO"
    ASIGNADA = "ASIGNADA"

class MaquinaEstadoPostulacion:
    TRANSICIONES_PERMITIDAS: Dict[EstadoPostulacion, Set[EstadoPostulacion]] = {
        EstadoPostulacion.BORRADOR: {
            EstadoPostulacion.POSTULADO,
        },
        EstadoPostulacion.POSTULADO: {
            EstadoPostulacion.RECHAZADO,
            EstadoPostulacion.ASIGNADA,
        },
        EstadoPostulacion.RECHAZADO: {
            EstadoPostulacion.ASIGNADA,
        },
        EstadoPostulacion.ASIGNADA: {
            EstadoPostulacion.RECHAZADO,
        }
    }


class PostulacionBase(BaseModel):
    id_postulante : UUID = Field(..., description= "ID de la empresa postulante")

class PostulacionModelo(PostulacionBase):
    ID : UUID = Field(default_factory=uuid4, description = "ID unico del contrato")
    carga_ID : Optional[UUID] = Field(default_factory=uuid4, description = "ID unico de la carga ID")
    estado : EstadoPostulacion = Field(default=EstadoPostulacion.BORRADOR, description= "Estado de postulación")
    comentario : str = Field(default=" ", description= "Comentario de la postulacion" )
    created_at : Optional[datetime] = Field(default= None, description= "Fecha de publicación del contrato")