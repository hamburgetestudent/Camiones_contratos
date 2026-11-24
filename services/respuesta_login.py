"""TD-01: Componente reutilizable de respuestas de autenticación.

Unidad 3 - Refactorización y modularización.

Este módulo centraliza la construcción de respuestas de inicio
de sesión para eliminar código duplicado entre los servicios.

Clases aplicadas:
3.1 - Refactorización sistemática.
3.2 - Identificación de deuda técnica.
3.3 - Construcción para reutilización.
"""

from __future__ import annotations

from domain.modelos_login import RespuestaLogin
from domain.modelos_usuario import UsuarioModelo
from services.security import crear_token_acceso


def construir_respuesta_login(
    datos_usuario: UsuarioModelo | None,
    usuario_solicitado: str,
) -> RespuestaLogin:
    """Construye una respuesta de autenticación con token Bearer.

    Parámetros:
        datos_usuario: Perfil autenticado, o None si no está disponible.
        usuario_solicitado: Identificador que mostrará la respuesta.

    Retorna:
        RespuestaLogin con el token y los datos del usuario.

    TD-01:
        Los servicios seguirán siendo responsables de validar
        credenciales y manejar sus respectivas excepciones.
    """

    # TD-01: Valores predeterminados cuando no existe un perfil.
    rol = "USUARIO"
    identificador = None
    nombre = None
    correo = usuario_solicitado
    estado = None

    # TD-01: Obtener los datos disponibles del usuario autenticado.
    if datos_usuario is not None:
        identificador = str(datos_usuario.id)
        nombre = datos_usuario.nombre
        correo = datos_usuario.email

        # Convertir el rol a texto para la respuesta y el token.
        rol_objeto = datos_usuario.rol
        rol = rol_objeto.value if hasattr(rol_objeto, "value") else str(rol_objeto)

        # Convertir el estado del usuario a texto.
        estado_objeto = datos_usuario.estado
        estado = (
            estado_objeto.value
            if hasattr(estado_objeto, "value")
            else str(estado_objeto)
        )

    # TD-01: Reutilizar la función de seguridad existente.
    # No modificamos el algoritmo de creación de tokens.
    token = crear_token_acceso(
        {
            "sub": identificador or correo,
            "email": correo,
            "rol": rol,
        }
    )

    # TD-01: Construir la respuesta desde un único componente.
    return RespuestaLogin(
        access_token=token,
        token_type="bearer",
        rol=rol,
        mensaje="Inicio de sesión exitoso",
        usuario=usuario_solicitado,
        id=identificador,
        nombre=nombre,
        email=correo,
        estado=estado,
    )
