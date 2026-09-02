"""
Punto de entrada principal para la aplicacion refactorizada de FastAPI.
Configura las rutas modulares y el servidor ASGI.
"""

from fastapi import FastAPI
from routers.config_router import router as config_router
from routers.contratos_router import router as contratos_router
from routers.auth_router import router as auth_router
from routers.login_router import crear_login_router
from services.usuario_service import ValidadorUsuario

app = FastAPI(
    title="API - Contratos Camiones (Refactorizado)",
    version="0.1.0",
    description="Backend modular",
)

# Inclusion de routers modulares
app.include_router(auth_router)
app.include_router(crear_login_router(ValidadorUsuario()))
app.include_router(config_router)
app.include_router(contratos_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)