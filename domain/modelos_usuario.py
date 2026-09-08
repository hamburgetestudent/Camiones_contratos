from pydantic import BaseModel, EmailStr, Field
from uuid import UUID, uuid4
from enum import StrEnum

class RolUsuario(StrEnum):
    INDEPENDIENTE = "INDEPENDIENTE"
    EMPRESA = "EMPRESA"
    ADMIN = "ADMIN"

class UsuarioBase(BaseModel):
    nombre: str = Field(..., min_length=2, description="Nombre del usuario")
    email: EmailStr = Field(..., description="Correo electrónico único")
    rol: RolUsuario = Field(default=RolUsuario.GENERADOR, description="Rol del usuario en el sistema")

class UsuarioCrear(UsuarioBase):
    password: str = Field(..., min_length=6, description="Contraseña del usuario")

class UsuarioModelo(UsuarioBase):
    id: UUID = Field(default_factory=uuid4, description="ID único del usuario")
    password_hash: str = Field(..., description="Hash de la contraseña")
