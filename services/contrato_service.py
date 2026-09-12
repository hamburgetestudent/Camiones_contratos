"""Servicio de negocio para la gestion del ciclo de vida de los Contratos.

Orquesta los modelos de dominio, la maquina de estados y la capa de persistencia.
"""

from uuid import UUID

from dao.contrato_dao import ContratoDAO
from domain.auditoria import AccionAuditoria, EntidadAuditable
from domain.maquina_estados import EstadoContrato, MaquinaEstadosContrato
from domain.modelos import ContratoCrear, ContratoModelo
from domain.reglas import ReglasNegocio
from services.auditoria_service import ServicioAuditoria
from services.onboarding_service import OnboardingService, onboarding_service_instancia


class ServicioContrato:
    """Servicio que encapsula los casos de uso principales de Contratos."""

    def __init__(
        self,
        dao: ContratoDAO,
        onboarding_service: OnboardingService | None = None,
        auditoria_service: ServicioAuditoria | None = None,
    ) -> None:
        self.dao = dao
        self.onboarding_service = onboarding_service or onboarding_service_instancia
        self.auditoria_service = auditoria_service

    def crear_contrato(self, datos: ContratoCrear) -> ContratoModelo:
        """Crea un nuevo contrato en estado BORRADOR y lo persiste via DAO."""
        if not self.onboarding_service.es_dador_aprobado(datos.id_empresa_generadora):
            raise PermissionError(
                f"La empresa generadora {datos.id_empresa_generadora} no cuenta con su "
                "verificacion KYC/Onboarding en estado APROBADO."
            )

        nuevo_contrato = ContratoModelo(**datos.model_dump())
        contrato_guardado = self.dao.guardar(nuevo_contrato)
        if self.auditoria_service:
            self.auditoria_service.registrar_evento(
                transporte_id=contrato_guardado.id,
                entidad=EntidadAuditable.CONTRATO,
                entidad_id=contrato_guardado.id,
                accion=AccionAuditoria.CONTRATO_CREADO,
                actor_id=datos.id_empresa_generadora,
                datos=contrato_guardado.model_dump(mode="json"),
                bases_aplicadas=ReglasNegocio.obtener_configuracion(),
                informacion_utilizada={"origen": "solicitud_creacion_contrato"},
            )
        return contrato_guardado

    def obtener_contrato(self, contrato_id: UUID) -> ContratoModelo:
        """Recupera un contrato por su ID unico. Lanza ValueError si no existe."""
        contrato = self.dao.obtener_por_id(contrato_id)
        if not contrato:
            raise ValueError(f"El contrato con ID {contrato_id} no fue encontrado")
        return contrato

    def listar_contratos(self) -> list[ContratoModelo]:
        """Obtiene la lista completa de todos los contratos registrados."""
        return self.dao.obtener_todos()

    def cambiar_estado(
        self,
        contrato_id: UUID,
        nuevo_estado: EstadoContrato,
        id_transportista: UUID | None = None,
        id_camion: UUID | None = None,
        actor_id: UUID | None = None,
    ) -> ContratoModelo:
        """Solicita un cambio de estado evaluando las reglas de la Maquina de Estados
        y persiste los cambios aplicados.
        """
        contrato = self.obtener_contrato(contrato_id)
        estado_anterior = contrato.estado

        contrato_actualizado = MaquinaEstadosContrato.cambiar_estado(
            contrato_data=contrato,
            nuevo_estado=nuevo_estado,
            id_transportista=id_transportista,
            id_camion=id_camion,
        )

        self.dao.actualizar(contrato_id, contrato_actualizado)
        if self.auditoria_service:
            self.auditoria_service.registrar_evento(
                transporte_id=contrato_id,
                entidad=EntidadAuditable.CONTRATO,
                entidad_id=contrato_id,
                accion=AccionAuditoria.ESTADO_CONTRATO_CAMBIADO,
                actor_id=actor_id or contrato.id_empresa_generadora,
                datos=contrato_actualizado.model_dump(mode="json"),
                bases_aplicadas=ReglasNegocio.obtener_configuracion(),
                informacion_utilizada={
                    "estado_anterior": estado_anterior.value,
                    "estado_nuevo": nuevo_estado.value,
                    "id_transportista_solicitado": str(id_transportista) if id_transportista else None,
                    "id_camion_solicitado": str(id_camion) if id_camion else None,
                },
            )
        return contrato_actualizado


# Alias para retrocompatibilidad
ContratoService = ServicioContrato
