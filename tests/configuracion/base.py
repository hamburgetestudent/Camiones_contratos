"""Base DRY para pruebas del singleton ReglasNegocio."""

from __future__ import annotations

from domain.reglas import ReglasNegocio
from tests.base import BaseTestCase


class BaseTestConfiguracion(BaseTestCase):
    """Clase base DRY para pruebas de reglas de negocio globales.
    
    Hereda de tests.base.BaseTestCase y asegura el reseteo
    a los valores por defecto antes y después de cada prueba.
    """

    def setUp(self) -> None:
        super().setUp()
        ReglasNegocio.reseteo_defaults()

    def tearDown(self) -> None:
        ReglasNegocio.reseteo_defaults()
        super().tearDown()

