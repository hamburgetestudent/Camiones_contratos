"""Base DRY para pruebas de Onboarding."""

from __future__ import annotations

from uuid import UUID, uuid4

from domain.modelos_onboarding import (
    CrearPerfilDadorDTO,
    DatosFacturacion,
    DocumentoTransportista,
    EstadoValidacion,
    TipoDocumento,
)
from services.onboarding_service import (
    OnboardingService,
)
from tests.base import BaseTestCase


class BaseTestOnboarding(BaseTestCase):
    """Clase base DRY para pruebas de onboarding y compliance KYC.

    Hereda de tests.base.BaseTestCase y provee aislamiento
    completo de servicios sobre una base SQLite temporal. El singleton que usan
    los routers apunta a la misma base (ver ``preparar_bd_aislada``).
    """

    def setUp(self) -> None:
        super().setUp()
        self.db_path = self.preparar_bd_aislada()
        self.onboarding_service = OnboardingService(db_path=self.db_path)

        self.transportista_id = uuid4()
        self.dador_id = uuid4()

    def obtener_documento(
        self, user_id: UUID, tipo: TipoDocumento
    ) -> DocumentoTransportista | None:
        """Lee de SQLite el documento de un tipo dado para un transportista."""
        for doc in self.onboarding_service.listar_documentos_transportista(user_id):
            if doc.tipo == tipo:
                return doc
        return None

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
