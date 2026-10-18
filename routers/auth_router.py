"""Router HTTP para Autenticacion y Registro de Usuarios."""

from uuid import UUID

from fastapi import APIRouter, status
from pydantic import BaseModel, ConfigDict, Field

from domain.modelos_usuario import UsuarioCrear, UsuarioModelo
from services.usuario_service import UsuarioService

router = APIRouter(prefix="/auth", tags=["Autenticación"])


class LoginEsquema(BaseModel):
    """Esquema de solicitud JSON para autenticacion de usuario en el sistema.

    Attributes:
        email (str): Correo electronico registrado del usuario (formato estandar RFC 5322).
        password (str): Clave secreta en texto plano enviada por canal seguro HTTPS para comprobacion.
    """

    email: str = Field(..., description="Correo electronico del usuario")
    password: str = Field(..., description="Contrasena del usuario")

    model_config = ConfigDict(extra="forbid")


@router.post(
    "/registro",
    response_model=UsuarioModelo,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un nuevo usuario",
)
def registrar_usuario(usuario: UsuarioCrear) -> UsuarioModelo:
    """Registra un nuevo usuario en la base de datos SQLite."""
    return UsuarioService.registrar_usuario(usuario)


@router.get(
    "/usuarios",
    response_model=list[UsuarioModelo],
    status_code=status.HTTP_200_OK,
    summary="Listar todos los usuarios registrados",
)
def listar_usuarios() -> list[UsuarioModelo]:
    """Obtiene la lista de todos los usuarios y correos registrados en SQLite."""
    return UsuarioService.listar_usuarios()


@router.get(
    "/usuarios/{usuario_id}",
    response_model=UsuarioModelo,
    status_code=status.HTTP_200_OK,
    summary="Obtener un usuario por su UUID",
)
def obtener_usuario(usuario_id: UUID) -> UsuarioModelo:
    """Busca un usuario específico por su identificador único."""
    return UsuarioService.obtener_usuario(usuario_id)

