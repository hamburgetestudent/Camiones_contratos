"""Dependencias HTTP de identidad Bearer y cierre de sesión."""

from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from domain.modelos_usuario import RolUsuario, UsuarioModelo
from services.sesion_service import (
    resolver_usuario_desde_token,
    revocar_token_sesion,
)

Bearer = Annotated[
    HTTPAuthorizationCredentials | None, Depends(HTTPBearer(auto_error=False))
]


def usuario_actual(bearer: Bearer) -> UsuarioModelo:
    if bearer:
        try:
            usuario = resolver_usuario_desde_token(bearer.credentials)
        except ValueError:
            raise HTTPException(401, "Sesión inválida.") from None
        if usuario:
            return usuario
    raise HTTPException(
        401, "Inicia sesión nuevamente.", headers={"WWW-Authenticate": "Bearer"}
    )


UsuarioActual = Annotated[UsuarioModelo, Depends(usuario_actual)]


def administrador_actual(usuario: UsuarioActual) -> UsuarioModelo:
    if usuario.rol != RolUsuario.ADMIN_BACKOFFICE:
        raise HTTPException(403, "Se requiere una cuenta administradora.")
    return usuario


Administrador = Annotated[UsuarioModelo, Depends(administrador_actual)]


def cerrar_sesion(bearer: Bearer) -> None:
    """Revoca solo la sesión presentada delegando la persistencia al servicio."""
    if bearer:
        revocar_token_sesion(bearer.credentials)
