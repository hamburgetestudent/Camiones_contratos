"""Tests unitarios dedicados a la función OnboardingService.cargar_documento."""

from __future__ import annotations

from domain.modelos_onboarding import EstadoValidacion, TipoDocumento
from tests.onboarding.base import BaseTestOnboarding


class TestCargarDocumento(BaseTestOnboarding):
    """Pruebas dedicadas exclusivamente a la carga de documentos de transportistas."""

    def test_carga_inicial_documento_estado_pendiente(self) -> None:
        doc = self.onboarding_service.cargar_documento(
            user_id=self.transportista_id,
            tipo=TipoDocumento.LICENCIA_CONDUCIR,
            archivo="docs/mi_licencia.pdf",
        )
        self.assertEqual(doc.user_id, self.transportista_id)
        self.assertEqual(doc.tipo, TipoDocumento.LICENCIA_CONDUCIR)
        self.assertEqual(doc.archivo, "docs/mi_licencia.pdf")
        self.assertEqual(doc.estado, EstadoValidacion.PENDIENTE)

    def test_actualizacion_documento_existente_reinicia_a_pendiente(self) -> None:
        # Primera carga
        doc1 = self.onboarding_service.cargar_documento(
            user_id=self.transportista_id,
            tipo=TipoDocumento.PADRON_VEHICULO,
            archivo="docs/padron_antiguo.jpg",
        )
        # Se aprueba
        self.onboarding_service.validar_documento(doc1.id, EstadoValidacion.APROBADO)
        self.assertEqual(self.doc_dao.get_by_id(doc1.id).estado, EstadoValidacion.APROBADO)

        # Se vuelve a cargar el mismo tipo -> Debe actualizar archivo y volver a PENDIENTE
        doc2 = self.onboarding_service.cargar_documento(
            user_id=self.transportista_id,
            tipo=TipoDocumento.PADRON_VEHICULO,
            archivo="docs/padron_nuevo.jpg",
        )
        self.assertEqual(doc2.id, doc1.id)
        self.assertEqual(doc2.archivo, "docs/padron_nuevo.jpg")
        self.assertEqual(doc2.estado, EstadoValidacion.PENDIENTE)

