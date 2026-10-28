"""Tests unitarios dedicados a la función _base64url_decode."""

from __future__ import annotations

from services.security import _base64url_decode, _base64url_encode
from tests.seguridad.base import BaseTestSeguridad


class TestBase64UrlDecode(BaseTestSeguridad):
    """Pruebas dedicadas exclusivamente a la decodificación base64url."""

    def test_decodifica_correctamente_agregando_padding(self) -> None:
        original = b"Texto para decodificar sin problemas"
        codificado = _base64url_encode(original)
        decodificado = _base64url_decode(codificado)
        self.assertEqual(decodificado, original)

    def test_decodifica_cadena_vacia(self) -> None:
        self.assertEqual(_base64url_decode(""), b"")

    def test_decodifica_con_diferentes_longitudes_de_padding(self) -> None:
        for tamano in range(1, 20):
            muestra = b"X" * tamano
            codificado = _base64url_encode(muestra)
            self.assertEqual(_base64url_decode(codificado), muestra)

