"""
Capa de acceso a datos (DAO) para la entidad Postulacion en espanol.
"""

from abc import abstractmethod
from typing import List
from uuid import UUID

from dao.base_dao import BaseDAO, DAOMemoria
from domain.postulacion import EstadoPostulacion, PostulacionModelo


class PostulacionDAO(BaseDAO[PostulacionModelo, UUID]):
    """Interfaz abstracta para operaciones de persistencia de postulaciones."""

    @abstractmethod
    def obtener_por_contrato(self, contrato_id: UUID) -> List[PostulacionModelo]:
        """Obtiene todas las postulaciones asociadas a un contrato o carga."""
        pass

    @abstractmethod
    def obtener_por_transportista(self, transportista_id: UUID) -> List[PostulacionModelo]:
        """Obtiene todas las postulaciones enviadas por un transportista especifico."""
        pass

    @abstractmethod
    def rechazar_postulaciones(self, contrato_id: UUID, ganadora_id: UUID) -> List[PostulacionModelo]:
        """Marca como RECHAZADA toda postulacion del contrato excepto la seleccionada."""
        pass

class PostulacionDAOMemoria(DAOMemoria[PostulacionModelo, UUID], PostulacionDAO):
    """Implementacion en memoria thread-safe de persistencia para PostulacionModelo."""

    def obtener_por_contrato(self, contrato_id: UUID) -> List[PostulacionModelo]:
        """Obtiene todas las postulaciones asociadas a un contrato o carga."""
        with self._lock:
            return [
                postulacion for postulacion in self._almacenamiento.values()
                if postulacion.carga_id == contrato_id
            ]

    def obtener_por_transportista(self, transportista_id: UUID) -> List[PostulacionModelo]:
        """Obtiene todas las postulaciones enviadas por un transportista especifico."""
        with self._lock:
            return [
                postulacion for postulacion in self._almacenamiento.values()
                if postulacion.transportista_id == transportista_id
            ]

    def rechazar_postulaciones(self, contrato_id: UUID, ganadora_id: UUID) -> List[PostulacionModelo]:
        """
        Marca todas las demas postulaciones de un contrato como RECHAZADA,
        salvo la postulacion ganadora de forma atomica.
        """
        with self._lock:
            modificadas: List[PostulacionModelo] = []
            for postulacion in self.obtener_por_contrato(contrato_id):
                if postulacion.id != ganadora_id and postulacion.estado != EstadoPostulacion.RECHAZADA:
                    postulacion.estado = EstadoPostulacion.RECHAZADA
                    self._almacenamiento[postulacion.id] = postulacion
                    modificadas.append(postulacion)
            return modificadas