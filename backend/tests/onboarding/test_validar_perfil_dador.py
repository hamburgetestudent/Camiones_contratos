"""Tests unitarios dedicados a OnboardingService.validar_dador."""

from __future__ import annotations

from uuid import uuid4

from app.modules.onboarding.models import DatosFacturacion, EstadoValidacion
from tests.onboarding.base import BaseTestOnboarding


class TestValidarPerfilDador(BaseTestOnboarding):
    """Pruebas dedicadas a la acción administrativa de validación del perfil dador."""

    def test_validar_perfil_inexistente_lanza_value_error(self) -> None:
        with self.assertRaises(ValueError):
            self.onboarding_service.validar_dador(uuid4(), EstadoValidacion.APROBADO)

    def test_validar_perfil_cambia_estado(self) -> None:
        perfil = self.onboarding_service.registrar_o_actualizar_perfil_dador(
            user_id=self.dador_id,
            rut_id_empresa="76123456-0",
            datos_facturacion=DatosFacturacion(
                razon_social="Test", direccion="Dir", correo_facturacion="a@b.cl"
            ),
        )
        aprobado = self.onboarding_service.validar_dador(
            perfil.id, EstadoValidacion.APROBADO
        )
        self.assertIsNotNone(aprobado)
        self.assertEqual(aprobado.estado_validacion, EstadoValidacion.APROBADO)

    def test_listar_dadores_pendientes(self) -> None:
        perfil = self.onboarding_service.registrar_o_actualizar_perfil_dador(
            user_id=self.dador_id,
            rut_id_empresa="76123456-0",
            datos_facturacion=DatosFacturacion(
                razon_social="Test", direccion="Dir", correo_facturacion="a@b.cl"
            ),
        )
        pendientes = self.onboarding_service.listar_dadores_pendientes_admin()
        self.assertEqual(len(pendientes), 1)
        self.assertEqual(pendientes[0].id, perfil.id)

    def test_volver_a_pendiente_conserva_el_rechazo(self) -> None:
        perfil = self.onboarding_service.registrar_o_actualizar_perfil_dador(
            self.dador_id, "76123456-0",
            DatosFacturacion(razon_social="Test", direccion="Dir", correo_facturacion="a@b.cl"),
        )
        self.onboarding_service.validar_dador(perfil.id, EstadoValidacion.RECHAZADO)
        with self.assertRaisesRegex(ValueError, "APROBADO o RECHAZADO"):
            self.onboarding_service.validar_dador(perfil.id, EstadoValidacion.PENDIENTE)
        guardado = self.onboarding_service.obtener_perfil_dador(self.dador_id)
        self.assertEqual(guardado.estado_validacion, EstadoValidacion.RECHAZADO)
