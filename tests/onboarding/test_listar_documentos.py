"""Tests unitarios dedicados a OnboardingService.listar_documentos_transportista."""

from __future__ import annotations

from domain.modelos_onboarding import TipoDocumento
from tests.onboarding.base import BaseTestOnboarding


class TestListarDocumentos(BaseTestOnboarding):
    """Pruebas dedicadas exclusivamente al listado de documentos por transportista."""

    def test_listar_documentos_transportista_vacio(self) -> None:
        docs = self.onboarding_service.listar_documentos_transportista(self.transportista_id)
        self.assertEqual(docs, [])

    def test_listar_documentos_retorna_solo_los_del_transportista(self) -> None:
        self.onboarding_service.cargar_documento(self.transportista_id, TipoDocumento.LICENCIA_CONDUCIR, "lic.pdf")
        self.onboarding_service.cargar_documento(self.transportista_id, TipoDocumento.SEGURO_CARGA, "seg.pdf")

        # Cargar para otro usuario
        self.onboarding_service.cargar_documento(self.dador_id, TipoDocumento.LICENCIA_CONDUCIR, "otro.pdf")

        docs = self.onboarding_service.listar_documentos_transportista(self.transportista_id)
        self.assertEqual(len(docs), 2)
        tipos = {d.tipo for d in docs}
        self.assertEqual(tipos, {TipoDocumento.LICENCIA_CONDUCIR, TipoDocumento.SEGURO_CARGA})

