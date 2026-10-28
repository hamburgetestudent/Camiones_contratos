"""Tests unitarios dedicados a UsuarioService.autenticar_usuario."""

from __future__ import annotations

from services.usuario_service import UsuarioService
from tests.usuarios.base import BaseTestUsuarios


class TestAutenticarUsuario(BaseTestUsuarios):
    """Pruebas dedicadas a la verificación de credenciales de usuario."""

    def test_autenticacion_exitosa(self) -> None:
        usuario = UsuarioService.autenticar_usuario("juan.chofer@transporte.cl", self.password_comun)
        self.assertEqual(usuario.id, self.usuario_transportista.id)
        self.assertEqual(usuario.email, "juan.chofer@transporte.cl")

    def test_rechazo_usuario_no_registrado(self) -> None:
        with self.assertHttpException(401, "credenciales inválidas"):
            UsuarioService.autenticar_usuario("no_existe@correo.cl", self.password_comun)

    def test_rechazo_password_incorrecta(self) -> None:
        with self.assertHttpException(401, "credenciales inválidas"):
            UsuarioService.autenticar_usuario("juan.chofer@transporte.cl", "passwordTotalmenteErronea")

    def test_rechazo_campos_vacios_o_espacios(self) -> None:
        with self.assertHttpException(400, "requeridos"):
            UsuarioService.autenticar_usuario("", self.password_comun)
        with self.assertHttpException(400, "requeridos"):
            UsuarioService.autenticar_usuario("juan.chofer@transporte.cl", "   ")