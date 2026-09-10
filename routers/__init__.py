"""
Modulo de Routers FastAPI para exponer los endpoints HTTP de la aplicacion.
Centraliza y reexporta los enrutadores modulares.
"""

from routers.auth_router import router as auth_router
from routers.config_router import router as config_router
from routers.contratos_router import router as contratos_router
from routers.login_router import crear_login_router
from routers.onboarding_router import router as onboarding_router
from routers.subasta_router import router as subasta_router

__all__ = [
    "auth_router",
    "config_router",
    "contratos_router",
    "crear_login_router",
    "onboarding_router",
    "subasta_router",
]
