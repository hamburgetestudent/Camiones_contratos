"""Tests unitarios dedicados a UsuarioService.listar_usuarios."""

from __future__ import annotations

from services.usuario_service import UsuarioService
from tests.usuarios.base import BaseTestUsuarios


class TestListarUsuarios(BaseTestUsuarios):
    """Pruebas dedicadas al listado completo de usuarios registrados."""

    def test_listar_usuarios_retorna_usuarios_semilla(self) -> None:
        usuarios = UsuarioService.listar_usuarios()
        self.assertGreaterEqual(len(usuarios), 3)
        emails = {u.email for u in usuarios}
        self.assertIn("juan.chofer@transporte.cl", emails)
        self.assertIn("marcela@empresa.cl", emails)
        self.assertIn("admin@plataforma.cl", emails)