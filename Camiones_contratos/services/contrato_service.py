"""
Servicio de Negocio para la gestion del ciclo de vida de los Contratos.
Orquesta los modelos de dominio, la maquina de estados y la capa DAO.
"""

from typing import List, Optional
from uuid import UUID

from dao.base_dao import BD_DAO
from Camiones_contratos.domain.modelos import ContratoCrear, ContratoModelo
from Camiones_contratos.domain.maquina_estados import EstadoContrato, MaquinaEstadosContrato


class ContratoService:
    """Servicio que encapsula los casos de uso principales de Contratos."""

    def __init__(self, dao: BD_DAO[ContratoModelo, UUID]):
        self.dao = dao

    def crear_contrato(self, datos: ContratoCrear) -> ContratoModelo:
        """Crea un nuevo contrato en estado BORRADOR y lo persiste via DAO."""
        nuevo_contrato = ContratoModelo(**datos.model_dump())
        return self.dao.save(nuevo_contrato)

    def obtener_contrato(self, contrato_id: UUID) -> ContratoModelo:
        """Recupera un contrato por su ID. Lanza ValueError si no existe."""
        contrato = self.dao.get_id(contrato_id)
        if not contrato:
            raise ValueError(f"El contrato con ID {contrato_id} no fue encontrado")
        return contrato

    def listar_contratos(self) -> List[ContratoModelo]:
        """Obtiene la lista completa de contratos."""
        return self.dao.get_all()

    def cambiar_estado(
        self,
        contrato_id: UUID,
        nuevo_estado: EstadoContrato,
        id_transportista: Optional[UUID] = None,
        id_camion: Optional[UUID] = None,
    ) -> ContratoModelo:
        """
        Solicita un cambio de estado evaluando las reglas de la Maquina de Estados
        y persiste los cambios.
        """
        contrato = self.obtener_contrato(contrato_id)

        contrato_actualizado = MaquinaEstadosContrato.cambiar_estado(
            contrato_data=contrato,
            nuevo_estado=nuevo_estado,
            id_transportista=id_transportista,
            id_camion=id_camion,
        )

        self.dao.update(contrato_id, contrato_actualizado)
        return contrato_actualizado