"""Orquestación del inicio de sesión, sin implementar la validación."""

from __future__ import annotations

from typing import Protocol

from domain.modelos_login import CredencialesLogin, RespuestaLogin
from domain.modelos_usuario import UsuarioModelo

# TD-01: Componente reutilizable para construir respuestas de autenticación.
# Se comparte con UsuarioService sin duplicar la generación del token.
from services.respuesta_login import construir_respuesta_login


class ValidadorCredenciales(Protocol):
    """Contrato que debe cumplir el validador de credenciales.

    Gracias a este contrato, el login desacopla la coordinacion de la persistencia directa.
    """

    def validar(self, usuario: str, password: str) -> bool:
        """Indica si la combinación de usuario y contraseña es correcta."""
        ...

    def obtener_datos_usuario(self, usuario: str) -> UsuarioModelo | None:
        """Obtiene la entidad de datos del usuario autenticado si está disponible."""
        ...


class CredencialesInvalidasError(Exception):
    """Señala que el validador rechazó las credenciales recibidas."""


class LoginService:
    """Coordina el login y delega la comprobación de credenciales."""

    def __init__(self, validador: ValidadorCredenciales) -> None:
        self._validador = validador

    def iniciar_sesion(self, credenciales: CredencialesLogin) -> RespuestaLogin:
        """Solicita la validación y construye la respuesta del login con token Bearer."""

        password = credenciales.obtener_password_texto()
        credenciales_validas = self._validador.validar(
            credenciales.usuario,
            password,
        )

        if not credenciales_validas:
            raise CredencialesInvalidasError("Credenciales inválidas")

        datos_usuario: UsuarioModelo | None = None
        if hasattr(self._validador, "obtener_datos_usuario"):
            datos_usuario = self._validador.obtener_datos_usuario(credenciales.usuario)

        # ============================================================
        # TD-01: REFACTORIZACIÓN DE AUTENTICACIÓN
        #
        # Se conserva la validación y la excepción originales.
        # También se permite autenticar sin datos de perfil.
        #
        # La construcción de la respuesta y del token se delega
        # al componente compartido services/respuesta_login.py.
        #
        # El identificador solicitado se conserva para no modificar
        # el comportamiento original de LoginService.
        #
        # Clases aplicadas: 3.1, 3.2 y 3.3.
        # ============================================================
        return construir_respuesta_login(
            datos_usuario=datos_usuario,
            usuario_solicitado=credenciales.usuario,
        )
