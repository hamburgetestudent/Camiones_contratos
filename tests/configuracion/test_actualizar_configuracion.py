"""Tests unitarios dedicados a la función ReglasNegocio.actualizar_configuracion."""

from __future__ import annotations

from domain.reglas import ReglasNegocio
from tests.configuracion.base import BaseTestConfiguracion


class TestActualizarConfiguracion(BaseTestConfiguracion):
    """Pruebas dedicadas exclusivamente a la modificación de reglas de negocio globales."""

    def test_actualizacion_exitosa_parametros(self) -> None:
        cfg = ReglasNegocio.actualizar_configuracion(
            iva_porcentaje=0.15,
            tolerancia_max=0.05,
            anticipacion_min_h=5,
        )
        self.assertEqual(cfg["iva_porcentaje"], 0.15)
        self.assertEqual(cfg["tolerancia_max"], 0.05)
        self.assertEqual(cfg["anticipacion_min_h"], 5)

    def test_actualizacion_parcial(self) -> None:
        cfg = ReglasNegocio.actualizar_configuracion(iva_porcentaje=0.10)
        self.assertEqual(cfg["iva_porcentaje"], 0.10)
        self.assertEqual(cfg["tolerancia_max"], 0.01)  # Conserva valor previo
        self.assertEqual(cfg["anticipacion_min_h"], 2)

    def test_rechazo_iva_fuera_de_rango(self) -> None:
        with self.assertRaises(ValueError):
            ReglasNegocio.actualizar_configuracion(iva_porcentaje=-0.05)
        with self.assertRaises(ValueError):
            ReglasNegocio.actualizar_configuracion(iva_porcentaje=1.05)

    def test_rechazo_tolerancia_negativa(self) -> None:
        with self.assertRaises(ValueError):
            ReglasNegocio.actualizar_configuracion(tolerancia_max=-0.01)

    def test_rechazo_anticipacion_negativa(self) -> None:
        with self.assertRaises(ValueError):
            ReglasNegocio.actualizar_configuracion(anticipacion_min_h=-1)

