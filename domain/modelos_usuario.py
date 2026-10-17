from __future__ import annotations

from typing import Any, Optional, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator

from domain.modelos_onboarding import (
    CargarDocumentoDTO,
    CrearPerfilDadorDTO,
    DatosFacturacion,
)

import sys

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
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

    def __init__(
        self,
        *,
        nombre: Any = ...,
        email: Any = ...,
        rol: Any = ...,
        password: Any = ...,
        documentos: Any = None,
        perfil_tributario: Any = None,
        **kwargs: Any,
    ) -> None:
        data: dict[str, Any] = {}
        if nombre is not ...:
            data["nombre"] = nombre
        if email is not ...:
            data["email"] = email
        if rol is not ...:
            data["rol"] = rol
        if password is not ...:
            data["password"] = password
        if documentos is not None:
            data["documentos"] = documentos
        if perfil_tributario is not None:
            data["perfil_tributario"] = perfil_tributario
        data.update(kwargs)
        super().__init__(**data)

    @field_validator("rol", mode="before")
    @classmethod
    def normalizar_rol_entrada(cls, v: object) -> object:
        if isinstance(v, str):
            valor = v.strip().upper()
            if valor == "INDEPENDIENTE":
                return RolUsuario.TRANSPORTISTA
            if valor == "EMPRESA":
                return RolUsuario.DADOR_CARGA
            return valor
        return v

    @field_validator("rol")
    @classmethod
    def validar_rol(cls, v: RolUsuario) -> RolUsuario:
        if v == RolUsuario.INDEPENDIENTE:
            return RolUsuario.TRANSPORTISTA
        if v == RolUsuario.EMPRESA:
            return RolUsuario.DADOR_CARGA
        if v not in (RolUsuario.TRANSPORTISTA, RolUsuario.DADOR_CARGA):
            raise ValueError("El rol al registrarse solo puede ser TRANSPORTISTA o DADOR_CARGA")
        return v


class UsuarioModelo(UsuarioBase):
    id: UUID = Field(default_factory=uuid4, description="ID unico del usuario")
    password_hash: str = Field(..., description="Hash de la contrasena")
    estado: EstadoUsuario = Field(default=EstadoUsuario.EN_REVISION, description="Estado del usuario en el sistema")