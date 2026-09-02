"""
Router HTTP para Autenticacion y Registro de Usuarios.
"""

from fastapi import APIRouter, status
from pydantic import BaseModel, Field

from domain.modelos_usuario import UsuarioCrear, UsuarioModelo
from services.usuario_service import UsuarioService

router = APIRouter(prefix="/auth", tags=["Autenticación"])


class LoginEsquema(BaseModel):
    """Esquema de solicitud JSON para autenticacion de usuario."""
    email: str = Field(..., description="Correo electronico del usuario")
    password: str = Field(..., description="Contrasena del usuario")


@router.post(
    "/registro",
    response_model=UsuarioModelo,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un nuevo usuario",
)
def registrar_usuario(usuario: UsuarioCrear) -> UsuarioModelo:
    """Registra un nuevo usuario en el sistema."""
    return UsuarioService.registrar_usuario(usuario)


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    summary="Autenticación de usuario",
)
def login(payload: LoginEsquema):
    """Autentica a un usuario verificando sus credenciales."""
    usuario = UsuarioService.autenticar_usuario(payload.email, payload.password)
    return {
        "access_token": usuario.email,
        "token_type": "bearer",
        "rol": usuario.rol,
    }