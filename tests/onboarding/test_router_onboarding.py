"""Tests para los endpoints de routers/onboarding_router.py."""

from __future__ import annotations

from uuid import uuid4
from domain.modelos_onboarding import (
    CargarDocumentoDTO,
    EstadoValidacion,
    TipoDocumento,
    ValidarDocumentoDTO,
    ValidarPerfilDadorDTO,
)
from routers.onboarding_router import (
    cargar_documento_transportista,
    consultar_estado_transportista,
    listar_dadores_pendientes_admin,
    listar_documentos_pendientes_admin,
    listar_documentos_transportista,
    obtener_perfil_dador,
    registrar_perfil_dador,
    validar_dador_admin,
    validar_documento_admin,
)
from tests.onboarding.base import BaseTestOnboarding


class TestRouterOnboarding(BaseTestOnboarding):
    """Pruebas dedicadas a las funciones endpoint de routers/onboarding_router.py."""

    def test_cargar_y_listar_documentos_transportista(self) -> None:
        payload = CargarDocumentoDTO(tipo=TipoDocumento.LICENCIA_CONDUCIR, archivo="doc.pdf")
        doc_creado = cargar_documento_transportista(payload=payload, x_user_id=self.transportista_id)
        self.assertEqual(doc_creado.tipo, TipoDocumento.LICENCIA_CONDUCIR)

        lista = listar_documentos_transportista(x_user_id=self.transportista_id)
        self.assertEqual(len(lista), 1)

    def test_consultar_estado_transportista(self) -> None:
        estado = consultar_estado_transportista(x_user_id=self.transportista_id)
        self.assertEqual(estado.estado_global, EstadoValidacion.PENDIENTE)

    def test_registrar_y_obtener_perfil_dador(self) -> None:
        dto = self.crear_perfil_dador_valido(self.dador_id)
        perfil = registrar_perfil_dador(payload=dto, x_user_id=self.dador_id)
        self.assertEqual(perfil.rut_id_empresa, dto.rut_id_empresa)

        recuperado = obtener_perfil_dador(x_user_id=self.dador_id)
        self.assertEqual(recuperado.id, perfil.id)

    def test_validar_documento_y_dador_admin(self) -> None:
        # Cargar documento
        payload_doc = CargarDocumentoDTO(tipo=TipoDocumento.LICENCIA_CONDUCIR, archivo="doc.pdf")
        doc = cargar_documento_transportista(payload_doc, x_user_id=self.transportista_id)

        # Listar pendientes admin
        pendientes_docs = listar_documentos_pendientes_admin()
        self.assertGreaterEqual(len(pendientes_docs), 1)

        # Validar admin
        doc_val = validar_documento_admin(documento_id=doc.id, payload=ValidarDocumentoDTO(estado=EstadoValidacion.APROBADO))
        self.assertEqual(doc_val.estado, EstadoValidacion.APROBADO)

        # Registrar perfil dador
        dto_dador = self.crear_perfil_dador_valido(self.dador_id)
        dador = registrar_perfil_dador(dto_dador, x_user_id=self.dador_id)

        # Listar dadores pendientes
        pendientes_dadores = listar_dadores_pendientes_admin()
        self.assertGreaterEqual(len(pendientes_dadores), 1)

        # Validar dador admin
        dador_val = validar_dador_admin(dador_id=dador.id, payload=ValidarPerfilDadorDTO(estado_validacion=EstadoValidacion.APROBADO))
        self.assertEqual(dador_val.estado_validacion, EstadoValidacion.APROBADO)
