from typing import Optional, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator

from domain.modelos_onboarding import (
    CargarDocumentoDTO,
    CrearPerfilDadorDTO,
    DatosFacturacion,
)

try:
    from enum import StrEnum
except ImportError:
    from enum import Enum

    class StrEnum(str, Enum):  # noqa: UP042
        pass


class RolUsuario(StrEnum):
    TRANSPORTISTA = "TRANSPORTISTA"
    DADOR_CARGA = "DADOR_CARGA"
    ADMIN_BACKOFFICE = "ADMIN_BACKOFFICE"
    EMPRESA = "EMPRESA"
    INDEPENDIENTE = "INDEPENDIENTE"

class EstadoUsuario(StrEnum):
    EN_REVISION = "EN_REVISION"
    APROBADO = "APROBADO"

class UsuarioBase(BaseModel):
    nombre: str = Field(..., min_length=2, description="Nombre del usuario")
    email: str = Field(..., pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$", description="Correo electrónico único")
    rol: RolUsuario = Field(..., description="Rol del usuario en el sistema")


class UsuarioCrear(UsuarioBase):
    password: str = Field(..., min_length=6, description="Contrasena del usuario")
    documentos: Optional[list[CargarDocumentoDTO]] = Field(
        default=None,
        description="Lista de documentos si es transportista",
    )
    perfil_tributario: Optional[Union[CrearPerfilDadorDTO, DatosFacturacion]] = Field(
        default=None,
        description="Datos de facturación o perfil tributario si es dador de carga",
    )

    @field_validator("rol")
    @classmethod
    def validar_rol(cls, v: RolUsuario) -> RolUsuario:
        if v not in (RolUsuario.TRANSPORTISTA, RolUsuario.DADOR_CARGA):
            raise ValueError("El rol al registrarse solo puede ser TRANSPORTISTA o DADOR_CARGA")
        return v


class UsuarioModelo(UsuarioBase):
    id: UUID = Field(default_factory=uuid4, description="ID unico del usuario")
    password_hash: str = Field(..., description="Hash de la contrasena")
    estado: EstadoUsuario = Field(default=EstadoUsuario.EN_REVISION, description="Estado del usuario en el sistema")