"""
Modelos de dominio y esquemas Pydantic para el modulo de Onboarding y Verificacion KYC / Fleet Compliance.
"""

from datetime import datetime, timezone
from enum import StrEnum
from typing import List, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, EmailStr, Field, field_validator


# =========================================
# Enumeraciones
# =========================================

class EstadoValidacion(StrEnum):
    PENDIENTE = "PENDIENTE"
    APROBADO = "APROBADO"
    RECHAZADO = "RECHAZADO"


class TipoDocumento(StrEnum):
    LICENCIA_CONDUCIR = "LICENCIA_CONDUCIR"
    PADRON_VEHICULO = "PADRON_VEHICULO"
    REVISION_TECNICA = "REVISION_TECNICA"
    SEGURO_CARGA = "SEGURO_CARGA"
    ANTECEDENTES = "ANTECEDENTES"


# =========================================
# Modelos de Transportista (Documentos)
# =========================================

class DocumentoTransportistaBase(BaseModel):
    tipo: TipoDocumento = Field(..., description="Tipo de documento requerido")
    archivo: str = Field(..., min_length=3, description="Ruta o referencia simulada al archivo cargado")


class CargarDocumentoDTO(DocumentoTransportistaBase):
    """Payload para la carga simulada de un documento por parte del transportista."""
    pass


class ValidarDocumentoDTO(BaseModel):
    """Payload para aprobacion o rechazo de un documento por Backoffice/Admin."""
    estado: EstadoValidacion = Field(..., description="Nuevo estado del documento (APROBADO o RECHAZADO)")


class DocumentoTransportista(DocumentoTransportistaBase):
    """Entidad completa del documento del transportista."""
    id: UUID = Field(default_factory=uuid4, description="Identificador unico del documento")
    user_id: UUID = Field(..., description="UUID del usuario transportista")
    estado: EstadoValidacion = Field(default=EstadoValidacion.PENDIENTE, description="Estado de validacion")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Fecha y hora de carga del documento",
    )


class EstadoOnboardingTransportistaDTO(BaseModel):
    """Resumen del estado global de onboarding para un transportista."""
    user_id: UUID
    estado_global: EstadoValidacion
    documentos_requeridos: List[TipoDocumento]
    documentos_cargados: List[DocumentoTransportista]
    faltantes: List[TipoDocumento]


# =========================================
# Modelos de Dador de Carga (Tributario / Facturacion)
# =========================================

class DatosFacturacion(BaseModel):
    razon_social: str = Field(..., min_length=2, description="Razon social o nombre tributario de la empresa")
    direccion: str = Field(..., min_length=3, description="Direccion tributaria")
    correo_facturacion: str = Field(
        ...,
        pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$",
        description="Correo electronico de facturacion",
    )


class CrearPerfilDadorDTO(BaseModel):
    """Payload para registrar o actualizar los datos tributarios del dador de carga."""
    rut_id_empresa: str = Field(..., min_length=3, description="RUT o ID tributario de la empresa")
    datos_facturacion: DatosFacturacion = Field(..., description="Datos de facturacion tributaria")

    @field_validator("rut_id_empresa")
    @classmethod
    def validar_rut_formato(cls, valor: str) -> str:
        valor_limpio = valor.strip().upper().replace(".", "")
        if len(valor_limpio) < 3:
            raise ValueError("El RUT/ID de empresa debe tener al menos 3 caracteres validos")
        return valor_limpio


class ValidarPerfilDadorDTO(BaseModel):
    """Payload para aprobacion o rechazo del perfil dador por Backoffice/Admin."""
    estado_validacion: EstadoValidacion = Field(
        ...,
        description="Nuevo estado de validacion tributaria (APROBADO o RECHAZADO)",
    )


class DadorCarga(BaseModel):
    """Entidad completa del perfil del dador de carga."""
    id: UUID = Field(default_factory=uuid4, description="Identificador unico del perfil dador")
    user_id: UUID = Field(..., description="UUID del usuario dador de carga")
    rut_id_empresa: str = Field(..., description="RUT o ID de empresa")
    datos_facturacion: DatosFacturacion = Field(..., description="Datos de facturacion")
    estado_validacion: EstadoValidacion = Field(
        default=EstadoValidacion.PENDIENTE,
        description="Estado de validacion tributaria",
    )
