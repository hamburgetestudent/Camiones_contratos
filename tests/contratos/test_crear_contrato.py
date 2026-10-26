"""Tests unitarios dedicados a ServicioContrato.crear_contrato."""

from __future__ import annotations

from uuid import uuid4
from domain.maquina_estados import EstadoContrato
from tests.contratos.base import BaseTestContratos


class TestCrearContrato(BaseTestContratos):
    """Pruebas dedicadas exclusivamente a la creación y persistencia de contratos."""

    def test_creacion_exitosa_contrato_estado_borrador(self) -> None:
        datos = self.crear_datos_contrato_validos()
        contrato = self.contrato_service.crear_contrato(datos)

        self.assertIsNotNone(contrato.id)
        self.assertEqual(contrato.id_empresa_generadora, self.empresa_aprobada_id)
        self.assertEqual(contrato.estado, EstadoContrato.BORRADOR)
        self.assertEqual(contrato.origen, "SANTIAGO")
        self.assertEqual(contrato.destino, "CONCEPCION")

        # Verificar persistencia en DAO
        guardado = self.contrato_dao.obtener_por_id(contrato.id)
        self.assertIsNotNone(guardado)

    def test_rechazo_empresa_generadora_sin_onboarding_aprobado(self) -> None:
        empresa_no_aprobada = uuid4()
        datos = self.crear_datos_contrato_validos(empresa_id=empresa_no_aprobada)

        with self.assertRaises(PermissionError) as ctx:
            self.contrato_service.crear_contrato(datos)

        self.assertIn("no cuenta con su verificacion kyc/onboarding", str(ctx.exception).lower())

