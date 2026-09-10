"""
Servicio de negocio para la gestion del ciclo de vida de los Contratos.
Orquesta los modelos de dominio, la maquina de estados y la capa de persistencia.
"""

from typing import List, Optional
from uuid import UUID

from dao.contrato_dao import ContratoDAO
from domain.maquina_estados import EstadoContrato, MaquinaEstadosContrato
from services.onboarding_service import OnboardingService, onboarding_service_instancia
from domain.modelos import ContratoCrear, ContratoModelo


class ServicioContrato:
    """Servicio que encapsula los casos de uso principales de Contratos."""

    def __init__(
        self,
        dao: ContratoDAO,
        onboarding_service: Optional[OnboardingService] = None,
    ):
        self.dao = dao
        self.onboarding_service = onboarding_service or onboarding_service_instancia

    def crear_contrato(self, datos: ContratoCrear) -> ContratoModelo:
        """Crea un nuevo contrato en estado BORRADOR y lo persiste via DAO."""
        if not self.onboarding_service.es_dador_aprobado(datos.id_empresa_generadora):
            raise PermissionError(
                f"La empresa generadora {datos.id_empresa_generadora} no cuenta con su verificacion KYC/Onboarding en estado APROBADO."
            )

        nuevo_contrato = ContratoModelo(**datos.model_dump())
        return self.dao.guardar(nuevo_contrato)

    def obtener_contrato(self, contrato_id: UUID) -> ContratoModelo:
        """Recupera un contrato por su ID unico. Lanza ValueError si no existe."""
        contrato = self.dao.obt_por_id(contrato_id)
        if not contrato:
            raise ValueError(f"El contrato con ID {contrato_id} no fue encontrado")
        return contrato

    def listar_contratos(self) -> List[ContratoModelo]:
        """Obtiene la lista completa de todos los contratos registrados."""
        return self.dao.obt_todos()

    def cambiar_estado(
        self,
        contrato_id: UUID,
        nuevo_estado: EstadoContrato,
        id_transportista: Optional[UUID] = None,
        id_camion: Optional[UUID] = None,
    ) -> ContratoModelo:
        """
        Solicita un cambio de estado evaluando las reglas de la Maquina de Estados
        y persiste los cambios aplicados.
        """
        contrato = self.obtener_contrato(contrato_id)

        contrato_actualizado = MaquinaEstadosContrato.cambiar_estado(
            contrato_data=contrato,
            nuevo_estado=nuevo_estado,
            id_transportista=id_transportista,
            id_camion=id_camion,
        )

        self.dao.actualizar(contrato_id, contrato_actualizado)
        return contrato_actualizado


# Alias para retrocompatibilidad
ContratoService = ServicioContrato