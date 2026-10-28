"""Tests unitarios dedicados a OnboardingService.obtener_perfil_dador."""

from __future__ import annotations

from domain.modelos_onboarding import DatosFacturacion
from tests.onboarding.base import BaseTestOnboarding


class TestObtenerPerfilDador(BaseTestOnboarding):
    """Pruebas dedicadas a la consulta del perfil tributario del dador."""

    def test_obtener_perfil_inexistente_retorna_none(self) -> None:
        self.assertIsNone(self.onboarding_service.obtener_perfil_dador(self.dador_id))

    def test_obtener_perfil_existente(self) -> None:
        self.onboarding_service.registrar_o_actualizar_perfil_dador(
            user_id=self.dador_id,
            rut_id_empresa="76123456-0",
            datos_facturacion=DatosFacturacion(razon_social="Test", direccion="Dir", correo_facturacion="a@b.cl"),
        )
        perfil = self.onboarding_service.obtener_perfil_dador(self.dador_id)
        self.assertIsNotNone(perfil)
        assert perfil is not None
        self.assertEqual(perfil.rut_id_empresa, "76123456-0")

