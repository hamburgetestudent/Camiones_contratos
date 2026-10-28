"""Tests unitarios dedicados a OnboardingService.registrar_o_actualizar_perfil_dador."""

from __future__ import annotations

from domain.modelos_onboarding import DatosFacturacion, EstadoValidacion
from tests.onboarding.base import BaseTestOnboarding


class TestRegistrarPerfilDador(BaseTestOnboarding):
    """Pruebas dedicadas a la creación y actualización de perfiles tributarios de dadores de carga."""

    def test_registro_inicial_perfil_dador_pendiente(self) -> None:
        datos_fac = DatosFacturacion(
            razon_social="Agrícola del Valle SpA",
            direccion="Camino Los Aromos km 4",
            correo_facturacion="dte@agricola.cl",
        )
        perfil = self.onboarding_service.registrar_o_actualizar_perfil_dador(
            user_id=self.dador_id,
            rut_id_empresa="77987654-3",
            datos_facturacion=datos_fac,
        )
        self.assertEqual(perfil.user_id, self.dador_id)
        self.assertEqual(perfil.rut_id_empresa, "77987654-3")
        self.assertEqual(perfil.datos_facturacion.razon_social, "Agrícola del Valle SpA")
        self.assertEqual(perfil.estado_validacion, EstadoValidacion.PENDIENTE)

    def test_actualizacion_perfil_existente(self) -> None:
        self.onboarding_service.registrar_o_actualizar_perfil_dador(
            user_id=self.dador_id,
            rut_id_empresa="77987654-3",
            datos_facturacion=DatosFacturacion(razon_social="Original", direccion="Dir 1", correo_facturacion="a@b.cl"),
        )
        # Actualización
        actualizado = self.onboarding_service.registrar_o_actualizar_perfil_dador(
            user_id=self.dador_id,
            rut_id_empresa="77987654-3",
            datos_facturacion=DatosFacturacion(razon_social="Nueva Razón", direccion="Dir 2", correo_facturacion="b@b.cl"),
        )
        self.assertEqual(actualizado.datos_facturacion.razon_social, "Nueva Razón")

