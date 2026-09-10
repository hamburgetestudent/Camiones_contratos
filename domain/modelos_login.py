"""Modelos que forman el contrato HTTP del inicio de sesión."""

from pydantic import BaseModel, SecretStr


class CredencialesLogin(BaseModel):
    """Datos que el cliente debe enviar al endpoint de login.

    No contiene reglas de negocio: la validación de las credenciales se
    delega al componente que desarrollará el compañero responsable.
    """

    usuario: str
    password: SecretStr


class RespuestaLogin(BaseModel):
    """Respuesta básica entregada cuando el validador acepta el acceso."""

    mensaje: str
    usuario: str
