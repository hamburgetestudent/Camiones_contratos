"""Tests unitarios dedicados a la función crear_token_acceso."""

from __future__ import annotations

import json
from services.security import _base64url_decode, crear_token_acceso
from tests.seguridad.base import BaseTestSeguridad


class TestCrearTokenAcceso(BaseTestSeguridad):
    """Pruebas dedicadas exclusivamente a la emisión de tokens JWT OAuth2 Bearer."""

    def test_creacion_token_estructura_tres_segmentos(self) -> None:
        token = crear_token_acceso(self.claims_base, clave_secreta=self.clave_secreta_test)
        partes = token.split(".")
        self.assertEqual(len(partes), 3)

    def test_header_contiene_algoritmo_hs256_y_tipo_jwt(self) -> None:
        token = crear_token_acceso(self.claims_base, clave_secreta=self.clave_secreta_test)
        header_b64 = token.split(".")[0]
        header = json.loads(_base64url_decode(header_b64).decode("utf-8"))
        self.assertEqual(header.get("alg"), "HS256")
        self.assertEqual(header.get("typ"), "JWT")

    def test_payload_incluye_claims_y_metadatos_estandar(self) -> None:
        token = crear_token_acceso(self.claims_base, expiracion_minutos=30, clave_secreta=self.clave_secreta_test)
        payload_b64 = token.split(".")[1]
        payload = json.loads(_base64url_decode(payload_b64).decode("utf-8"))

        self.assertEqual(payload.get("sub"), self.claims_base["sub"])
        self.assertEqual(payload.get("email"), self.claims_base["email"])
        self.assertEqual(payload.get("rol"), self.claims_base["rol"])
        self.assertIn("iat", payload)
        self.assertIn("exp", payload)
        self.assertEqual(payload.get("iss"), "camiones_contratos_iam")
        self.assertTrue(payload["exp"] > payload["iat"])

