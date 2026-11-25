"""Tests unitarios dedicados a UsuarioService.autenticar_usuario."""

from __future__ import annotations

from services.usuario_service import CredencialesInvalidasError, UsuarioService
from tests.usuarios.base import BaseTestUsuarios


class TestAutenticarUsuario(BaseTestUsuarios):
    """Pruebas dedicadas a la verificación de credenciales de usuario."""

    def test_autenticacion_exitosa(self) -> None:
        usuario = UsuarioService.autenticar_usuario(
            "juan.chofer@transporte.cl", self.password_comun
        )
        self.assertEqual(usuario.id, self.usuario_transportista.id)
        self.assertEqual(usuario.email, "juan.chofer@transporte.cl")

    def test_rechazo_usuario_no_registrado(self) -> None:
        with self.assertRaises(CredencialesInvalidasError) as ctx:
            UsuarioService.autenticar_usuario(
                "no_existe@correo.cl", self.password_comun
            )
        self.assertEqual(str(ctx.exception), "Credenciales inválidas")

    def test_rechazo_password_incorrecta(self) -> None:
        with self.assertRaises(CredencialesInvalidasError) as ctx:
            UsuarioService.autenticar_usuario(
                "juan.chofer@transporte.cl", "passwordTotalmenteErronea"
            )
        self.assertEqual(str(ctx.exception), "Credenciales inválidas")

    def test_rechazo_campos_vacios_o_espacios(self) -> None:
        with self.assertRaises(ValueError) as ctx_email:
            UsuarioService.autenticar_usuario("", self.password_comun)
        self.assertIn("requeridos", str(ctx_email.exception))

        with self.assertRaises(ValueError) as ctx_pass:
            UsuarioService.autenticar_usuario("juan.chofer@transporte.cl", "   ")
        self.assertIn("requeridos", str(ctx_pass.exception))

    def test_busca_el_correo_sin_distinguir_mayusculas_ni_espacios(self) -> None:
        usuario = UsuarioService.autenticar_usuario(
            "  JUAN.CHOFER@TRANSPORTE.CL  ", self.password_comun
        )
        self.assertEqual(usuario.id, self.usuario_transportista.id)
