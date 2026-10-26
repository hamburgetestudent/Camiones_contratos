"""Tests para los endpoints de routers/auth_router.py."""

from __future__ import annotations

from domain.modelos_login import CredencialesLogin
from domain.modelos_usuario import RolUsuario
from routers.auth_router import (
    iniciar_sesion,
    listar_usuarios,
    obtener_usuario,
    registrar_usuario,
)
from tests.usuarios.base import BaseTestUsuarios


class TestRouterAuth(BaseTestUsuarios):
    """Pruebas dedicadas a las funciones endpoint de routers/auth_router.py."""

    def test_iniciar_sesion_endpoint(self) -> None:
        cred = CredencialesLogin(usuario="juan.chofer@transporte.cl", password=self.password_comun)
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

