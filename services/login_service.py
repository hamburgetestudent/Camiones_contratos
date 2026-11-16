"""Orquestación del inicio de sesión, sin implementar la validación."""

from __future__ import annotations

from typing import Protocol

from domain.modelos_login import CredencialesLogin, RespuestaLogin
from domain.modelos_usuario import UsuarioModelo
from services.security import crear_token_acceso


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

        rol_valor = "USUARIO"
        user_id: str | None = None
        nombre: str | None = None
        email: str = credenciales.usuario
        estado: str | None = None

        if datos_usuario is not None:
            user_id = str(datos_usuario.id)
            nombre = datos_usuario.nombre
            email = datos_usuario.email
            rol_obj = datos_usuario.rol
            rol_valor = rol_obj.value if hasattr(rol_obj, "value") else str(rol_obj)
            estado_obj = datos_usuario.estado
            estado = (
                estado_obj.value if hasattr(estado_obj, "value") else str(estado_obj)
            )

        access_token = crear_token_acceso(
            {
                "sub": user_id or email,
                "email": email,
                "rol": rol_valor,
            }
        )

        return RespuestaLogin(
            access_token=access_token,
            token_type="bearer",
            rol=rol_valor,
            mensaje="Inicio de sesión exitoso",
            usuario=credenciales.usuario,
            id=user_id,
            nombre=nombre,
            email=email,
            estado=estado,
        )
