"""Endpoint HTTP para iniciar sesión con usuario y contraseña."""

from fastapi import APIRouter, HTTPException, status

from domain.modelos_login import CredencialesLogin, RespuestaLogin
from services.login_service import (
    CredencialesInvalidasError,
    LoginService,
    ValidadorCredenciales,
)


def crear_login_router(validador: ValidadorCredenciales) -> APIRouter:
    """Crea el router del login conectado al validador del equipo.

    Recibir el validador como dependencia mantiene separadas las tareas:
    este módulo administra el login y otro módulo decide si las
    credenciales son correctas.
    """

    router = APIRouter(prefix="/auth", tags=["Autenticación"])
    servicio = LoginService(validador)

    @router.post(
        "/login",
        response_model=RespuestaLogin,
        status_code=status.HTTP_200_OK,
        summary="Iniciar sesión con usuario y contraseña",
        responses={
            status.HTTP_401_UNAUTHORIZED: {
                "description": "Usuario o contraseña incorrectos"
            }
        },
    )
    def iniciar_sesion(credenciales: CredencialesLogin) -> RespuestaLogin:
        """Recibe credenciales y delega su comprobación al validador."""

        try:
            return servicio.iniciar_sesion(credenciales)
        except CredencialesInvalidasError as error:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario o contraseña incorrectos",
            ) from error

    return router

