"""Tests para los endpoints de routers/contratos_router.py."""

from __future__ import annotations

from uuid import uuid4
from domain.maquina_estados import EstadoContrato
from routers.contratos_router import (
    SolicitudCambioEstado,
    cambiar_estado_contrato,
    crear_contrato,
    listar_contratos,
    obtener_contrato,
)
from tests.contratos.base import BaseTestContratos


class TestRouterContratos(BaseTestContratos):
    """Pruebas dedicadas a las funciones endpoint de routers/contratos_router.py."""

    def test_crear_obtener_y_listar_contrato_endpoint(self) -> None:
        datos = self.crear_datos_contrato_validos()
        contrato = crear_contrato(datos, contrato_service=self.contrato_service)
        self.assertEqual(contrato.estado, EstadoContrato.BORRADOR)

        recuperado = obtener_contrato(contrato.id, contrato_service=self.contrato_service)
        self.assertEqual(recuperado.id, contrato.id)

        todos = listar_contratos(contrato_service=self.contrato_service)
        self.assertEqual(len(todos), 1)

    def test_cambiar_estado_contrato_endpoint(self) -> None:
        datos = self.crear_datos_contrato_validos()
        contrato = crear_contrato(datos, contrato_service=self.contrato_service)

        payload = SolicitudCambioEstado(nuevo_estado=EstadoContrato.PUBLICADO)
        actualizado = cambiar_estado_contrato(
            contrato_id=contrato.id,
            payload=payload,
            contrato_service=self.contrato_service,
        )
        self.assertEqual(actualizado.estado, EstadoContrato.PUBLICADO)

