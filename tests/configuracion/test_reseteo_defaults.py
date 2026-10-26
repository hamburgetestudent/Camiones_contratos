"""Tests unitarios dedicados a la función ReglasNegocio.reseteo_defaults."""

from __future__ import annotations

from domain.reglas import ReglasNegocio
from tests.configuracion.base import BaseTestConfiguracion


class TestReseteoDefaults(BaseTestConfiguracion):
    """Pruebas dedicadas exclusivamente a la restauración de valores por defecto."""

    def test_resetea_correctamente_tras_modificacion(self) -> None:
        ReglasNegocio.actualizar_configuracion(iva_porcentaje=0.08, tolerancia_max=0.5, anticipacion_min_h=10)
        self.assertEqual(ReglasNegocio.IVA_PORCENTAJE, 0.08)

        ReglasNegocio.reseteo_defaults()
        self.assertEqual(ReglasNegocio.IVA_PORCENTAJE, ReglasNegocio.DEFAULT_IVA_PORCENTAJE)
        self.assertEqual(ReglasNegocio.TOLERANCIA_MAX, ReglasNegocio.DEFAULT_TOLERANCIA_MAX)
        self.assertEqual(ReglasNegocio.ANTICIPACION_MIN_H, ReglasNegocio.DEFAULT_ANTICIPACION_MIN_H)

