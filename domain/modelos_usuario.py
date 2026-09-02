from pydantic import BaseModel, EmailStr, Field
from uuid import UUID, uuid4
from enum import StrEnum

class RolUsuario(StrEnum):
    TRANSPORTISTA = "TRANSPORTISTA"
    DADOR_CARGA = "DADOR_CARGA"
    ADMIN_BACKOFFICE = "ADMIN_BACKOFFICE"
    GENERADOR = "DADOR_CARGA"
    ADMIN = "ADMIN_BACKOFFICE"
    EMPRESA = "EMPRESA"
    INDEPENDIENTE = "INDEPENDIENTE"

class UsuarioBase(BaseModel):
    nombre: str = Field(..., min_length=2, description="Nombre del usuario")
    email: str = Field(..., pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$", description="Correo electrónico único")
    rol: RolUsuario = Field(default=RolUsuario.DADOR_CARGA, description="Rol del usuario en el sistema")

class UsuarioCrear(UsuarioBase):
    password: str = Field(..., min_length=6, description="Contraseña del usuario")

class UsuarioModelo(UsuarioBase):
    id: UUID = Field(default_factory=uuid4, description="ID único del usuario")
    password_hash: str = Field(..., description="Hash de la contraseña")
