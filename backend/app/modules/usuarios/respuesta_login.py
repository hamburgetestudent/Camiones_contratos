"""Construccion de respuestas de autenticacion."""

from app.core.security import crear_token_acceso
from app.modules.usuarios.models import UsuarioModelo
from app.modules.usuarios.models_login import RespuestaLogin


def construir_respuesta_login(usuario: UsuarioModelo) -> RespuestaLogin:
    """Construye la respuesta de un usuario autenticado."""
    rol_valor = (
        usuario.rol.value if hasattr(usuario.rol, "value") else str(usuario.rol)
    )
    estado_valor = (
        usuario.estado.value
        if hasattr(usuario.estado, "value")
        else str(usuario.estado)
    )

    access_token = crear_token_acceso(
        {
            "sub": str(usuario.id),
            "email": usuario.email,
            "rol": rol_valor,
        }
    )

    return RespuestaLogin(
        access_token=access_token,
        token_type="bearer",
        rol=rol_valor,
        mensaje="Inicio de sesión exitoso",
        usuario=usuario.email,
        id=str(usuario.id),
        nombre=usuario.nombre,
        email=usuario.email,
        estado=estado_valor,
    )
