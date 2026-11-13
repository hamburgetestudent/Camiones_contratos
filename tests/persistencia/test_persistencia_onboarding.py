"""Tests unitarios de la persistencia de KYC (documentos y perfiles de dador) en SQLite."""

from __future__ import annotations

from uuid import uuid4

from domain.modelos_onboarding import (
    DatosFacturacion,
    EstadoValidacion,
    TipoDocumento,
)
from services.onboarding_service import OnboardingService
from tests.persistencia.base import BaseTestPersistencia


class TestPersistenciaOnboarding(BaseTestPersistencia):
    """Pruebas dedicadas a la persistencia relacional de KYC en SQLite."""

    def setUp(self) -> None:
        super().setUp()
        self.servicio = OnboardingService(db_path=self.db_path)

    def test_cargar_documento_queda_guardado_en_la_tabla(self) -> None:
        user_id = uuid4()
        doc = self.servicio.cargar_documento(
            user_id, TipoDocumento.LICENCIA_CONDUCIR, "archivos/licencia.pdf"
        )

        filas = self.consultar(
            "SELECT id, tipo, archivo, estado FROM documentos_transportista WHERE user_id = ?",
            (str(user_id),),
        )
        self.assertEqual(len(filas), 1)
        self.assertEqual(filas[0]["id"], str(doc.id))
        self.assertEqual(filas[0]["tipo"], "LICENCIA_CONDUCIR")
        self.assertEqual(filas[0]["archivo"], "archivos/licencia.pdf")
        self.assertEqual(filas[0]["estado"], "PENDIENTE")

        docs_usuario = self.servicio.listar_documentos_transportista(user_id)
        self.assertEqual(len(docs_usuario), 1)
        self.assertEqual(docs_usuario[0].tipo, TipoDocumento.LICENCIA_CONDUCIR)

    def test_recargar_mismo_tipo_actualiza_la_fila_existente(self) -> None:
        user_id = uuid4()
        doc = self.servicio.cargar_documento(
            user_id, TipoDocumento.PADRON_VEHICULO, "docs/padron_1.jpg"
        )
        self.servicio.validar_documento(doc.id, EstadoValidacion.APROBADO)
        self.servicio.cargar_documento(
            user_id, TipoDocumento.PADRON_VEHICULO, "docs/padron_2.jpg"
        )

        filas = self.consultar(
            "SELECT archivo, estado FROM documentos_transportista WHERE user_id = ?",
            (str(user_id),),
        )
        self.assertEqual(len(filas), 1)  # UNIQUE(user_id, tipo): una sola fila
        self.assertEqual(filas[0]["archivo"], "docs/padron_2.jpg")
        self.assertEqual(filas[0]["estado"], "PENDIENTE")

    def test_registrar_perfil_dador_queda_guardado_en_la_tabla(self) -> None:
        user_id = uuid4()
        perfil = self.servicio.registrar_o_actualizar_perfil_dador(
            user_id,
            "76123456-0",
            DatosFacturacion(
                razon_social="Empresa Minera SpA",
                direccion="Av. Matta 456",
                correo_facturacion="factura@minera.cl",
            ),
        )

        filas = self.consultar(
            "SELECT id, rut_id_empresa, razon_social, estado_validacion "
            "FROM dadores_carga WHERE user_id = ?",
            (str(user_id),),
        )
        self.assertEqual(len(filas), 1)
        self.assertEqual(filas[0]["id"], str(perfil.id))
        self.assertEqual(filas[0]["razon_social"], "Empresa Minera SpA")
        self.assertEqual(filas[0]["estado_validacion"], "PENDIENTE")

        recuperado = self.servicio.obtener_perfil_dador(user_id)
        assert recuperado is not None
        self.assertEqual(recuperado.rut_id_empresa, "76123456-0")
        self.assertEqual(
            recuperado.datos_facturacion.correo_facturacion, "factura@minera.cl"
        )

    def test_actualizar_perfil_dador_reinicia_validacion_sin_duplicar(self) -> None:
        user_id = uuid4()
        datos = DatosFacturacion(
            razon_social="Empresa Uno",
            direccion="Calle 1",
            correo_facturacion="uno@empresa.cl",
        )
        perfil = self.servicio.registrar_o_actualizar_perfil_dador(
            user_id, "76123456-0", datos
        )
        self.servicio.validar_dador(perfil.id, EstadoValidacion.APROBADO)
        self.assertTrue(self.servicio.es_dador_aprobado(user_id))

        self.servicio.registrar_o_actualizar_perfil_dador(user_id, "76123456-0", datos)

        filas = self.consultar(
            "SELECT estado_validacion FROM dadores_carga WHERE user_id = ?",
            (str(user_id),),
        )
        self.assertEqual(len(filas), 1)
        self.assertEqual(filas[0]["estado_validacion"], "PENDIENTE")
        self.assertFalse(self.servicio.es_dador_aprobado(user_id))
