"""Tests unitarios dedicados a validaciones de modelos de Contratos (Pydantic)."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pydantic import ValidationError
from domain.modelos import TipoCarga, limpiar_texto
from tests.contratos.base import BaseTestContratos


class TestModelosContrato(BaseTestContratos):
    """Pruebas dedicadas a las validaciones de negocio en ContratoBase y ContratoCrear."""

    def test_limpiar_texto_normaliza_mayusculas_y_espacios(self) -> None:
        self.assertEqual(limpiar_texto("   santiago   centro  "), "SANTIAGO CENTRO")

    def test_peso_superior_a_capacidad_es_rechazado(self) -> None:
        with self.assertRaises(ValidationError) as ctx:
            self.crear_datos_contrato_validos(peso_total=12000.0, capacidad_kg=10000.0)
        self.assertIn("supera", str(ctx.exception).lower())

    def test_carga_peligrosa_requiere_numero_onu_valido(self) -> None:
        # Sin ONU debe fallar
        with self.assertRaises(ValidationError) as ctx:
            self.crear_datos_contrato_validos(tipo_carga=TipoCarga.PELIGROSA, numero_onu=None)
        self.assertIn("onu", str(ctx.exception).lower())

        # Con ONU válido (UN1203) debe tener éxito
        contrato = self.crear_datos_contrato_validos(tipo_carga=TipoCarga.PELIGROSA, numero_onu="UN1203")
        self.assertEqual(contrato.numero_onu, "UN1203")

    def test_cuadratura_financiera_monto_total_debe_coincidir(self) -> None:
        # Neto 100.000 + IVA 19.000 = Total 119.000 (Si se envía 150.000 debe fallar)
        with self.assertRaises(ValidationError) as ctx:
            self.crear_datos_contrato_validos(monto_neto=100000.0, monto_iva=19000.0, monto_total=150000.0)
        self.assertIn("no coincide", str(ctx.exception).lower())
