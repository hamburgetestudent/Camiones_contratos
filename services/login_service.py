"""Orquestación del inicio de sesión, sin implementar la validación."""

from typing import Protocol

from domain.modelos_login import CredencialesLogin, RespuestaLogin


class ValidadorCredenciales(Protocol):
    """Contrato que debe cumplir el validador creado por el compañero.

    Gracias a este contrato, el login no conoce bases de datos, hashes,
    reglas de contraseña ni otros detalles que pertenecen a validación.
    """

    def validar(self, usuario: str, password: str) -> bool:
        """Indica si la combinación de usuario y contraseña es correcta."""
        ...


class CredencialesInvalidasError(Exception):
    """Señala que el validador rechazó las credenciales recibidas."""


class LoginService:
    """Coordina el login y delega la comprobación de credenciales."""

    def __init__(self, validador: ValidadorCredenciales) -> None:
        self._validador = validador

    def iniciar_sesion(self, credenciales: CredencialesLogin) -> RespuestaLogin:
        """Solicita la validación y construye la respuesta del login.

        Este método no valida por sí mismo el usuario ni la contraseña.
        """

        password = credenciales.password.get_secret_value()
        credenciales_validas = self._validador.validar(
            credenciales.usuario,
            password,
        )

        if not credenciales_validas:
            raise CredencialesInvalidasError

        return RespuestaLogin(
            mensaje="Inicio de sesión exitoso",
            usuario=credenciales.usuario,
        )

