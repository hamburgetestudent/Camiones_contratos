"""Tests para los endpoints y traducción HTTP de routers/auth_router.py."""

from __future__ import annotations

import asyncio
from uuid import uuid4

import httpx
from fastapi import HTTPException

from domain.modelos_login import CredencialesLogin
from domain.modelos_usuario import RolUsuario
from main import app
from routers.auth_router import (
    iniciar_sesion,
    listar_usuarios,
    obtener_usuario,
    registrar_usuario,
)
from tests.usuarios.base import BaseTestUsuarios


def _peticion_http(metodo: str, ruta: str, **kwargs) -> httpx.Response:
    async def _ejecutar() -> httpx.Response:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://testserver",
        ) as cliente:
            return await cliente.request(metodo, ruta, **kwargs)

    return asyncio.run(_ejecutar())


class TestRouterAuth(BaseTestUsuarios):
    """Pruebas dedicadas a los endpoints de routers/auth_router.py."""

    def test_iniciar_sesion_endpoint(self) -> None:
        cred = CredencialesLogin(
            usuario="juan.chofer@transporte.cl", password=self.password_comun
        )
        respuesta = iniciar_sesion(cred)
        self.assertEqual(respuesta.rol, RolUsuario.TRANSPORTISTA.value)
        self.assertEqual(respuesta.token_type.lower(), "bearer")

    def test_registrar_usuario_endpoint(self) -> None:
        dto = self.crear_dto_transportista_valido(email="endpoint.user@correo.cl")
        creado = registrar_usuario(dto)
        self.assertEqual(creado.email, "endpoint.user@correo.cl")

    def test_listar_y_obtener_usuario_endpoint(self) -> None:
        todos = listar_usuarios()
        self.assertGreaterEqual(len(todos), 3)

        recuperado = obtener_usuario(self.usuario_dador.id)
        self.assertEqual(recuperado.id, self.usuario_dador.id)

    def test_endpoint_traduce_correo_duplicado_a_http_400(self) -> None:
        dto = self.crear_dto_transportista_valido(email="juan.chofer@transporte.cl")

        respuesta = _peticion_http(
            "POST", "/auth/registro", json=dto.model_dump(mode="json")
        )

        self.assertEqual(respuesta.status_code, 400)
        self.assertEqual(respuesta.json(), {"detail": "El email ya está registrado"})

    def test_endpoint_traduce_credenciales_invalidas_a_http_401(self) -> None:
        for payload in (
            {"email": "no_existe@correo.cl", "password": self.password_comun},
            {"email": "juan.chofer@transporte.cl", "password": "claveIncorrecta123"},
        ):
            with self.subTest(email=payload["email"]):
                respuesta = _peticion_http("POST", "/auth/login", json=payload)
                self.assertEqual(respuesta.status_code, 401)
                self.assertEqual(
                    respuesta.json(), {"detail": "Credenciales inválidas"}
                )

    def test_endpoint_traduce_usuario_inexistente_a_http_404(self) -> None:
        login = _peticion_http(
            "POST",
            "/auth/login",
            json={
                "email": self.usuario_admin.email,
                "password": self.password_comun,
            },
        )
        self.assertEqual(login.status_code, 200)
        token = login.json()["access_token"]

        respuesta = _peticion_http(
            "GET",
            f"/auth/usuarios/{uuid4()}",
            headers={"Authorization": f"Bearer {token}"},
        )

        self.assertEqual(respuesta.status_code, 404)
        self.assertEqual(respuesta.json(), {"detail": "Usuario no encontrado"})

    def test_endpoint_traduce_campos_vacios_de_login_a_http_400(self) -> None:
        cred = CredencialesLogin.model_construct(usuario="   ", password="")
        with self.assertRaises(HTTPException) as ctx:
            iniciar_sesion(cred)

        self.assertEqual(ctx.exception.status_code, 400)
        self.assertEqual(
            ctx.exception.detail,
            "El correo electrónico y la contraseña son campos obligatorios.",
        )
