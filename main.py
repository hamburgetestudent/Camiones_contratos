"""Punto de entrada principal para la aplicacion refactorizada de FastAPI.

Configura las rutas modulares y el servidor ASGI.
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database.conexion import inicializar_bd
from routers.auth_router import router as auth_router
from routers.config_router import router as config_router
from routers.contratos_router import router as contratos_router
from routers.onboarding_router import router as onboarding_router
from routers.subasta_router import router as subasta_router


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Prepara la base de datos SQLite (esquema y datos semilla) al iniciar el servidor."""
    inicializar_bd()
    yield


app = FastAPI(
    lifespan=lifespan,
    title="API - Contratos Camiones y Motor de Subastas",
    version="0.1.4",
    description="Backend modular con Autenticación, Motor de Contratos, Postulaciones y Subastas",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusion de routers modulares
app.include_router(auth_router)
app.include_router(config_router)
app.include_router(contratos_router)
app.include_router(onboarding_router)
app.include_router(subasta_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
