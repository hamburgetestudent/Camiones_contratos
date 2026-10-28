"""Tests unitarios dedicados a la clase ValidadorUsuario."""

from __future__ import annotations

from services.usuario_service import ValidadorUsuario
from tests.usuarios.base import BaseTestUsuarios


class TestValidadorUsuario(BaseTestUsuarios):
    """Pruebas dedicadas a la clase ValidadorUsuario que implementa ValidadorCredenciales."""

    def setUp(self) -> None:
        super().setUp()
        self.validador = ValidadorUsuario()

    def test_validar_credenciales_correctas_retorna_true(self) -> None:
        self.assertTrue(self.validador.validar("juan.chofer@transporte.cl", self.password_comun))

    def test_validar_credenciales_incorrectas_retorna_false(self) -> None:
        self.assertFalse(self.validador.validar("juan.chofer@transporte.cl", "claveErronea"))
        self.assertFalse(self.validador.validar("desconocido@correo.cl", self.password_comun))

    def test_obtener_datos_usuario(self) -> None:
        datos = self.validador.obtener_datos_usuario("juan.chofer@transporte.cl")
        self.assertIsNotNone(datos)
        self.assertEqual(datos.email, "juan.chofer@transporte.cl")

