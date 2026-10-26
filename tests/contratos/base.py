"""Base DRY para pruebas de Contratos y ciclo de vida de carga."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4
from dao.contrato_dao import ContratoDAOMemoria
from dao.onboarding_dao import DadorCargaDAOInMemory, DocumentoDAOInMemory
from domain.modelos import ContratoCrear, Moneda, TipoCarga
from domain.modelos_onboarding import DatosFacturacion, EstadoValidacion
from services.contrato_service import ServicioContrato
from services.onboarding_service import OnboardingService
from tests.base import BaseTestCase


class BaseTestContratos(BaseTestCase):
    """Clase base DRY para pruebas del ciclo de vida de contratos.
    
    Hereda de tests.base.BaseTestCase y provee aislamiento
    completo de servicios, DAOs y generadores de datos semilla válidos.
    """

    def setUp(self) -> None:
        super().setUp()
        self.contrato_dao = ContratoDAOMemoria()
        self.doc_dao = DocumentoDAOInMemory()
        self.dador_dao = DadorCargaDAOInMemory()
        self.onboarding_service = OnboardingService(
            documento_dao=self.doc_dao,
            dador_dao=self.dador_dao,
        )
        self.contrato_service = ServicioContrato(
            dao=self.contrato_dao,
            onboarding_service=self.onboarding_service,
        )

        # Empresa generadora aprobada por defecto
        self.empresa_aprobada_id = uuid4()
        perfil = self.onboarding_service.registrar_o_actualizar_perfil_dador(
            user_id=self.empresa_aprobada_id,
            rut_id_empresa="76123456-0",
            datos_facturacion=DatosFacturacion(
                razon_social="Generadora Mayorista S.A.",
                direccion="Parque Industrial 500",
                correo_facturacion="dte@generadora.cl",
            ),
        )
        self.onboarding_service.validar_dador(perfil.id, EstadoValidacion.APROBADO)

        self.transportista_id = uuid4()
        self.camion_id = uuid4()

    def crear_datos_contrato_validos(
        self,
        empresa_id: UUID | None = None,
        monto_neto: float = 100000.0,
        monto_iva: float = 19000.0,
        monto_total: float = 119000.0,
        peso_total: float = 5000.0,
        capacidad_kg: float = 10000.0,
        tipo_carga: TipoCarga = TipoCarga.GENERAL,
        numero_onu: str | None = None,
    ) -> ContratoCrear:
        """Helper DRY para instanciar contratos válidos con todas las reglas de negocio."""
        ahora = datetime.now(UTC)
        return ContratoCrear(
            id_empresa_generadora=empresa_id or self.empresa_aprobada_id,
            origen="SANTIAGO",
            destino="CONCEPCION",
            f_cierre_postulaciones=ahora + timedelta(hours=3),
            f_estimada_salida=ahora + timedelta(hours=6),
            f_estimada_llegada=ahora + timedelta(hours=14),
            input_camionKG=capacidad_kg,
            tipo_carga=tipo_carga,
            peso_total=peso_total,
            distancia_km=500.0,
            moneda=Moneda.CLP,
            monto_neto=monto_neto,
            monto_iva=monto_iva,
            monto_total=monto_total,
            numero_onu=numero_onu,
        )

