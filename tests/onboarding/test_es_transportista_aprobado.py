"""Tests unitarios dedicados a OnboardingService.es_transportista_aprobado."""

from __future__ import annotations

from domain.modelos_onboarding import EstadoValidacion
from tests.onboarding.base import BaseTestOnboarding


class TestEsTransportistaAprobado(BaseTestOnboarding):
    """Pruebas dedicadas a la comprobación rápida del estado de habilitación del transportista."""

    def test_retorna_false_si_no_ha_completado_onboarding(self) -> None:
        self.assertFalse(self.onboarding_service.es_transportista_aprobado(self.transportista_id))

    def test_retorna_true_si_tiene_onboarding_aprobado(self) -> None:
        self.cargar_los_5_documentos(self.transportista_id, estado=EstadoValidacion.APROBADO)
        self.assertTrue(self.onboarding_service.es_transportista_aprobado(self.transportista_id))