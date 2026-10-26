"""Tests unitarios dedicados a validaciones Pydantic de modelos de Onboarding."""

from __future__ import annotations

from pydantic import ValidationError
from domain.modelos_onboarding import (
    CargarDocumentoDTO,
    CrearPerfilDadorDTO,
    DatosFacturacion,
    TipoDocumento,
)
from tests.onboarding.base import BaseTestOnboarding


class TestModelosOnboarding(BaseTestOnboarding):
    """Pruebas de esquemas y validadores de onboarding (extensiones de archivo y RUT chileno con DV módulo 11)."""

    def test_extensiones_permitidas_documentos(self) -> None:
        for ext in (".pdf", ".jpg", ".jpeg", ".png", ".PDF", ".PNG"):
            dto = CargarDocumentoDTO(tipo=TipoDocumento.LICENCIA_CONDUCIR, archivo=f"archivo{ext}")
            self.assertEqual(dto.archivo, f"archivo{ext}")

    def test_extension_invalida_documentos_rechazada(self) -> None:
        for ext in (".doc", ".exe", ".txt", ".zip"):
            with self.assertRaises(ValidationError):
                CargarDocumentoDTO(tipo=TipoDocumento.LICENCIA_CONDUCIR, archivo=f"archivo{ext}")

    def test_ruts_chilenos_validos_con_modulo_11(self) -> None:
        ruts_validos = [
            "76.123.456-0",
            "76123456-0",
            "77.987.654-3",
            "11.111.111-1",
            "60.803.000-K",
            "60803000-k",
            "12.345.678-5",
        ]
        for rut in ruts_validos:
            dto = self.crear_perfil_dador_valido(self.dador_id, rut=rut)
            self.assertTrue(len(dto.rut_id_empresa) >= 3)

    def test_rut_con_dv_invalido_rechazado(self) -> None:
        ruts_invalidos = ["76.123.456-9", "77.987.654-K", "11.111.111-2"]
        for rut in ruts_invalidos:
            with self.assertRaises(ValidationError) as ctx:
                self.crear_perfil_dador_valido(self.dador_id, rut=rut)
            self.assertIn("dígito verificador", str(ctx.exception).lower())

    def test_validacion_correo_facturacion(self) -> None:
        with self.assertRaises(ValidationError):
            DatosFacturacion(razon_social="Empresa", direccion="Dir", correo_facturacion="invalido_sin_arroba")