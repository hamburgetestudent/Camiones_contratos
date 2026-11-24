"""Tests unitarios dedicados a UsuarioService.iniciar_sesion y LoginService."""

from __future__ import annotations

from uuid import uuid4

from fastapi import HTTPException, status

from domain.modelos_login import CredencialesLogin, RespuestaLogin
from domain.modelos_usuario import EstadoUsuario, RolUsuario, UsuarioModelo
from services.login_service import CredencialesInvalidasError, LoginService
from services.respuesta_login import construir_respuesta_login
from services.security import decodificar_token_acceso
from services.usuario_service import UsuarioService, ValidadorUsuario
from tests.usuarios.base import BaseTestUsuarios


class TestIniciarSesion(BaseTestUsuarios):
    """Pruebas dedicadas a la emisión de token OAuth2 Bearer y LoginService (CA-01, CA-02, CA-03)."""

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
        self.assertEqual(claims["email"], "juan.chofer@transporte.cl")
        self.assertEqual(claims["rol"], RolUsuario.TRANSPORTISTA.value)

    def test_login_service_con_validador_exitoso(self) -> None:
        servicio = LoginService(ValidadorUsuario())
        cred = CredencialesLogin(
            usuario="marcela@empresa.cl", password=self.password_comun
        )
        resp = servicio.iniciar_sesion(cred)
        self.assertEqual(resp.rol, RolUsuario.DADOR_CARGA.value)
        # TD-01: Verificamos claims del token emitido en LoginService
        claims = decodificar_token_acceso(resp.access_token)
        self.assertIsNotNone(claims)
        assert claims is not None
        self.assertEqual(claims["sub"], str(self.usuario_dador.id))
        self.assertEqual(claims["email"], "marcela@empresa.cl")
        self.assertEqual(claims["rol"], RolUsuario.DADOR_CARGA.value)

    def test_login_service_con_validador_credenciales_invalidas(self) -> None:
        servicio = LoginService(ValidadorUsuario())
        cred = CredencialesLogin(
            usuario="marcela@empresa.cl", password="passwordIncorrecta"
        )
        with self.assertRaises(CredencialesInvalidasError):
            servicio.iniciar_sesion(cred)

    # ============================================================
    # TD-01: PRUEBAS PARA CREDENCIALES INVÁLIDAS Y LÍMITES EN USUARIO_SERVICE
    # ============================================================
    def test_usuario_service_password_incorrecta_lanza_http_401(self) -> None:
        """Verifica que contraseña incorrecta lance HTTPException 401."""
        cred = CredencialesLogin(
            usuario="juan.chofer@transporte.cl", password="claveIncorrecta123"
        )
        with self.assertRaises(HTTPException) as ctx:
            UsuarioService.iniciar_sesion(cred)
        self.assertEqual(ctx.exception.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(ctx.exception.detail, "Credenciales inválidas")

    def test_usuario_service_usuario_no_existente_lanza_http_401(self) -> None:
        """Verifica que usuario no registrado lance HTTPException 401."""
        cred = CredencialesLogin(
            usuario="inexistente@noexiste.cl", password=self.password_comun
        )
        with self.assertRaises(HTTPException) as ctx:
            UsuarioService.iniciar_sesion(cred)
        self.assertEqual(ctx.exception.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(ctx.exception.detail, "Credenciales inválidas")

    def test_usuario_service_email_vacio_lanza_http_400(self) -> None:
        """Verifica valor límite: correo vacío lanza HTTPException 400."""
        cred = CredencialesLogin.model_construct(usuario="", password="Password123")
        with self.assertRaises(HTTPException) as ctx:
            UsuarioService.iniciar_sesion(cred)
        self.assertEqual(ctx.exception.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            ctx.exception.detail, "El correo electrónico es un campo obligatorio."
        )

    def test_usuario_service_password_vacia_lanza_http_400(self) -> None:
        """Verifica valor límite: contraseña vacía lanza HTTPException 400."""
        cred = CredencialesLogin.model_construct(
            usuario="juan.chofer@transporte.cl", password=""
        )
        with self.assertRaises(HTTPException) as ctx:
            UsuarioService.iniciar_sesion(cred)
        self.assertEqual(ctx.exception.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(ctx.exception.detail, "La contraseña es un campo obligatorio.")

    def test_usuario_service_ambos_campos_vacios_lanza_http_400(self) -> None:
        """Verifica valor límite: ambos campos vacíos lanza HTTPException 400."""
        cred = CredencialesLogin.model_construct(usuario="", password="")
        with self.assertRaises(HTTPException) as ctx:
            UsuarioService.iniciar_sesion(cred)
        self.assertEqual(ctx.exception.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            ctx.exception.detail,
            "El correo electrónico y la contraseña son campos obligatorios.",
        )

    # ============================================================
    # TD-01: PRUEBA DE CARACTERIZACIÓN - AUTENTICACIÓN
    # Clase 3.1: Refactorización sistemática
    #
    # Objetivo:
    # Proteger el comportamiento actual de LoginService cuando
    # las credenciales son válidas, pero el usuario no tiene
    # información de perfil disponible.
    #
    # Esta prueba debe seguir funcionando después de refactorizar.
    # ============================================================
    def test_login_sin_datos_usuario(self) -> None:
        """Verifica el login cuando el validador no entrega un perfil."""

        # Simulamos un validador que acepta las credenciales,
        # pero no dispone de información adicional del usuario.
        class ValidadorSinDatos:
            def validar(self, usuario: str, password: str) -> bool:
                return True

            def obtener_datos_usuario(self, usuario: str):
                return None

        # Preparamos credenciales válidas para la prueba.
        credenciales = CredencialesLogin(
            usuario="sinperfil@ejemplo.cl",
            password="clave123",
        )

        # Ejecutamos el comportamiento original de LoginService.
        servicio = LoginService(ValidadorSinDatos())
        respuesta = servicio.iniciar_sesion(credenciales)

        # Comprobamos los valores predeterminados de la respuesta.
        self.assertEqual(respuesta.rol, "USUARIO")
        self.assertEqual(respuesta.usuario, "sinperfil@ejemplo.cl")
        self.assertEqual(respuesta.email, "sinperfil@ejemplo.cl")
        self.assertIsNone(respuesta.id)
        self.assertIsNone(respuesta.nombre)
        self.assertIsNone(respuesta.estado)

        # Verificamos que el token conserve los datos esperados.
        claims = decodificar_token_acceso(respuesta.access_token)
        self.assertIsNotNone(claims)
        self.assertEqual(claims["sub"], "sinperfil@ejemplo.cl")
        self.assertEqual(claims["rol"], "USUARIO")

    def test_login_service_validador_sin_metodo_obtener_datos_usuario(self) -> None:
        """Verifica duck typing: validador sin el método obtener_datos_usuario."""

        class ValidadorMinimo:
            def validar(self, usuario: str, password: str) -> bool:
                return True

        credenciales = CredencialesLogin(
            usuario="minimo@ejemplo.cl",
            password="clave123",
        )
        servicio = LoginService(ValidadorMinimo())  # type: ignore[arg-type]
        respuesta = servicio.iniciar_sesion(credenciales)

        self.assertEqual(respuesta.rol, "USUARIO")
        self.assertEqual(respuesta.usuario, "minimo@ejemplo.cl")
        self.assertIsNone(respuesta.id)
        self.assertIsNone(respuesta.nombre)

        claims = decodificar_token_acceso(respuesta.access_token)
        self.assertIsNotNone(claims)
        assert claims is not None
        self.assertEqual(claims["sub"], "minimo@ejemplo.cl")
        self.assertEqual(claims["rol"], "USUARIO")


class TestConstruirRespuestaLogin(BaseTestUsuarios):
    """Pruebas unitarias directas para el componente reutilizable construir_respuesta_login (TD-01)."""

    def test_construir_respuesta_con_usuario_completo(self) -> None:
        """Verifica la construcción de respuesta a partir de un UsuarioModelo completo."""
        respuesta = construir_respuesta_login(
            datos_usuario=self.usuario_transportista,
            usuario_solicitado="solicitado@empresa.cl",
        )

        self.assertIsInstance(respuesta, RespuestaLogin)
        self.assertEqual(respuesta.token_type, "bearer")
        self.assertEqual(respuesta.rol, RolUsuario.TRANSPORTISTA.value)
        self.assertEqual(respuesta.id, str(self.usuario_transportista.id))
        self.assertEqual(respuesta.nombre, self.usuario_transportista.nombre)
        self.assertEqual(respuesta.email, self.usuario_transportista.email)
        self.assertEqual(respuesta.estado, EstadoUsuario.APROBADO.value)
        self.assertEqual(respuesta.usuario, "solicitado@empresa.cl")

        # Verificar claims del token generado
        claims = decodificar_token_acceso(respuesta.access_token)
        self.assertIsNotNone(claims)
        assert claims is not None
        self.assertEqual(claims["sub"], str(self.usuario_transportista.id))
        self.assertEqual(claims["email"], self.usuario_transportista.email)
        self.assertEqual(claims["rol"], RolUsuario.TRANSPORTISTA.value)

    def test_construir_respuesta_sin_perfil_usuario_none(self) -> None:
        """Verifica valores predeterminados cuando datos_usuario es None."""
        respuesta = construir_respuesta_login(
            datos_usuario=None,
            usuario_solicitado="usuario.externo@ejemplo.cl",
        )

        self.assertEqual(respuesta.rol, "USUARIO")
        self.assertEqual(respuesta.usuario, "usuario.externo@ejemplo.cl")
        self.assertEqual(respuesta.email, "usuario.externo@ejemplo.cl")
        self.assertIsNone(respuesta.id)
        self.assertIsNone(respuesta.nombre)
        self.assertIsNone(respuesta.estado)

        claims = decodificar_token_acceso(respuesta.access_token)
        self.assertIsNotNone(claims)
        assert claims is not None
        self.assertEqual(claims["sub"], "usuario.externo@ejemplo.cl")
        self.assertEqual(claims["email"], "usuario.externo@ejemplo.cl")
        self.assertEqual(claims["rol"], "USUARIO")

    def test_construir_respuesta_rol_y_estado_como_string(self) -> None:
        """Verifica tolerancia cuando rol y estado son strings en lugar de enums."""
        user_id = uuid4()
        usuario_con_strings = UsuarioModelo.model_construct(
            id=user_id,
            nombre="Usuario Texto",
            email="texto@ejemplo.cl",
            rol="TRANSPORTISTA",  # String directo
            estado="APROBADO",  # String directo
            password_hash="fakehash",
        )

        respuesta = construir_respuesta_login(
            datos_usuario=usuario_con_strings,
            usuario_solicitado="texto@ejemplo.cl",
        )

        self.assertEqual(respuesta.rol, "TRANSPORTISTA")
        self.assertEqual(respuesta.estado, "APROBADO")
        self.assertEqual(respuesta.id, str(user_id))

        claims = decodificar_token_acceso(respuesta.access_token)
        self.assertIsNotNone(claims)
        assert claims is not None
        self.assertEqual(claims["rol"], "TRANSPORTISTA")
