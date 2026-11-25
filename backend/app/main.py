"""Punto de entrada principal para la aplicacion refactorizada de FastAPI.

Configura las rutas modulares y el servidor ASGI.
"""

import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.db.conexion import inicializar_bd
from app.modules.admin.router import router as admin_router
from app.modules.configuracion.router import router as config_router
from app.modules.contratos.router import router as contratos_router
from app.modules.onboarding.router import router as onboarding_router
from app.modules.subastas.router import router as subasta_router
from app.modules.usuarios.router import router as auth_router
from app.modules.usuarios.sesion import usuario_actual


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
app.include_router(admin_router)
# Toda ruta de negocio comprueba la vigencia de la cuenta en cada solicitud.
for modulo in (config_router, contratos_router, onboarding_router, subasta_router):
    app.include_router(modulo, dependencies=[Depends(usuario_actual)])

FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend" / "src"
FRONTEND_PAGINAS_DIR = FRONTEND_DIR / "paginas"
FRONTEND_COMPARTIDO_DIR = FRONTEND_DIR / "compartido"
FRONTEND_IMAGENES_DIR = FRONTEND_DIR / "recursos" / "imagenes"


@app.get("/", include_in_schema=False)
def raiz() -> RedirectResponse:
    """Redirige la raíz del sitio web hacia la vista de inicio de sesión."""
    return RedirectResponse(url="/login/login.html")


if FRONTEND_IMAGENES_DIR.is_dir():
    app.mount(
        "/imagenes",
        StaticFiles(directory=str(FRONTEND_IMAGENES_DIR)),
        name="imagenes",
    )

if FRONTEND_COMPARTIDO_DIR.is_dir():
    # Las páginas piden ../../compartido/..., que en la web se resuelve a /compartido/...
    app.mount(
        "/compartido",
        StaticFiles(directory=str(FRONTEND_COMPARTIDO_DIR)),
        name="compartido",
    )

if FRONTEND_PAGINAS_DIR.is_dir():
    app.mount(
        "/",
        StaticFiles(directory=str(FRONTEND_PAGINAS_DIR), html=True),
        name="frontend",
    )


if __name__ == "__main__":
    import uvicorn

    port_env = os.environ.get("PORT")
    host = os.environ.get("HOST", "0.0.0.0" if port_env else "127.0.0.1")
    port = int(port_env) if port_env else 8000
    uvicorn.run("app.main:app", host=host, port=port, reload=port_env is None)
