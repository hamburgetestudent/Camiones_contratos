"""Servicio de verificación de vigencia y revocación de sesiones JWT."""

from __future__ import annotations

import hashlib
import time
from uuid import UUID

from dao.sesion_dao import SesionDAO, SesionDAOSQLite
from domain.modelos_usuario import UsuarioModelo
from services.security import decodificar_token_acceso
from services.usuario_service import UsuarioService

# DAO persistente por defecto (sustituible por inyección desde dependencies.py).
sesion_dao: SesionDAO = SesionDAOSQLite()


def huella_token(token: str) -> str:
    """Calcula la huella SHA-256 del token para no almacenar credenciales en claro."""
    return hashlib.sha256(token.encode()).hexdigest()


def resolver_usuario_desde_token(token: str) -> UsuarioModelo | None:
    """Valida el JWT, comprueba que no esté revocado y resuelve el usuario vigente."""
    claims = decodificar_token_acceso(token)
    if not isinstance(claims, dict) or not claims.get("sub"):
        return None

    identificador = UUID(str(claims["sub"]))
    with sesion_dao.conexion() as conn:
        revocada = sesion_dao.esta_revocada(conn, huella_token(token))
        usuario = UsuarioService.dao.obtener_por_id(conn, identificador)
        if usuario and not revocada:
            return usuario
    return None


def revocar_token_sesion(token: str) -> None:
    """Registra la huella del token como revocada y purga registros expirados."""
    claims = decodificar_token_acceso(token)
    if not isinstance(claims, dict) or "exp" not in claims:
        return

    with sesion_dao.conexion() as conn:
        sesion_dao.revocar_y_purgar(
            conn,
            huella=huella_token(token),
            expira=int(claims["exp"]),
            ahora=int(time.time()),
        )
