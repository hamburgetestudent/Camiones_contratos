"""
Utilidades y dependencias compartidas para la capa de Routers HTTP.
Centraliza el manejo homogeneo de errores y la inyeccion tipada de servicios.
"""

from typing import Annotated
from fastapi import Depends, HTTPException, status

from services.contrato_service import ContratoService
from services.dependencies import get_contrato_service, get_subasta_service
from services.subasta_service import SubastaService

# Inyeccion de dependencias tipada con Annotated
ServicioContratoDep = Annotated[ContratoService, Depends(get_contrato_service)]
ServicioSubastaDep = Annotated[SubastaService, Depends(get_subasta_service)]


def manejar_excepcion_http(error: Exception) -> HTTPException:
    """
    Mapea excepciones de dominio, reglas y persistencia a codigos de estado HTTP adecuados.
    """
    mensaje = str(error)
    mensaje_lower = mensaje.lower()

    if any(patron in mensaje_lower for patron in ["no fue encontrad", "no existe", "not found"]):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=mensaje)

    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=mensaje)

