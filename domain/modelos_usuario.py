from enum import StrEnum
import re
from typing import Annotated
from uuid import UUID, uuid4
from pydantic import BaseModel, ConfigDict, Field, field_validator

PATRON_EMAIL = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")


class RolUsuario(StrEnum):
    GENERADOR = "GENERADOR"
    TRANSPORTISTA = "TRANSPORTISTA"
    EMPRESA = "EMPRESA"
    INDEPENDIENTE = "INDEPENDIENTE"
    ADMIN = "ADMIN"


class UsuarioBase(BaseModel):
    nombre: str = Field(..., min_length=2, description="Nombre del usuario")
    email: str = Field(..., description="Correo electronico unico del usuario")
    rol: RolUsuario = Field(default=RolUsuario.GENERADOR, description="Rol del usuario en el sistema")

    model_config = ConfigDict(str_strip_whitespace=True)

    @field_validator("email")
    @classmethod
    def validar_email(cls, v: str) -> str:
        email_limpio = v.strip().lower()
        if not PATRON_EMAIL.match(email_limpio):
            raise ValueError("Formato de correo electronico invalido")
        return email_limpio


class UsuarioCrear(UsuarioBase):
    password: str = Field(..., min_length=6, description="Contrasena del usuario")


class UsuarioModelo(UsuarioBase):
    id: UUID = Field(default_factory=uuid4, description="ID unico del usuario")
    password_hash: str = Field(..., description="Hash de la contrasena")
