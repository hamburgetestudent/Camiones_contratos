"""Pruebas unitarias e integración para HU-IAM-02: Iniciar sesión.

Criterios de Aceptación:
- CA-01: Inicio de sesión exitoso (emisión de credencial OAuth2 con token de acceso tipo Bearer y rol).
- CA-02: Credenciales incorrectas (correo no registrado o clave incorrecta -> HTTP 401 "Credenciales inválidas").
- CA-03: Validación de campos obligatorios (sin email, sin password, o ambos -> campos obligatorios informados).
- CA-04: Visualización de funcionalidades según el rol (entrega rol correspondiente y claims en el token).

Trazabilidad técnica:
- routers/auth_router.py (POST /auth/login)
- services/usuario_service.py (autenticar_usuario, iniciar_sesion)
- services/security.py (crear_token_acceso, decodificar_token_acceso)
- domain/modelos_login.py (CredencialesLogin, RespuestaLogin)
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from uuid import UUID, uuid4

from fastapi import HTTPException
from fastapi.testclient import TestClient
from pydantic import ValidationError

from dao.usuario_dao import UsuarioDAOMemoria, UsuarioDAOSQLite
from domain.modelos_login import CredencialesLogin, RespuestaLogin
from domain.modelos_usuario import EstadoUsuario, RolUsuario, UsuarioCrear, UsuarioModelo
from main import app
from routers.auth_router import iniciar_sesion as router_iniciar_sesion
from services.security import crear_token_acceso, decodificar_token_acceso
import services.usuario_service as usuario_service_modulo
from services.usuario_service import UsuarioService, hash_password


class BaseTestLogin(unittest.TestCase):
    """Configuracion base con aislamiento en memoria para pruebas rapidas y deterministas."""

    def setUp(self) -> None:
        self._orig_usuario_dao = usuario_service_modulo.usuario_dao
        self.usuario_dao_memoria = UsuarioDAOMemoria()
        usuario_service_modulo.usuario_dao = self.usuario_dao_memoria

        # Crear usuarios semilla en memoria para pruebas
        self.password_comun = "passwordSegura123"
        self.hash_comun = hash_password(self.password_comun)

        self.usuario_transportista = UsuarioModelo(
            id=uuid4(),
            nombre="Juan Chofer",
            email="juan.chofer@transporte.cl",
            rol=RolUsuario.TRANSPORTISTA,
            password_hash=self.hash_comun,
            estado=EstadoUsuario.APROBADO,
        )
        self.usuario_dao_memoria.guardar(self.usuario_transportista)

        self.usuario_dador = UsuarioModelo(
            id=uuid4(),
            nombre="Marcela Gerente",
            email="marcela@empresa.cl",
            rol=RolUsuario.DADOR_CARGA,
            password_hash=self.hash_comun,
            estado=EstadoUsuario.APROBADO,
        )
        self.usuario_dao_memoria.guardar(self.usuario_dador)

        self.usuario_admin = UsuarioModelo(
            id=uuid4(),
            nombre="Carlos Admin",
            email="admin@plataforma.cl",
            rol=RolUsuario.ADMIN_BACKOFFICE,
            password_hash=self.hash_comun,
            estado=EstadoUsuario.APROBADO,
        )
        self.usuario_dao_memoria.guardar(self.usuario_admin)

        self.client = TestClient(app)

    def tearDown(self) -> None:
        usuario_service_modulo.usuario_dao = self._orig_usuario_dao


class TestCA01InicioSesionExitoso(BaseTestLogin):
    """CA1: Inicio de sesión exitoso con emisión de token Bearer y rol."""

    def test_login_exitoso_transportista_retorna_token_bearer_y_rol(self) -> None:
        """Transportista con credenciales validas recibe HTTP 200, access_token y rol."""
        credenciales = CredencialesLogin(
            usuario="juan.chofer@transporte.cl",
            password=self.password_comun,
        )

        respuesta = UsuarioService.iniciar_sesion(credenciales)

        self.assertIsInstance(respuesta, RespuestaLogin)
        self.assertEqual(respuesta.mensaje, "Inicio de sesión exitoso")
        self.assertEqual(respuesta.token_type.lower(), "bearer")
        self.assertEqual(respuesta.rol, RolUsuario.TRANSPORTISTA.value)
        self.assertEqual(respuesta.usuario, "juan.chofer@transporte.cl")
        self.assertEqual(respuesta.nombre, "Juan Chofer")
        self.assertIsNotNone(respuesta.access_token)
        self.assertTrue(len(respuesta.access_token) > 20)

        # Validar decodificacion y claims del token Bearer
        claims = decodificar_token_acceso(respuesta.access_token)
        self.assertIsNotNone(claims)
        assert claims is not None
        self.assertEqual(claims.get("email"), "juan.chofer@transporte.cl")
        self.assertEqual(claims.get("rol"), RolUsuario.TRANSPORTISTA.value)
        self.assertEqual(claims.get("sub"), str(self.usuario_transportista.id))

    def test_login_exitoso_dador_carga(self) -> None:
        """Dador de carga con credenciales validas recibe token y rol DADOR_CARGA."""
        credenciales = CredencialesLogin(
            usuario="marcela@empresa.cl",
            password=self.password_comun,
        )

        respuesta = UsuarioService.iniciar_sesion(credenciales)

        self.assertEqual(respuesta.rol, RolUsuario.DADOR_CARGA.value)
        self.assertEqual(respuesta.token_type.lower(), "bearer")
        self.assertEqual(respuesta.nombre, "Marcela Gerente")

        claims = decodificar_token_acceso(respuesta.access_token)
        self.assertIsNotNone(claims)
        assert claims is not None
        self.assertEqual(claims.get("rol"), RolUsuario.DADOR_CARGA.value)

    def test_login_exitoso_a_traves_del_router_auth(self) -> None:
        """El router de autenticacion POST /auth/login responde con status 200 y token Bearer."""
        credenciales = CredencialesLogin(
            email="juan.chofer@transporte.cl",
            password=self.password_comun,
        )

        resultado = router_iniciar_sesion(credenciales)

        self.assertEqual(resultado.token_type.lower(), "bearer")
        self.assertEqual(resultado.rol, RolUsuario.TRANSPORTISTA.value)
        self.assertIsNotNone(resultado.access_token)

    def test_login_cliente_http_post_auth_login_con_alias_email(self) -> None:
        """Endpoint HTTP POST /auth/login acepta JSON con campo 'email'."""
        respuesta = self.client.post(
            "/auth/login",
            json={
                "email": "juan.chofer@transporte.cl",
                "password": self.password_comun,
            },
        )

        self.assertEqual(respuesta.status_code, 200)
        datos = respuesta.json()
        self.assertEqual(datos["token_type"].lower(), "bearer")
        self.assertEqual(datos["rol"], "TRANSPORTISTA")
        self.assertEqual(datos["usuario"], "juan.chofer@transporte.cl")
        self.assertIn("access_token", datos)

    def test_login_cliente_http_post_auth_login_con_alias_usuario(self) -> None:
        """Endpoint HTTP POST /auth/login acepta JSON con campo 'usuario'."""
        respuesta = self.client.post(
            "/auth/login",
            json={
                "usuario": "marcela@empresa.cl",
                "password": self.password_comun,
            },
        )

        self.assertEqual(respuesta.status_code, 200)
        datos = respuesta.json()
        self.assertEqual(datos["rol"], "DADOR_CARGA")
        self.assertEqual(datos["token_type"].lower(), "bearer")

    def test_login_insensible_a_mayusculas_en_correo(self) -> None:
        """El correo es insensible a mayusculas durante el inicio de sesion."""
        credenciales = CredencialesLogin(
            usuario="JUAN.CHOFER@TRANSPORTE.CL",
            password=self.password_comun,
        )

        respuesta = UsuarioService.iniciar_sesion(credenciales)
        self.assertEqual(respuesta.usuario, "juan.chofer@transporte.cl")
        self.assertEqual(respuesta.token_type.lower(), "bearer")


class TestCA02CredencialesIncorrectas(BaseTestLogin):
    """CA2: Rechazo ante credenciales incorrectas con HTTP 401 «Credenciales inválidas»."""

    def test_rechazo_usuario_no_registrado_servicio(self) -> None:
        """Intento con correo no registrado lanza HTTP 401 con 'Credenciales inválidas'."""
        credenciales = CredencialesLogin(
            usuario="desconocido@correo.cl",
            password=self.password_comun,
        )

        with self.assertRaises(HTTPException) as ctx:
            UsuarioService.iniciar_sesion(credenciales)

        self.assertEqual(ctx.exception.status_code, 401)
        self.assertEqual(ctx.exception.detail, "Credenciales inválidas")

    def test_rechazo_password_incorrecta_servicio(self) -> None:
        """Intento con password incorrecta lanza HTTP 401 con 'Credenciales inválidas'."""
        credenciales = CredencialesLogin(
            usuario="juan.chofer@transporte.cl",
            password="claveCompletamenteErronea999",
        )

        with self.assertRaises(HTTPException) as ctx:
            UsuarioService.iniciar_sesion(credenciales)

        self.assertEqual(ctx.exception.status_code, 401)
        self.assertEqual(ctx.exception.detail, "Credenciales inválidas")

    def test_cliente_http_rechazo_correo_no_registrado_retorna_401(self) -> None:
        """Endpoint HTTP retorna 401 Unauthorized con detalle «Credenciales inválidas»."""
        respuesta = self.client.post(
            "/auth/login",
            json={
                "email": "inexistente@correo.cl",
                "password": "cualquierPassword123",
            },
        )

        self.assertEqual(respuesta.status_code, 401)
        self.assertEqual(respuesta.json().get("detail"), "Credenciales inválidas")

    def test_cliente_http_rechazo_password_erronea_retorna_401(self) -> None:
        """Endpoint HTTP con clave erronea retorna 401 Unauthorized y no expone tokens."""
        respuesta = self.client.post(
            "/auth/login",
            json={
                "email": "juan.chofer@transporte.cl",
                "password": "passwordIncorrecta",
            },
        )

        self.assertEqual(respuesta.status_code, 401)
        self.assertEqual(respuesta.json().get("detail"), "Credenciales inválidas")
        self.assertNotIn("access_token", respuesta.json())


class TestCA03CamposObligatorios(BaseTestLogin):
    """CA3: Validación de campos obligatorios faltantes o vacíos."""

    def test_rechazo_correo_vacio_pydantic(self) -> None:
        """Modelo rechaza correo vacio e informa obligatoriedad."""
        with self.assertRaises(ValidationError) as ctx:
            CredencialesLogin(
                usuario="",
                password="passwordValida123",
            )
        self.assertIn("correo electrónico es un campo obligatorio", str(ctx.exception).lower())

    def test_rechazo_password_vacia_pydantic(self) -> None:
        """Modelo rechaza contrasena vacia e informa obligatoriedad."""
        with self.assertRaises(ValidationError) as ctx:
            CredencialesLogin(
                usuario="juan@transporte.cl",
                password="",
            )
        self.assertIn("contraseña es un campo obligatorio", str(ctx.exception).lower())

    def test_rechazo_campos_con_solo_espacios_en_blanco(self) -> None:
        """Modelo rechaza cadenas que solo contienen espacios en blanco."""
        with self.assertRaises(ValidationError):
            CredencialesLogin(
                usuario="    ",
                password="passwordValida123",
            )

        with self.assertRaises(ValidationError):
            CredencialesLogin(
                usuario="juan@transporte.cl",
                password="    ",
            )

    def test_cliente_http_falta_email_informa_campo_obligatorio(self) -> None:
        """Peticion HTTP sin email retorna 422 informando campo faltante."""
        respuesta = self.client.post(
            "/auth/login",
            json={"password": "password123"},
        )

        self.assertEqual(respuesta.status_code, 422)
        errores = respuesta.json().get("detail", [])
        campos_con_error = [loc for err in errores for loc in err.get("loc", [])]
        self.assertTrue("usuario" in campos_con_error or "email" in campos_con_error)

    def test_cliente_http_falta_password_informa_campo_obligatorio(self) -> None:
        """Peticion HTTP sin password retorna 422 informando campo faltante."""
        respuesta = self.client.post(
            "/auth/login",
            json={"email": "usuario@correo.cl"},
        )

        self.assertEqual(respuesta.status_code, 422)
        errores = respuesta.json().get("detail", [])
        campos_con_error = [loc for err in errores for loc in err.get("loc", [])]
        self.assertIn("password", campos_con_error)

    def test_cliente_http_cuerpo_completamente_vacio(self) -> None:
        """Peticion HTTP con body vacio identifica que faltan ambos campos."""
        respuesta = self.client.post(
            "/auth/login",
            json={},
        )

        self.assertEqual(respuesta.status_code, 422)
        errores = respuesta.json().get("detail", [])
        campos_afectados = {loc for err in errores for loc in err.get("loc", [])}
        self.assertTrue("usuario" in campos_afectados or "email" in campos_afectados)
        self.assertIn("password", campos_afectados)


class TestCA04VisualizacionSegunRol(BaseTestLogin):
    """CA4: Visualización y entrega de información según el rol asignado."""

    def test_rol_transportista_reflejado_en_respuesta_y_claims(self) -> None:
        """Usuario con rol TRANSPORTISTA recibe exactamente ese rol en el payload y en el token."""
        respuesta = self.client.post(
            "/auth/login",
            json={
                "email": "juan.chofer@transporte.cl",
                "password": self.password_comun,
            },
        )

        self.assertEqual(respuesta.status_code, 200)
        datos = respuesta.json()
        self.assertEqual(datos["rol"], "TRANSPORTISTA")

        claims = decodificar_token_acceso(datos["access_token"])
        self.assertIsNotNone(claims)
        assert claims is not None
        self.assertEqual(claims.get("rol"), "TRANSPORTISTA")

    def test_rol_dador_carga_reflejado_en_respuesta_y_claims(self) -> None:
        """Usuario con rol DADOR_CARGA recibe rol correspondiente para visualizar sus funciones."""
        respuesta = self.client.post(
            "/auth/login",
            json={
                "email": "marcela@empresa.cl",
                "password": self.password_comun,
            },
        )

        self.assertEqual(respuesta.status_code, 200)
        datos = respuesta.json()
        self.assertEqual(datos["rol"], "DADOR_CARGA")

        claims = decodificar_token_acceso(datos["access_token"])
        self.assertIsNotNone(claims)
        assert claims is not None
        self.assertEqual(claims.get("rol"), "DADOR_CARGA")

    def test_rol_admin_backoffice_reflejado_en_respuesta_y_claims(self) -> None:
        """Usuario con rol ADMIN_BACKOFFICE recibe rol administrativo para habilitacion de compliance."""
        respuesta = self.client.post(
            "/auth/login",
            json={
                "email": "admin@plataforma.cl",
                "password": self.password_comun,
            },
        )

        self.assertEqual(respuesta.status_code, 200)
        datos = respuesta.json()
        self.assertEqual(datos["rol"], "ADMIN_BACKOFFICE")

        claims = decodificar_token_acceso(datos["access_token"])
        self.assertIsNotNone(claims)
        assert claims is not None
        self.assertEqual(claims.get("rol"), "ADMIN_BACKOFFICE")


class TestPersistenciaSQLiteIntegracionLogin(unittest.TestCase):
    """Prueba de integración end-to-end conectada a base de datos SQLite real y aislada."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_login.db"

        self.sqlite_dao = UsuarioDAOSQLite(db_path=self.db_path, cargar_semilla=False)
        self._orig_usuario_dao = usuario_service_modulo.usuario_dao
        usuario_service_modulo.usuario_dao = self.sqlite_dao

        self.client = TestClient(app)

    def tearDown(self) -> None:
        usuario_service_modulo.usuario_dao = self._orig_usuario_dao
        self.temp_dir.cleanup()

    def test_flujo_completo_registro_y_login_en_sqlite(self) -> None:
        """Registra un usuario en SQLite y luego inicia sesion exitosamente emitiendo credenciales Bearer."""
        # 1. Registrar usuario en SQLite
        dto_registro = UsuarioCrear(
            nombre="Transportista SQLite Real",
            email="sqlite.chofer@correo.cl",
            rol=RolUsuario.TRANSPORTISTA,
            password="miPasswordFuerte2026",
        )
        usuario_creado = UsuarioService.registrar_usuario(dto_registro)
        self.assertIsInstance(usuario_creado.id, UUID)

        # 2. Iniciar sesión a través de la API
        respuesta_login = self.client.post(
            "/auth/login",
            json={
                "email": "sqlite.chofer@correo.cl",
                "password": "miPasswordFuerte2026",
            },
        )

        self.assertEqual(respuesta_login.status_code, 200)
        datos = respuesta_login.json()
        self.assertEqual(datos["token_type"].lower(), "bearer")
        self.assertEqual(datos["rol"], "TRANSPORTISTA")
        self.assertEqual(datos["usuario"], "sqlite.chofer@correo.cl")
        self.assertEqual(datos["id"], str(usuario_creado.id))

        # 3. Validar token emitido
        claims = decodificar_token_acceso(datos["access_token"])
        self.assertIsNotNone(claims)
        assert claims is not None
        self.assertEqual(claims.get("sub"), str(usuario_creado.id))
        self.assertEqual(claims.get("email"), "sqlite.chofer@correo.cl")
        self.assertEqual(claims.get("rol"), "TRANSPORTISTA")


if __name__ == "__main__":
    unittest.main()
