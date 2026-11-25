"""Modelos que forman el contrato HTTP del inicio de sesión."""

from __future__ import annotations

from typing import Any, Union

from pydantic import (
    AliasChoices,
    BaseModel,
    ConfigDict,
    Field,
    SecretStr,
    field_validator,
)


class CredencialesLogin(BaseModel):
    """Datos que el cliente debe enviar al endpoint de login.

    Valida que los campos obligatorios esten presentes y no esten vacios.
    """

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    usuario: str = Field(
        ...,
        description="Correo electronico o identificador de usuario",
        validation_alias=AliasChoices("usuario", "email"),
    )
    password: Union[SecretStr, str] = Field(
        ...,
        description="Contrasena secreta del usuario",
    )

    @field_validator("usuario", mode="before")
    @classmethod
    def validar_usuario_obligatorio(cls, v: Any) -> str:
        if v is None or not str(v).strip():
            raise ValueError("El correo electrónico es un campo obligatorio.")
        return str(v).strip()

    @field_validator("password", mode="before")
    @classmethod
    def validar_password_obligatorio(cls, v: Any) -> str:
        if isinstance(v, SecretStr):
            v = v.get_secret_value()
        if v is None or not str(v).strip():
            raise ValueError("La contraseña es un campo obligatorio.")
        return str(v)

    def obtener_password_texto(self) -> str:
        """Devuelve la contrasena en texto plano para verificacion de hash."""
        if isinstance(self.password, SecretStr):
            return self.password.get_secret_value()
        return str(self.password)


class LoginEsquema(CredencialesLogin):
    """Esquema de solicitud JSON para autenticacion en routers/auth_router.py."""

    model_config = ConfigDict(populate_by_name=True, extra="ignore")


class RespuestaLogin(BaseModel):
    """Respuesta emitida tras una autenticacion exitosa conforme a OAuth2 Bearer."""

    access_token: str = Field(..., description="Token de acceso OAuth2 Bearer firmado")
    token_type: str = Field(
        default="bearer", description="Tipo de credencial emitida segun estandar OAuth2"
    )
    rol: str = Field(..., description="Rol asignado al usuario en el sistema")
    mensaje: str = Field(
        default="Inicio de sesión exitoso", description="Mensaje de confirmacion"
    )
    usuario: str = Field(
        ..., description="Identificador o correo del usuario autenticado"
    )
    id: str | None = Field(
        default=None, description="Identificador unico UUID del usuario"
    )
    nombre: str | None = Field(
        default=None, description="Nombre registrado del usuario"
    )
    email: str | None = Field(
        default=None, description="Correo electronico verificado del usuario"
    )
    estado: str | None = Field(
        default=None, description="Estado operativo de la cuenta"
    )
