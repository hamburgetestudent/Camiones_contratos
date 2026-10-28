"""Tests unitarios dedicados a la función decodificar_token_acceso."""

from __future__ import annotations

import time
from services.security import crear_token_acceso, decodificar_token_acceso
from tests.seguridad.base import BaseTestSeguridad


class TestDecodificarTokenAcceso(BaseTestSeguridad):
    """Pruebas dedicadas exclusivamente a la validación y decodificación de tokens JWT."""

    def test_decodificacion_exitosa_token_valido(self) -> None:
        token = crear_token_acceso(self.claims_base, clave_secreta=self.clave_secreta_test)
        claims_recuperadas = decodificar_token_acceso(token, clave_secreta=self.clave_secreta_test)

        self.assertIsNotNone(claims_recuperadas)
        assert claims_recuperadas is not None
        self.assertEqual(claims_recuperadas["sub"], self.claims_base["sub"])
        self.assertEqual(claims_recuperadas["email"], self.claims_base["email"])
        self.assertEqual(claims_recuperadas["rol"], self.claims_base["rol"])

    def test_rechazo_token_con_clave_secreta_incorrecta(self) -> None:
        token = crear_token_acceso(self.claims_base, clave_secreta=self.clave_secreta_test)
        resultado = decodificar_token_acceso(token, clave_secreta="clave_totalmente_distinta")
        self.assertIsNone(resultado)

    def test_rechazo_token_expirado(self) -> None:
        token = crear_token_acceso(self.claims_base, expiracion_minutos=-10, clave_secreta=self.clave_secreta_test)
        resultado = decodificar_token_acceso(token, clave_secreta=self.clave_secreta_test)
        self.assertIsNone(resultado)

    def test_rechazo_token_malformado(self) -> None:
        self.assertIsNone(decodificar_token_acceso("invalido", clave_secreta=self.clave_secreta_test))
        self.assertIsNone(decodificar_token_acceso("a.b", clave_secreta=self.clave_secreta_test))
        self.assertIsNone(decodificar_token_acceso("a.b.c.d", clave_secreta=self.clave_secreta_test))
        self.assertIsNone(decodificar_token_acceso("", clave_secreta=self.clave_secreta_test))

