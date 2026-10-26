"""Base para pruebas de seguridad y generación de tokens JWT OAuth2 Bearer."""

from __future__ import annotations

from tests.base import BaseTestCase


class BaseTestSeguridad(BaseTestCase):
    """Clase base DRY para pruebas de seguridad.
    
    Hereda de tests.base.BaseTestCase y provee datos semilla,
    claves secretas y claims de prueba compartidas.
    """

    def setUp(self) -> None:
        super().setUp()
        self.clave_secreta_test = "clave_secreta_de_prueba_12345"
        self.claims_base = {
            "sub": "123e4567-e89b-12d3-a456-426614174000",
            "email": "test@camiones.cl",
            "rol": "TRANSPORTISTA",
        }

