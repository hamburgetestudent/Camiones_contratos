"""Identidad resuelta desde el Bearer y la cuenta vigente en SQLite."""

import hashlib
import time
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from database.conexion import obtener_conexion
from domain.modelos_usuario import RolUsuario, UsuarioModelo
from services.security import decodificar_token_acceso
from services.usuario_service import buscar_usuario_por_id

Bearer = Annotated[
    HTTPAuthorizationCredentials | None, Depends(HTTPBearer(auto_error=False))
]


def _huella(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def usuario_actual(bearer: Bearer) -> UsuarioModelo:
    claims = decodificar_token_acceso(bearer.credentials) if bearer else None
    if isinstance(claims, dict) and claims.get("sub"):
        try:
            identificador = UUID(str(claims["sub"]))
        except ValueError:
            raise HTTPException(401, "Sesión inválida.") from None
        with obtener_conexion() as conn:
            cerrada = conn.execute(
                "SELECT 1 FROM sesiones_cerradas WHERE huella=?",
                (_huella(bearer.credentials),),
            ).fetchone()
            usuario = buscar_usuario_por_id(conn, identificador)
            if usuario and not cerrada:
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


def cerrar_sesion(bearer: Bearer):
    """Revoca solo la sesión presentada. La tabla guarda huellas, nunca tokens."""
    claims = decodificar_token_acceso(bearer.credentials)
    with obtener_conexion() as conn:
        conn.execute(
            "DELETE FROM sesiones_cerradas WHERE expira < ?", (int(time.time()),)
        )
        conn.execute(
            "INSERT OR IGNORE INTO sesiones_cerradas VALUES (?,?)",
            (_huella(bearer.credentials), claims["exp"]),
        )
