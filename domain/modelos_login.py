"""Modelos que forman el contrato HTTP del inicio de sesión."""

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, SecretStr


class CredencialesLogin(BaseModel):
    """Datos que el cliente debe enviar al endpoint de login.

    No contiene reglas de negocio: la validación de las credenciales se
    delega al componente que desarrollará el compañero responsable.
    """

    model_config = ConfigDict(populate_by_name=True)

    usuario: str = Field(..., validation_alias=AliasChoices("usuario", "email"))
    password: SecretStr


class RespuestaLogin(BaseModel):
    """Respuesta básica entregada cuando el validador acepta el acceso."""

    mensaje: str
    usuario: str
    id: str | None = None
    nombre: str | None = None
    email: str | None = None
    rol: str | None = None
    estado: str | None = None

