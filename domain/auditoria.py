"""Modelos de dominio para auditoria y reconstruccion historica.

Los eventos representan hechos ya ocurridos. Por esa razon son inmutables y las
rectificaciones se expresan mediante un nuevo evento que referencia al original.
"""

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, model_validator


class EntidadAuditable(StrEnum):
    """Entidades que participan en el ciclo de un transporte."""

    CONTRATO = "CONTRATO"
    OFERTA = "OFERTA"
    REVISION = "REVISION"
    DECISION = "DECISION"


class AccionAuditoria(StrEnum):
    """Hechos de negocio que deben conservar trazabilidad."""

    CONTRATO_CREADO = "CONTRATO_CREADO"
    ESTADO_CONTRATO_CAMBIADO = "ESTADO_CONTRATO_CAMBIADO"
    OFERTA_CREADA = "OFERTA_CREADA"
    OFERTA_ESTADO_CAMBIADO = "OFERTA_ESTADO_CAMBIADO"
    OFERTA_REVISADA = "OFERTA_REVISADA"
    ADJUDICACION_REALIZADA = "ADJUDICACION_REALIZADA"
    CORRECCION_REGISTRADA = "CORRECCION_REGISTRADA"


class EventoAuditoriaCrear(BaseModel):
    """Datos necesarios para anexar un hecho al registro de auditoria."""

    transporte_id: UUID = Field(..., description="Contrato o transporte al que pertenece el hecho")
    entidad: EntidadAuditable
    entidad_id: UUID
    accion: AccionAuditoria
    actor_id: UUID = Field(..., description="Usuario o sistema responsable de la actuacion")
    ocurrido_en: AwareDatetime
    datos: dict[str, Any] = Field(default_factory=dict, description="Instantanea de la entidad tras el hecho")
    bases_aplicadas: dict[str, Any] = Field(
        default_factory=dict,
        description="Reglas y configuracion vigentes usadas al ejecutar la actuacion",
    )
    informacion_utilizada: dict[str, Any] = Field(
        default_factory=dict,
        description="Antecedentes considerados para revisar o decidir",
    )
    evento_corregido_id: UUID | None = None
    motivo_correccion: str | None = Field(default=None, min_length=5, max_length=500)

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def validar_correccion(self) -> "EventoAuditoriaCrear":
        """Exige referencia y motivo solo cuando el hecho es una correccion."""
        es_correccion = self.accion == AccionAuditoria.CORRECCION_REGISTRADA
        if es_correccion and (not self.evento_corregido_id or not self.motivo_correccion):
            raise ValueError("Una correccion debe indicar el evento corregido y su motivo")
        if not es_correccion and (self.evento_corregido_id or self.motivo_correccion):
            raise ValueError("Solo un evento de correccion puede referenciar otro evento")
        return self


class EventoAuditoria(EventoAuditoriaCrear):
    """Evento persistido, encadenado mediante hashes y ordenado por secuencia."""

    secuencia: int = Field(..., ge=1)
    id: UUID
    hash_anterior: str | None = Field(default=None, pattern=r"^[a-f0-9]{64}$")
    hash_evento: str = Field(..., pattern=r"^[a-f0-9]{64}$")

    model_config = ConfigDict(extra="forbid", frozen=True)


class SolicitudCorreccionAuditoria(BaseModel):
    """Solicitud para rectificar un evento sin eliminar ni modificar el original."""

    evento_corregido_id: UUID
    motivo: str = Field(..., min_length=5, max_length=500)
    datos_corregidos: dict[str, Any] = Field(..., min_length=1)
    informacion_utilizada: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(extra="forbid")


class ResultadoIntegridadAuditoria(BaseModel):
    """Resultado de verificar la cadena criptografica del registro."""

    integra: bool
    eventos_verificados: int = Field(..., ge=0)
    primer_evento_invalido: UUID | None = None


class EstadoTransporteHistorico(BaseModel):
    """Vista reconstruida de un transporte en una fecha de corte."""

    transporte_id: UUID
    hasta: AwareDatetime
    contrato: dict[str, Any] | None = None
    ofertas: list[dict[str, Any]] = Field(default_factory=list)
    revisiones: list[dict[str, Any]] = Field(default_factory=list)
    decisiones: list[dict[str, Any]] = Field(default_factory=list)
    bases_aplicadas: list[dict[str, Any]] = Field(default_factory=list)
    correcciones: list[dict[str, Any]] = Field(default_factory=list)
    eventos_considerados: int = Field(..., ge=0)


def normalizar_fecha_utc(fecha: datetime) -> datetime:
    """Convierte una fecha consciente de zona horaria a UTC."""
    if fecha.tzinfo is None or fecha.utcoffset() is None:
        raise ValueError("La fecha de auditoria debe incluir zona horaria")
    return fecha.astimezone(UTC)
