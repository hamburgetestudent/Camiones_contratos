"""Tests unitarios dedicados a la función _base64url_encode."""

from __future__ import annotations

from services.security import _base64url_encode
from tests.seguridad.base import BaseTestSeguridad


class TestBase64UrlEncode(BaseTestSeguridad):
    """Pruebas dedicadas exclusivamente a la codificación base64url."""

    def test_codifica_bytes_correctamente(self) -> None:
        entrada = b"Hola Mundo Camiones"
        resultado = _base64url_encode(entrada)
        self.assertIsInstance(resultado, str)
        self.assertNotIn("=", resultado)
        self.assertNotIn("+", resultado)
        self.assertNotIn("/", resultado)

    def test_cadena_vacia(self) -> None:
        resultado = _base64url_encode(b"")
        self.assertEqual(resultado, "")

    def test_elimina_padding(self) -> None:
        # Cadena cuya codificación estándar base64 tiene padding '=='
        datos = b"a"  # 'YQ==' en base64 normal
        resultado = _base64url_encode(datos)
        self.assertEqual(resultado, "YQ")

