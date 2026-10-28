"""Tests unitarios dedicados a ServicioContrato.listar_contratos."""

from __future__ import annotations

from tests.contratos.base import BaseTestContratos


class TestListarContratos(BaseTestContratos):
    """Pruebas dedicadas exclusivamente al listado de contratos."""

    def test_listar_contratos_inicial_vacio(self) -> None:
        self.assertEqual(self.contrato_service.listar_contratos(), [])

    def test_listar_multiples_contratos(self) -> None:
        c1 = self.contrato_service.crear_contrato(self.crear_datos_contrato_validos())
        c2 = self.contrato_service.crear_contrato(self.crear_datos_contrato_validos())
        lista = self.contrato_service.listar_contratos()
        self.assertEqual(len(lista), 2)
        ids = {c.id for c in lista}
        self.assertEqual(ids, {c1.id, c2.id})

