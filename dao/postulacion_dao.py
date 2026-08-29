"""
Capa de acceso a datos (DAO) para la entidad Postulacion.
"""

from abc import abstractmethod
from typing import List
from uuid import UUID

from dao.base_dao import BaseDAO, InMemoryDAO
from domain.postulacion import EstadoPostulacion, PostulacionModelo


class PostulacionDAO(BaseDAO[PostulacionModelo, UUID]):
    """Interfaz abstracta para operaciones de persistencia de postulaciones."""

    @abstractmethod
    def get_por_contrato(self, contrato_id: UUID) -> List[PostulacionModelo]:
        """Obtiene todas las postulaciones asociadas a un contrato o carga."""
        pass

    @abstractmethod
    def get_by_transportista(self, transportista_id: UUID) -> List[PostulacionModelo]:
        """Obtiene todas las postulaciones enviadas por un transportista especifico."""
        pass

    @abstractmethod
    def rechazar_postulaciones(self, contrato_id: UUID, ganadora_id: UUID) -> List[PostulacionModelo]:
        """Marca como RECHAZADA toda postulacion del contrato excepto la seleccionada."""
        pass


class PostulacionDAOInMemory(InMemoryDAO[PostulacionModelo, UUID], PostulacionDAO):
    """Implementacion en memoria de persistencia para PostulacionModelo."""

    def get_por_contrato(self, contrato_id: UUID) -> List[PostulacionModelo]:
        """Obtiene todas las postulaciones asociadas a un contrato o carga."""
        return [
            postulacion for postulacion in self._storage.values()
            if postulacion.carga_id == contrato_id
        ]

    def get_by_transportista(self, transportista_id: UUID) -> List[PostulacionModelo]:
        """Obtiene todas las postulaciones enviadas por un transportista especifico."""
        return [
            postulacion for postulacion in self._storage.values()
            if postulacion.transportista_id == transportista_id
        ]

    def rechazar_postulaciones(self, contrato_id: UUID, ganadora_id: UUID) -> List[PostulacionModelo]:
        """
        Marca todas las demas postulaciones de un contrato como RECHAZADA,
        salvo la postulacion ganadora.
        """
        modificadas: List[PostulacionModelo] = []
        for postulacion in self.get_por_contrato(contrato_id):
            if postulacion.id != ganadora_id and postulacion.estado != EstadoPostulacion.RECHAZADA:
                postulacion.estado = EstadoPostulacion.RECHAZADA
                self._storage[postulacion.id] = postulacion
                modificadas.append(postulacion)
        return modificadas