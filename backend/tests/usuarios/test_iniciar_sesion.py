"""Tests unitarios dedicados a UsuarioService.iniciar_sesion."""

from __future__ import annotations

from app.core.security import decodificar_token_acceso
from app.modules.usuarios.models import RolUsuario
from app.modules.usuarios.models_login import CredencialesLogin, RespuestaLogin
from app.modules.usuarios.service import UsuarioService
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

    def test_inicio_sesion_todos_los_roles(self) -> None:
        usuarios = (
            self.usuario_transportista,
            self.usuario_dador,
            self.usuario_admin,
        )

        for usuario in usuarios:
            with self.subTest(rol=usuario.rol):
                credenciales = CredencialesLogin(
                    usuario=usuario.email,
                    password=self.password_comun,
                )
                respuesta = UsuarioService.iniciar_sesion(credenciales)

                self.assertEqual(respuesta.id, str(usuario.id))
                self.assertEqual(respuesta.nombre, usuario.nombre)
                self.assertEqual(respuesta.email, usuario.email)
                self.assertEqual(respuesta.usuario, usuario.email)
                self.assertEqual(respuesta.rol, usuario.rol.value)
                self.assertEqual(respuesta.estado, usuario.estado.value)
                self.assertEqual(respuesta.token_type, "bearer")

                claims = decodificar_token_acceso(respuesta.access_token)
                self.assertIsNotNone(claims)
                assert claims is not None
                self.assertEqual(claims["sub"], str(usuario.id))
                self.assertEqual(claims["email"], usuario.email)
                self.assertEqual(claims["rol"], usuario.rol.value)

    def test_colaboracion_entre_modulos(self) -> None:
        from unittest.mock import patch

        from app.core.security import crear_token_acceso
        from app.modules.usuarios.respuesta_login import construir_respuesta_login

        credenciales = CredencialesLogin(
            usuario=self.usuario_transportista.email,
            password=self.password_comun,
        )

        with (
            patch(
                "app.modules.usuarios.service.construir_respuesta_login",
                wraps=construir_respuesta_login,
            ) as constructor,
            patch(
                "app.modules.usuarios.respuesta_login.crear_token_acceso",
                wraps=crear_token_acceso,
            ) as generador,
        ):
            respuesta = UsuarioService.iniciar_sesion(credenciales)

            constructor.assert_called_once()
            generador.assert_called_once_with({
                "sub": str(self.usuario_transportista.id),
                "email": self.usuario_transportista.email,
                "rol": self.usuario_transportista.rol.value,
            })

            self.assertEqual(
                respuesta.id, str(self.usuario_transportista.id)
            )
            self.assertIsNotNone(
                decodificar_token_acceso(respuesta.access_token)
            )

    def test_credenciales_invalidas_no_construyen_respuesta(self) -> None:
        from unittest.mock import patch

        from app.modules.usuarios.service import CredencialesInvalidasError

        credenciales = CredencialesLogin(
            usuario=self.usuario_transportista.email,
            password="passwordIncorrecta",
        )

        with patch(
            "app.modules.usuarios.service.construir_respuesta_login"
        ) as constructor:
            with self.assertRaises(CredencialesInvalidasError) as error:
                UsuarioService.iniciar_sesion(credenciales)

            self.assertEqual(str(error.exception), "Credenciales inválidas")
            constructor.assert_not_called()
