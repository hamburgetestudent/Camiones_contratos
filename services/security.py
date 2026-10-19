"""Modulo de seguridad y emision de tokens OAuth2 Bearer.

Implementa generacion y decodificacion de JSON Web Tokens (JWT)
utilizando el algoritmo estandar HS256 con librerias nativas de Python
(hmac, hashlib, base64) para garantizar portabilidad y cero dependencias externas.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import time
from typing import Any

# Clave secreta configurable por variable de entorno o clave por defecto para desarrollo
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "secreto_super_seguro_plataforma_camiones_2026")
ALGORITMO = "HS256"
EXPIRACION_DEFAULT_MINUTOS = 60 * 8  # 8 horas de sesion


def _base64url_encode(datos: bytes) -> str:
    """Codifica bytes en formato base64url sin padding '='."""
    return base64.urlsafe_b64encode(datos).decode("utf-8").rstrip("=")


def _base64url_decode(cadena: str) -> bytes:
    """Decodifica una cadena base64url agregando el padding necesario."""
    padding = "=" * (-len(cadena) % 4)
    return base64.urlsafe_b64decode(cadena + padding)


def crear_token_acceso(
    claims: dict[str, Any],
    expiracion_minutos: int = EXPIRACION_DEFAULT_MINUTOS,
    clave_secreta: str = SECRET_KEY,
) -> str:
    """Genera un token de acceso OAuth2 Bearer firmado con HS256.

    Args:
        claims: Diccionario con la informacion a codificar (sub, email, rol, etc.).
        expiracion_minutos: Minutos de vigencia del token.
        clave_secreta: Clave simetrica para la firma HMAC-SHA256.

    Returns:
        Token JWT en formato 'header.payload.signature'.
    """
    ahora = int(time.time())
    payload = dict(claims)
    payload.setdefault("iat", ahora)
    payload.setdefault("exp", ahora + (expiracion_minutos * 60))
    payload.setdefault("iss", "camiones_contratos_iam")

    header = {
        "alg": ALGORITMO,
        "typ": "JWT",
    }

    header_bytes = json.dumps(header, separators=(",", ":"), sort_keys=True).encode("utf-8")
    payload_bytes = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")

    header_b64 = _base64url_encode(header_bytes)
    payload_b64 = _base64url_encode(payload_bytes)

    contenido_a_firmar = f"{header_b64}.{payload_b64}".encode("utf-8")
    firma = hmac.new(clave_secreta.encode("utf-8"), contenido_a_firmar, hashlib.sha256).digest()
    firma_b64 = _base64url_encode(firma)

    return f"{header_b64}.{payload_b64}.{firma_b64}"


def decodificar_token_acceso(
    token: str,
    clave_secreta: str = SECRET_KEY,
) -> dict[str, Any] | None:
    """Valida y decodifica un token JWT Bearer.

    Args:
        token: Cadena con el token 'header.payload.signature'.
        clave_secreta: Clave secreta para verificar la firma.

    Returns:
        Diccionario con las claims si el token es valido y no ha expirado; None en caso contrario.
    """
    try:
        partes = token.strip().split(".")
        if len(partes) != 3:
            return None

        header_b64, payload_b64, firma_b64 = partes
        contenido_a_firmar = f"{header_b64}.{payload_b64}".encode("utf-8")

        firma_esperada = hmac.new(clave_secreta.encode("utf-8"), contenido_a_firmar, hashlib.sha256).digest()
        firma_recibida = _base64url_decode(firma_b64)

        if not hmac.compare_digest(firma_esperada, firma_recibida):
            return None

        payload_bytes = _base64url_decode(payload_b64)
        payload = json.loads(payload_bytes.decode("utf-8"))

        # Validar expiracion
        exp = payload.get("exp")
        if exp is not None and int(exp) < int(time.time()):
            return None

        return payload
    except Exception:
        return None

