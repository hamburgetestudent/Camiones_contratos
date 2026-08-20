"""
Punto de entrada principal para la aplicacion refactorizada de FastAPI.
Configura las rutas modulares y el servidor ASGI.
"""

from fastapi import FastAPI
from Camiones_contratos.routers.config_router import router as config_router
from Camiones_contratos.routers.contratos_router import router as contratos_router

app = FastAPI(
    title="API - Contratos Camiones (Refactorizado)",
    version="0.1.0",
    description="Backend modular",
)

# Inclusion de routers modulares
app.include_router(config_router)
app.include_router(contratos_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main_borrador:app", host="127.0.0.1", port=8000, reload=True)