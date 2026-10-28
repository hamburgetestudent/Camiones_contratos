"""Tests unitarios dedicados a OnboardingService.validar_documento."""

from __future__ import annotations

from uuid import uuid4
from domain.modelos_onboarding import EstadoValidacion, TipoDocumento
from tests.onboarding.base import BaseTestOnboarding


class TestValidarDocumento(BaseTestOnboarding):
    """Pruebas dedicadas a la acción administrativa de aprobación/rechazo de documentos."""

    def test_validar_documento_inexistente_lanza_value_error(self) -> None:
        with self.assertRaises(ValueError):
            self.onboarding_service.validar_documento(uuid4(), EstadoValidacion.APROBADO)

    def test_validar_documento_aprobado_y_rechazado(self) -> None:
        doc = self.onboarding_service.cargar_documento(self.transportista_id, TipoDocumento.LICENCIA_CONDUCIR, "lic.pdf")
        doc_aprobado = self.onboarding_service.validar_documento(doc.id, EstadoValidacion.APROBADO)
        self.assertIsNotNone(doc_aprobado)
        self.assertEqual(doc_aprobado.estado, EstadoValidacion.APROBADO)

        doc_rechazado = self.onboarding_service.validar_documento(doc.id, EstadoValidacion.RECHAZADO)
        self.assertIsNotNone(doc_rechazado)
        self.assertEqual(doc_rechazado.estado, EstadoValidacion.RECHAZADO)

    def test_listar_documentos_pendientes(self) -> None:
        doc1 = self.onboarding_service.cargar_documento(self.transportista_id, TipoDocumento.LICENCIA_CONDUCIR, "lic.pdf")
        doc2 = self.onboarding_service.cargar_documento(self.transportista_id, TipoDocumento.PADRON_VEHICULO, "pad.jpg")
        self.onboarding_service.validar_documento(doc1.id, EstadoValidacion.APROBADO)

        pendientes = self.onboarding_service.listar_documentos_pendientes_admin()
        self.assertEqual(len(pendientes), 1)
        self.assertEqual(pendientes[0].id, doc2.id)
