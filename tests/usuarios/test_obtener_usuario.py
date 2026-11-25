"""Tests unitarios dedicados a UsuarioService.obtener_usuario."""

from __future__ import annotations

from uuid import uuid4

from services.usuario_service import UsuarioNoEncontradoError, UsuarioService
from tests.usuarios.base import BaseTestUsuarios


class TestObtenerUsuario(BaseTestUsuarios):
    """Pruebas dedicadas a la consulta de usuario por UUID."""

    def test_obtener_usuario_existente(self) -> None:
        recuperado = UsuarioService.obtener_usuario(self.usuario_transportista.id)
        self.assertEqual(recuperado.id, self.usuario_transportista.id)
        self.assertEqual(recuperado.email, self.usuario_transportista.email)

    def test_obtener_usuario_inexistente_lanza_error(self) -> None:
        with self.assertRaises(UsuarioNoEncontradoError) as ctx:
            UsuarioService.obtener_usuario(uuid4())
        self.assertEqual(str(ctx.exception), "Usuario no encontrado")
