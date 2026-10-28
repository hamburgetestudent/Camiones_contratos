"""Tests unitarios dedicados a ServicioContrato.obtener_contrato."""

from __future__ import annotations

from uuid import uuid4
from tests.contratos.base import BaseTestContratos


class TestObtenerContrato(BaseTestContratos):
    """Pruebas dedicadas exclusivamente a la consulta de un contrato por su ID."""

    def test_obtener_contrato_existente(self) -> None:
        creado = self.contrato_service.crear_contrato(self.crear_datos_contrato_validos())
        recuperado = self.contrato_service.obtener_contrato(creado.id)
        self.assertEqual(recuperado.id, creado.id)

    def test_obtener_contrato_inexistente_lanza_value_error(self) -> None:
        id_aleatorio = uuid4()
        with self.assertRaises(ValueError) as ctx:
            self.contrato_service.obtener_contrato(id_aleatorio)
        self.assertIn("no fue encontrado", str(ctx.exception).lower())

