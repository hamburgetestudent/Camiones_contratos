"""
Implementación en Memoria del DAO de Postulaciones.
"""

from typing import Dict, List, Optional
from uuid import UUID

from dao.base_dao import BD_DAO
from domain.postulacion import PostulacionModelo, EstadoPostulacion


class PostulacionDAOInMemory(BD_DAO[PostulacionModelo, UUID]):
    """Almacenamiento simulado en memoria para las postulaciones de subastas."""

    def __init__(self):
        self._storage: Dict[UUID, PostulacionModelo] = {}

    def get_id(self, entidad_id: UUID) -> Optional[PostulacionModelo]:
        """Obtiene una postulación por su UUID."""
        return self._storage.get(entidad_id)

    def get_all(self) -> List[PostulacionModelo]:
        """Retorna todas las postulaciones registradas."""
        return list(self._storage.values())

    def save(self, entidad: PostulacionModelo) -> PostulacionModelo:
        """Guarda una nueva postulación."""
        self._storage[entidad.id] = entidad
        return entidad

    def update(self, entidad_id: UUID, entidad: PostulacionModelo) -> Optional[PostulacionModelo]:
        """Actualiza una postulación existente."""
        if entidad_id in self._storage:
            self._storage[entidad_id] = entidad
            return entidad
        return None

    def delete(self, entidad_id: UUID) -> bool:
        """Elimina una postulación."""
        if entidad_id in self._storage:
            del self._storage[entidad_id]
            return True
        return False

    def get_by_contrato(self, contrato_id: UUID) -> List[PostulacionModelo]:
        """Obtiene todas las postulaciones asociadas a un contrato/carga."""
        return [p for p in self._storage.values() if p.carga_id == contrato_id]

    def get_by_transportista(self, transportista_id: UUID) -> List[PostulacionModelo]:
        """Obtiene todas las postulaciones enviadas por un transportista específico."""
        return [p for p in self._storage.values() if p.transportista_id == transportista_id]

    def rechazar_postulaciones(self, contrato_id: UUID, ganadora_id: UUID) -> List[PostulacionModelo]:
        """
        Marca todas las demás postulaciones de un contrato como RECHAZADA,
        salvo la postulación ganadora.
        """
        modificadas = []
        for post in self.get_by_contrato(contrato_id):
            if post.id != ganadora_id:
                post.estado = EstadoPostulacion.RECHAZADA
                self._storage[post.id] = post
                modificadas.append(post)
        return modificadas