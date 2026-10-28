"""Tests unitarios dedicados a ServicioContrato.cambiar_estado."""

from __future__ import annotations

from domain.maquina_estados import EstadoContrato
from tests.contratos.base import BaseTestContratos


class TestCambiarEstado(BaseTestContratos):
    """Pruebas dedicadas a las transiciones de estado de contratos mediante el servicio."""

    def test_transicion_borrador_a_publicado(self) -> None:
        contrato = self.contrato_service.crear_contrato(self.crear_datos_contrato_validos())
        actualizado = self.contrato_service.cambiar_estado(contrato.id, EstadoContrato.PUBLICADO)
        self.assertEqual(actualizado.estado, EstadoContrato.PUBLICADO)

    def test_transicion_a_adjudicado_requiere_transportista(self) -> None:
        contrato = self.contrato_service.crear_contrato(self.crear_datos_contrato_validos())
        self.contrato_service.cambiar_estado(contrato.id, EstadoContrato.PUBLICADO)

        # Sin transportista debe fallar
        with self.assertRaises(ValueError) as ctx:
            self.contrato_service.cambiar_estado(contrato.id, EstadoContrato.ADJUDICADO)
        self.assertIn("id_transportista", str(ctx.exception).lower())

        # Con transportista debe tener éxito
        adjudicado = self.contrato_service.cambiar_estado(
            contrato.id,
            EstadoContrato.ADJUDICADO,
            id_transportista=self.transportista_id,
        )
        self.assertEqual(adjudicado.estado, EstadoContrato.ADJUDICADO)
        self.assertEqual(adjudicado.id_transportista, self.transportista_id)

    def test_transicion_invalida_lanza_value_error(self) -> None:
        contrato = self.contrato_service.crear_contrato(self.crear_datos_contrato_validos())
        with self.assertRaises(ValueError) as ctx:
            # No se puede pasar de BORRADOR a ENTREGADO directamente
            self.contrato_service.cambiar_estado(contrato.id, EstadoContrato.ENTREGADO)
        self.assertIn("no permitida", str(ctx.exception).lower())

