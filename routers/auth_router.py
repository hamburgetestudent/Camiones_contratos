"""Router HTTP para Autenticacion y Registro de Usuarios."""

from uuid import UUID

from fastapi import APIRouter, status

from domain.modelos_login import CredencialesLogin, LoginEsquema, RespuestaLogin
from domain.modelos_usuario import UsuarioCrear, UsuarioModelo
from services.usuario_service import UsuarioService

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post(
    "/login",
    response_model=RespuestaLogin,
    status_code=status.HTTP_200_OK,
    summary="Iniciar sesión con correo electrónico y contraseña",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Credenciales inválidas"},
        status.HTTP_400_BAD_REQUEST: {"description": "Campos obligatorios incompletos"},
    },
)
def iniciar_sesion(credenciales: CredencialesLogin) -> RespuestaLogin:
    """Autentica a un usuario registrado mediante correo electronico y contrasena, emitiendo token Bearer."""
    return UsuarioService.iniciar_sesion(credenciales)


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
