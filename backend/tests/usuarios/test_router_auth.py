"""Tests para los endpoints y traducción HTTP de app/modules/usuarios/router.py."""

from __future__ import annotations

import json
import socket
import threading
import time
from contextlib import closing, contextmanager
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from uuid import uuid4

import uvicorn
from fastapi import HTTPException

from app.main import app
from app.modules.usuarios.models import RolUsuario
from app.modules.usuarios.models_login import CredencialesLogin
from app.modules.usuarios.router import (
    iniciar_sesion,
    listar_usuarios,
    obtener_usuario,
    registrar_usuario,
)
from tests.usuarios.base import BaseTestUsuarios


@contextmanager
def _servidor_http():
    """Levanta la app FastAPI en un puerto local libre usando solo stdlib + uvicorn."""
    with closing(socket.socket()) as puerto:
        puerto.bind(("127.0.0.1", 0))
        base = f"http://127.0.0.1:{puerto.getsockname()[1]}"
        servidor = uvicorn.Server(
            uvicorn.Config(app, log_level="error", access_log=False)
        )
        hilo = threading.Thread(
            target=servidor.run, kwargs={"sockets": [puerto]}, daemon=True
        )
        hilo.start()
        try:
            for _ in range(100):
                if servidor.started:
                    break
                time.sleep(0.02)

            def solicitar(
                metodo: str,
                ruta: str,
                datos: dict | None = None,
                token: str | None = None,
            ) -> tuple[int, dict]:
                cabeceras = {"Content-Type": "application/json"}
                if token:
                    cabeceras["Authorization"] = f"Bearer {token}"
                req = Request(
                    base + ruta,
                    method=metodo,
                    headers=cabeceras,
                    data=json.dumps(datos).encode() if datos is not None else None,
                )
                try:
                    with urlopen(req, timeout=3) as resp:
                        return resp.status, json.loads(resp.read() or b"null")
                except HTTPError as error:
                    with error:
                        return error.code, json.load(error)

            yield solicitar
        finally:
            servidor.should_exit = True
            hilo.join(timeout=3)


class TestRouterAuth(BaseTestUsuarios):
    """Pruebas dedicadas a los endpoints de app/modules/usuarios/router.py."""

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

    def test_endpoints_traducen_errores_de_usuario_service_a_http(self) -> None:
        dto_duplicado = self.crear_dto_transportista_valido(
            email="juan.chofer@transporte.cl"
        )

        with _servidor_http() as solicitar:
            status_reg, body_reg = solicitar(
                "POST", "/auth/registro", datos=dto_duplicado.model_dump(mode="json")
            )
            self.assertEqual(status_reg, 400)
            self.assertEqual(body_reg, {"detail": "El email ya está registrado"})

            for payload in (
                {"email": "no_existe@correo.cl", "password": self.password_comun},
                {"email": "juan.chofer@transporte.cl", "password": "claveIncorrecta123"},
            ):
                with self.subTest(email=payload["email"]):
                    status_login, body_login = solicitar(
                        "POST", "/auth/login", datos=payload
                    )
                    self.assertEqual(status_login, 401)
                    self.assertEqual(body_login, {"detail": "Credenciales inválidas"})

            status_ok, body_ok = solicitar(
                "POST",
                "/auth/login",
                datos={
                    "email": self.usuario_admin.email,
                    "password": self.password_comun,
                },
            )
            self.assertEqual(status_ok, 200)

            status_get, body_get = solicitar(
                "GET",
                f"/auth/usuarios/{uuid4()}",
                token=body_ok["access_token"],
            )
            self.assertEqual(status_get, 404)
            self.assertEqual(body_get, {"detail": "Usuario no encontrado"})

    def test_endpoint_traduce_campos_vacios_de_login_a_http_400(self) -> None:
        cred = CredencialesLogin.model_construct(usuario="   ", password="")
        with self.assertRaises(HTTPException) as ctx:
            iniciar_sesion(cred)

        self.assertEqual(ctx.exception.status_code, 400)
        self.assertEqual(
            ctx.exception.detail,
            "El correo electrónico y la contraseña son campos obligatorios.",
        )
