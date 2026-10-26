"""Tests unitarios dedicados a la función ReglasNegocio.obtener_configuracion."""

from __future__ import annotations

from domain.reglas import ReglasNegocio
from tests.configuracion.base import BaseTestConfiguracion


class TestObtenerConfiguracion(BaseTestConfiguracion):
    """Pruebas dedicadas exclusivamente a la consulta de configuración."""

    def test_obtener_valores_por_defecto(self) -> None:
        cfg = ReglasNegocio.obtener_configuracion()
        self.assertIsInstance(cfg, dict)
        self.assertEqual(cfg["iva_porcentaje"], 0.19)
        self.assertEqual(cfg["tolerancia_max"], 0.01)
        self.assertEqual(cfg["anticipacion_min_h"], 2)

    def test_patron_singleton_mismo_estado(self) -> None:
        instancia1 = ReglasNegocio()
        instancia2 = ReglasNegocio()
        self.assertIs(instancia1, instancia2)

    def test_alias_obt_configuracion(self) -> None:
        self.assertEqual(ReglasNegocio.obt_configuracion(), ReglasNegocio.obtener_configuracion())

