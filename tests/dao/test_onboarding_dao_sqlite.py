"""Tests unitarios dedicados a DocumentoDAOSQLite y DadorCargaDAOSQLite."""

from __future__ import annotations

from uuid import uuid4
from dao.onboarding_dao import DadorCargaDAOSQLite, DocumentoDAOSQLite
from dao.sqlite_db import inicializar_bd
from domain.modelos_onboarding import (
    DadorCarga,
    DatosFacturacion,
    DocumentoTransportista,
    EstadoValidacion,
    TipoDocumento,
)
from tests.dao.base import BaseTestDAO


class TestOnboardingDAOSQLite(BaseTestDAO):
    """Pruebas dedicadas a la persistencia relacional de KYC en SQLite."""

    def setUp(self) -> None:
        super().setUp()
        inicializar_bd(self.db_path)
        self.doc_dao = DocumentoDAOSQLite(self.db_path)
        self.dador_dao = DadorCargaDAOSQLite(self.db_path)

    def test_guardar_y_obtener_documento_transportista(self) -> None:
        user_id = uuid4()
        doc = DocumentoTransportista(
            id=uuid4(),
            user_id=user_id,
            tipo=TipoDocumento.LICENCIA_CONDUCIR,
            archivo="archivos/licencia.pdf",
            estado=EstadoValidacion.PENDIENTE,
        )
        guardado = self.doc_dao.save(doc)
        self.assertEqual(guardado.id, doc.id)

        docs_usuario = self.doc_dao.get_by_user_id(user_id)
        self.assertEqual(len(docs_usuario), 1)
        self.assertEqual(docs_usuario[0].tipo, TipoDocumento.LICENCIA_CONDUCIR)

    def test_guardar_y_obtener_perfil_dador(self) -> None:
        user_id = uuid4()
        perfil = DadorCarga(
            id=uuid4(),
            user_id=user_id,
            rut_id_empresa="76123456-0",
            datos_facturacion=DatosFacturacion(
                razon_social="Empresa Minera SpA",
                direccion="Av. Matta 456",
                correo_facturacion="factura@minera.cl",
            ),
            estado_validacion=EstadoValidacion.PENDIENTE,
        )
        guardado = self.dador_dao.save(perfil)
        self.assertEqual(guardado.id, perfil.id)

        recuperado = self.dador_dao.get_by_user_id(user_id)
        self.assertIsNotNone(recuperado)
        assert recuperado is not None
        self.assertEqual(recuperado.rut_id_empresa, "76123456-0")
        self.assertEqual(recuperado.datos_facturacion.razon_social, "Empresa Minera SpA")

