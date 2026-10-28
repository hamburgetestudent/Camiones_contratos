"""Tests unitarios dedicados a OnboardingService.obtener_estado_transportista."""

from __future__ import annotations

from domain.modelos_onboarding import EstadoValidacion, TipoDocumento
from tests.onboarding.base import BaseTestOnboarding


class TestObtenerEstadoTransportista(BaseTestOnboarding):
    """Pruebas dedicadas al cálculo de estado global del transportista (APROBADO, PENDIENTE, RECHAZADO)."""

    def test_estado_pendiente_cuando_faltan_documentos(self) -> None:
        self.onboarding_service.cargar_documento(self.transportista_id, TipoDocumento.LICENCIA_CONDUCIR, "lic.pdf")
        estado_dto = self.onboarding_service.obtener_estado_transportista(self.transportista_id)
        self.assertEqual(estado_dto.estado_global, EstadoValidacion.PENDIENTE)
        self.assertEqual(len(estado_dto.faltantes), 4)

    def test_estado_aprobado_cuando_5_documentos_estan_aprobados(self) -> None:
        self.cargar_los_5_documentos(self.transportista_id, estado=EstadoValidacion.APROBADO)
        estado_dto = self.onboarding_service.obtener_estado_transportista(self.transportista_id)
        self.assertEqual(estado_dto.estado_global, EstadoValidacion.APROBADO)
        self.assertEqual(len(estado_dto.faltantes), 0)

    def test_estado_rechazado_si_al_menos_uno_esta_rechazado(self) -> None:
        self.cargar_los_5_documentos(self.transportista_id, estado=EstadoValidacion.APROBADO)
        # Rechazamos la revisión técnica
        doc_rev = self.doc_dao.get_by_user_and_tipo(self.transportista_id, TipoDocumento.REVISION_TECNICA)
        self.onboarding_service.validar_documento(doc_rev.id, EstadoValidacion.RECHAZADO)

        estado_dto = self.onboarding_service.obtener_estado_transportista(self.transportista_id)
        self.assertEqual(estado_dto.estado_global, EstadoValidacion.RECHAZADO)

