"""Pruebas unitarias de services.sesion_service (vigencia y revocación de tokens)."""

from __future__ import annotations

import time
import unittest

from database.conexion import obtener_conexion
from services.security import crear_token_acceso
from services.sesion_service import (
    huella_token,
    resolver_usuario_desde_token,
    revocar_token_sesion,
)
from services.usuario_service import UsuarioService
from tests.seguridad.base import BaseTestSeguridad


class TestSesionService(BaseTestSeguridad):
    """Verifica la resolución y revocación persistida de tokens de sesión."""

    def setUp(self) -> None:
        super().setUp()
        self.preparar_bd_aislada(cargar_semilla=True)
        with UsuarioService.dao.conexion() as conn:
            usuario = UsuarioService.dao.obtener_por_email(conn, "admin@camiones.cl")
        assert usuario is not None
        self.usuario_admin = usuario

    def test_token_valido_retorna_usuario(self) -> None:
        token = crear_token_acceso(
            {
                "sub": str(self.usuario_admin.id),
                "email": self.usuario_admin.email,
                "rol": self.usuario_admin.rol.value,
            }
        )
        resuelto = resolver_usuario_desde_token(token)
        self.assertIsNotNone(resuelto)
        assert resuelto is not None
        self.assertEqual(resuelto.id, self.usuario_admin.id)
        self.assertEqual(resuelto.email, self.usuario_admin.email)

    def test_token_invalido_o_sin_sub_retorna_none(self) -> None:
        self.assertIsNone(resolver_usuario_desde_token(""))
        self.assertIsNone(resolver_usuario_desde_token("token.invalido.firma"))
        token_sin_sub = crear_token_acceso({"email": self.usuario_admin.email})
        self.assertIsNone(resolver_usuario_desde_token(token_sin_sub))

    def test_token_con_sub_no_uuid_lanza_value_error(self) -> None:
        token = crear_token_acceso({"sub": "identificador-invalido"})
        with self.assertRaises(ValueError):
            resolver_usuario_desde_token(token)

    def test_revocar_token_invalida_sesion_y_guarda_huella(self) -> None:
        token = crear_token_acceso(
            {
                "sub": str(self.usuario_admin.id),
                "email": self.usuario_admin.email,
                "rol": self.usuario_admin.rol.value,
            }
        )
        revocar_token_sesion(token)
        self.assertIsNone(resolver_usuario_desde_token(token))

        with obtener_conexion() as conn:
            filas = conn.execute("SELECT huella FROM sesiones_cerradas").fetchall()
        huellas = [fila["huella"] for fila in filas]
        self.assertIn(huella_token(token), huellas)
        self.assertNotIn(token, huellas)

    def test_revocar_token_purga_registros_expirados(self) -> None:
        ahora = int(time.time())
        with obtener_conexion() as conn:
            conn.execute(
                "INSERT INTO sesiones_cerradas VALUES (?, ?)",
                ("huella-expirada", ahora - 60),
            )

        token = crear_token_acceso(
            {
                "sub": str(self.usuario_admin.id),
                "email": self.usuario_admin.email,
                "rol": self.usuario_admin.rol.value,
            }
        )
        revocar_token_sesion(token)

        with obtener_conexion() as conn:
            huellas = {
                fila["huella"]
                for fila in conn.execute(
                    "SELECT huella FROM sesiones_cerradas"
                ).fetchall()
            }
        self.assertNotIn("huella-expirada", huellas)
        self.assertIn(huella_token(token), huellas)


if __name__ == "__main__":
    unittest.main()
