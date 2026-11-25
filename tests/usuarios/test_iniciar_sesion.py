"""Tests unitarios dedicados a UsuarioService.iniciar_sesion."""

from __future__ import annotations

from domain.modelos_login import CredencialesLogin, RespuestaLogin
from domain.modelos_usuario import RolUsuario
from services.security import decodificar_token_acceso
from services.usuario_service import UsuarioService
from tests.usuarios.base import BaseTestUsuarios


class TestIniciarSesion(BaseTestUsuarios):
    """Pruebas dedicadas a la emisión de token OAuth2 Bearer (CA-01, CA-02, CA-03)."""

    def test_inicio_sesion_exitoso_emite_token_y_rol(self) -> None:
        cred = CredencialesLogin(
            usuario="juan.chofer@transporte.cl", password=self.password_comun
        )
        respuesta = UsuarioService.iniciar_sesion(cred)

        self.assertIsInstance(respuesta, RespuestaLogin)
        self.assertEqual(respuesta.token_type.lower(), "bearer")
        self.assertEqual(respuesta.rol, RolUsuario.TRANSPORTISTA.value)
        self.assertEqual(respuesta.usuario, "juan.chofer@transporte.cl")

        # Validar claims del token emitido
        claims = decodificar_token_acceso(respuesta.access_token)
        self.assertIsNotNone(claims)
        assert claims is not None
        self.assertEqual(claims["sub"], str(self.usuario_transportista.id))
        self.assertEqual(claims["rol"], RolUsuario.TRANSPORTISTA.value)
