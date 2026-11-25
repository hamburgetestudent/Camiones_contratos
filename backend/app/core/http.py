"""
Utilidades y dependencias compartidas para la capa de Routers HTTP.
Centraliza el manejo homogeneo de errores y la inyeccion tipada de servicios.
"""

from typing import Annotated

from fastapi import Depends, HTTPException, status

from app.core.dependencies import get_contrato_service, get_subasta_service
from app.modules.contratos.service import ContratoService
from app.modules.subastas.service import SubastaService

# Inyeccion de dependencias tipada con Annotated
ServicioContratoDep = Annotated[ContratoService, Depends(get_contrato_service)]
ServicioSubastaDep = Annotated[SubastaService, Depends(get_subasta_service)]


def manejar_excepcion_http(error: Exception) -> HTTPException:
    """
    Mapea excepciones de dominio, reglas y persistencia a codigos de estado HTTP adecuados.
    """
    if isinstance(error, HTTPException):
        return error

    mensaje = str(error)
    mensaje_minuscula = mensaje.lower()

    if any(
        patron in mensaje_minuscula
        for patron in ["no fue encontrad", "no existe", "not found"]
    ):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=mensaje)

    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=mensaje)


def confirmar_operacion(operar, *argumentos):
    try:
        operacion, causa = operar(*argumentos)
    except PermissionError as error:
        raise HTTPException(403, str(error)) from error
    if causa:
        raise HTTPException(409, causa)
    return {"operacion_id": operacion}
