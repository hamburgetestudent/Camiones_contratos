"""Tests unitarios dedicados a OnboardingService.es_dador_aprobado."""

from __future__ import annotations

from domain.modelos_onboarding import DatosFacturacion, EstadoValidacion
from tests.onboarding.base import BaseTestOnboarding


class TestEsDadorAprobado(BaseTestOnboarding):
    """Pruebas dedicadas a la verificación de autorización tributaria para dadores de carga."""

    def test_retorna_false_si_no_registrado_o_pendiente(self) -> None:
        self.assertFalse(self.onboarding_service.es_dador_aprobado(self.dador_id))

        perfil = self.onboarding_service.registrar_o_actualizar_perfil_dador(
            user_id=self.dador_id,
            rut_id_empresa="76123456-0",
            datos_facturacion=DatosFacturacion(razon_social="Test", direccion="Dir", correo_facturacion="a@b.cl"),
        )
        self.assertFalse(self.onboarding_service.es_dador_aprobado(self.dador_id))

    def test_retorna_true_si_perfil_aprobado(self) -> None:
        perfil = self.onboarding_service.registrar_o_actualizar_perfil_dador(
            user_id=self.dador_id,
            rut_id_empresa="76123456-0",
            datos_facturacion=DatosFacturacion(razon_social="Test", direccion="Dir", correo_facturacion="a@b.cl"),
        )
        self.onboarding_service.validar_dador(perfil.id, EstadoValidacion.APROBADO)
        self.assertTrue(self.onboarding_service.es_dador_aprobado(self.dador_id))