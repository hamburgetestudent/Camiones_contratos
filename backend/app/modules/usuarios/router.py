"""Router HTTP para Autenticacion y Registro de Usuarios."""

from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.modules.usuarios.models import UsuarioCrear, UsuarioModelo
from app.modules.usuarios.models_login import CredencialesLogin, RespuestaLogin
from app.modules.usuarios.service import UsuarioService
from app.modules.usuarios.sesion import (
    Bearer,
    UsuarioActual,
    administrador_actual,
    cerrar_sesion,
    usuario_actual,
)

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.get("/sesion")
def consultar_sesion(usuario: UsuarioActual):
    return {
        "id": usuario.id,
        "nombre": usuario.nombre,
        "email": usuario.email,
        "rol": usuario.rol,
    }


@router.post("/logout", status_code=204, dependencies=[Depends(usuario_actual)])
def salir(bearer: Bearer):
    cerrar_sesion(bearer)


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
    dependencies=[Depends(administrador_actual)],
    response_model=list[UsuarioModelo],
    status_code=status.HTTP_200_OK,
    summary="Listar todos los usuarios registrados",
)
def listar_usuarios() -> list[UsuarioModelo]:
    """Obtiene la lista de todos los usuarios y correos registrados en SQLite."""
    return UsuarioService.listar_usuarios()


@router.get(
    "/usuarios/{usuario_id}",
    dependencies=[Depends(administrador_actual)],
    response_model=UsuarioModelo,
    status_code=status.HTTP_200_OK,
    summary="Obtener un usuario por su UUID",
)
def obtener_usuario(usuario_id: UUID) -> UsuarioModelo:
    """Busca un usuario específico por su identificador único."""
    return UsuarioService.obtener_usuario(usuario_id)
