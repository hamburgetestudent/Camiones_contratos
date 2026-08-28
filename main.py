"""
Punto de entrada principal para la aplicación refactorizada de FastAPI.
Configura las rutas modulares y el servidor ASGI.
"""

from fastapi import FastAPI

# Importación de los routers del sistema
from routers.config_router import router as config_router
from routers.contratos_router import router as contratos_router
from routers.auth_router import router as auth_router


# Creación de la aplicación FastAPI
app = FastAPI(
    title="API - Contratos Camiones (Refactorizado)",
    version="0.1.0",
    description="Backend modular",
)


# Inclusión de los routers modulares
app.include_router(config_router)
app.include_router(contratos_router)
app.include_router(auth_router)


# Ejecución directa de la aplicación
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )