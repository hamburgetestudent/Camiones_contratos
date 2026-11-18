"""
Modelos de dominio y esquemas Pydantic para el modulo de Onboarding y Verificacion KYC / Fleet Compliance.
"""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator

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
    archivo: str = Field(
        ..., min_length=3, description="Ruta o referencia simulada al archivo cargado"
    )

    @field_validator("archivo")
    @classmethod
    def validar_archivo(cls, valor: str) -> str:
        extensiones_validas = (".pdf", ".jpg", ".jpeg", ".png")
        if not valor.strip().lower().endswith(extensiones_validas):
            raise ValueError(
                "El formato del archivo debe terminar en .pdf, .jpg, .jpeg o .png"
            )
        return valor


class CargarDocumentoDTO(BaseModel):
    """Payload para la carga simulada de un documento por parte del transportista."""

    tipo: TipoDocumento = Field(..., description="Tipo de documento requerido")
    archivo: str = Field(
        ..., min_length=3, description="Ruta o referencia simulada al archivo cargado"
    )

    @field_validator("archivo")
    @classmethod
    def validar_archivo(cls, valor: str) -> str:
        extensiones_validas = (".pdf", ".jpg", ".jpeg", ".png")
        if not valor.strip().lower().endswith(extensiones_validas):
            raise ValueError(
                "El formato del archivo debe terminar en .pdf, .jpg, .jpeg o .png"
            )
        return valor


class ValidarDocumentoDTO(BaseModel):
    """Payload para aprobacion o rechazo de un documento por Backoffice/Admin."""

    estado: EstadoValidacion = Field(
        ..., description="Nuevo estado del documento (APROBADO o RECHAZADO)"
    )


class DocumentoTransportista(DocumentoTransportistaBase):
    """Entidad completa del documento del transportista."""

    id: UUID = Field(
        default_factory=uuid4, description="Identificador unico del documento"
    )
    user_id: UUID = Field(..., description="UUID del usuario transportista")
    estado: EstadoValidacion = Field(
        default=EstadoValidacion.PENDIENTE, description="Estado de validacion"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Fecha y hora de carga del documento",
    )


class EstadoOnboardingTransportistaDTO(BaseModel):
    """Resumen del estado global de onboarding para un transportista."""

    user_id: UUID
    estado_global: EstadoValidacion
    documentos_requeridos: list[TipoDocumento]
    documentos_cargados: list[DocumentoTransportista]
    faltantes: list[TipoDocumento]


# =========================================
# Modelos de Dador de Carga (Tributario / Facturacion)
# =========================================


class DatosFacturacion(BaseModel):
    razon_social: str = Field(
        ..., min_length=2, description="Razon social o nombre tributario de la empresa"
    )
    direccion: str = Field(..., min_length=3, description="Direccion tributaria")
    correo_facturacion: str = Field(
        ...,
        pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$",
        description="Correo electronico de facturacion",
    )


class CrearPerfilDadorDTO(BaseModel):
    """Payload para registrar o actualizar los datos tributarios del dador de carga."""

    rut_id_empresa: str = Field(
        ..., min_length=3, description="RUT o ID tributario de la empresa"
    )
    datos_facturacion: DatosFacturacion = Field(
        ..., description="Datos de facturacion tributaria"
    )

    @field_validator("rut_id_empresa")
    @classmethod
    def validar_rut_formato(cls, valor: str) -> str:
        valor_limpio = valor.strip().upper().replace(".", "")
        if len(valor_limpio) < 3:
            raise ValueError(
                "El RUT/ID de empresa debe tener al menos 3 caracteres validos"
            )

        rut_sin_guion = valor_limpio.replace("-", "")
        if (
            len(rut_sin_guion) < 7
            or not rut_sin_guion[:-1].isdigit()
            or rut_sin_guion[-1] not in "0123456789K"
        ):
            raise ValueError(
                "Formato de RUT inválido: debe contener entre 7 y 9 dígitos incluyendo el verificador"
            )

        cuerpo = rut_sin_guion[:-1]
        dv_recibido = rut_sin_guion[-1]
        suma = sum(int(c) * (2 + i % 6) for i, c in enumerate(reversed(cuerpo)))
        resto = 11 - (suma % 11)
        dv_esperado = "0" if resto == 11 else ("K" if resto == 10 else str(resto))

        if dv_recibido != dv_esperado:
            raise ValueError(
                f"Dígito verificador del RUT inválido: se esperaba '{dv_esperado}'"
            )

        return valor_limpio


class ValidarPerfilDadorDTO(BaseModel):
    """Payload para aprobacion o rechazo del perfil dador por Backoffice/Admin."""

    estado_validacion: EstadoValidacion = Field(
        ...,
        description="Nuevo estado de validacion tributaria (APROBADO o RECHAZADO)",
    )


class DadorCarga(BaseModel):
    """Entidad completa del perfil del dador de carga."""

    id: UUID = Field(
        default_factory=uuid4, description="Identificador unico del perfil dador"
    )
    user_id: UUID = Field(..., description="UUID del usuario dador de carga")
    rut_id_empresa: str = Field(..., description="RUT o ID de empresa")
    datos_facturacion: DatosFacturacion = Field(..., description="Datos de facturacion")
    estado_validacion: EstadoValidacion = Field(
        default=EstadoValidacion.PENDIENTE,
        description="Estado de validacion tributaria",
    )
