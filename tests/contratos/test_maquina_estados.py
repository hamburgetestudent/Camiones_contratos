"""Tests unitarios dedicados a MaquinaEstadosContrato y MaquinaEstadosBase."""

from __future__ import annotations

from domain.maquina_estados import EstadoContrato, MaquinaEstadosContrato
from tests.contratos.base import BaseTestContratos


class TestMaquinaEstados(BaseTestContratos):
    """Pruebas dedicadas a las reglas teóricas de la máquina de estados de contratos."""

    def test_transiciones_permitidas_desde_borrador(self) -> None:
        permitidos = MaquinaEstadosContrato.obtener_estados(EstadoContrato.BORRADOR)
        self.assertEqual(
            permitidos,
            {
                EstadoContrato.PUBLICADO,
                EstadoContrato.EN_SUBASTA,
                EstadoContrato.CANCELADO,
            },
        )

    def test_validar_transicion_metodo(self) -> None:
        self.assertTrue(MaquinaEstadosContrato.validar_transicion(EstadoContrato.BORRADOR, EstadoContrato.PUBLICADO))
        self.assertFalse(MaquinaEstadosContrato.validar_transicion(EstadoContrato.BORRADOR, EstadoContrato.ENTREGADO))

    def test_estados_terminales(self) -> None:
        self.assertTrue(MaquinaEstadosContrato.estado_terminal(EstadoContrato.FINALIZADO))
        self.assertTrue(MaquinaEstadosContrato.estado_terminal(EstadoContrato.CANCELADO))
        self.assertFalse(MaquinaEstadosContrato.estado_terminal(EstadoContrato.PUBLICADO))

    def test_transicion_desde_en_disputa(self) -> None:
        permitidos = MaquinaEstadosContrato.obtener_estados(EstadoContrato.EN_DISPUTA)
        self.assertEqual(permitidos, {EstadoContrato.FINALIZADO, EstadoContrato.CANCELADO})

