"""Base DRY para pruebas de Onboarding."""

from __future__ import annotations

from uuid import UUID, uuid4
from dao.onboarding_dao import DadorCargaDAOInMemory, DocumentoDAOInMemory
from domain.modelos_onboarding import (
    CrearPerfilDadorDTO,
    DatosFacturacion,
    EstadoValidacion,
    TipoDocumento,
)
from services.onboarding_service import (
    DOCUMENTOS_REQUERIDOS_TRANSPORTISTA,
    OnboardingService,
)
import services.onboarding_service as onboarding_service_modulo
from tests.base import BaseTestCase


class BaseTestOnboarding(BaseTestCase):
    """Clase base DRY para pruebas de onboarding y compliance KYC.
    
    Hereda de tests.base.BaseTestCase y provee aislamiento
    completo de servicios y DAOs en memoria.
    """

    def setUp(self) -> None:
        super().setUp()
        self.doc_dao = DocumentoDAOInMemory()
        self.dador_dao = DadorCargaDAOInMemory()
        self.onboarding_service = OnboardingService(
            documento_dao=self.doc_dao,
            dador_dao=self.dador_dao,
        )

        # Sobrescribir singleton para routers
        self._orig_singleton = onboarding_service_modulo.onboarding_service_instancia
        onboarding_service_modulo.onboarding_service_instancia = self.onboarding_service

        self.transportista_id = uuid4()
        self.dador_id = uuid4()

    def tearDown(self) -> None:
        onboarding_service_modulo.onboarding_service_instancia = self._orig_singleton
        super().tearDown()

    def cargar_los_5_documentos(
        self,
        user_id: UUID,
        estado: EstadoValidacion = EstadoValidacion.PENDIENTE,
    ) -> None:
        """Helper DRY para cargar los 5 documentos reglamentarios."""
        extensiones = {
            TipoDocumento.LICENCIA_CONDUCIR: "licencia.pdf",
            TipoDocumento.PADRON_VEHICULO: "padron.jpg",
            TipoDocumento.REVISION_TECNICA: "revision.jpeg",
            TipoDocumento.SEGURO_CARGA: "seguro.png",
            TipoDocumento.ANTECEDENTES: "antecedentes.pdf",
        }
        for tipo, archivo in extensiones.items():
            doc = self.onboarding_service.cargar_documento(
                user_id=user_id,
                tipo=tipo,
                archivo=archivo,
            )
            if estado != EstadoValidacion.PENDIENTE:
                self.onboarding_service.validar_documento(doc.id, estado)

    def crear_perfil_dador_valido(
        self,
        user_id: UUID,
        rut: str = "76.123.456-0",
        correo: str = "facturacion@empresa.cl",
    ) -> CrearPerfilDadorDTO:
        """Helper DRY para crear un DTO de perfil tributario válido."""
        return CrearPerfilDadorDTO(
            rut_id_empresa=rut,
            datos_facturacion=DatosFacturacion(
                razon_social="Sociedad de Transporte del Sur",
                direccion="Calle Principal 100",
                correo_facturacion=correo,
            ),
        )

