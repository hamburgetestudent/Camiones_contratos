"""
Modulo de Routers FastAPI para exponer los endpoints HTTP de la aplicacion.
Centraliza y reexporta los enrutadores modulares.
"""

from routers.config_router import router as config_router
from routers.contratos_router import router as contratos_router
from routers.subasta_router import router as subasta_router

__all__ = [
    "config_router",
    "contratos_router",
    "subasta_router",
]
