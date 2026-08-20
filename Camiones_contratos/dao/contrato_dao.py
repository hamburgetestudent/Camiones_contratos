"""
Implementacion del DAO de Contratos en Memoria.
Proporciona persistencia temporal aislada del resto de la aplicacion.
"""

from typing import Dict, List, Optional
from uuid import UUID

from dao.base_dao import BD_DAO
from Camiones_contratos.domain.modelos import ContratoModelo


class ContratoDAOInMemory(BD_DAO[ContratoModelo, UUID]):
    """
    Implementación concreta de almacenamiento en memoria para Contratos.
    """

    def __init__(self):
        self._storage: Dict[UUID, ContratoModelo] = {}

    def get_id(self, entidad_id: UUID) -> Optional[ContratoModelo]:
        """Obtiene un contrato por su UUID."""
        return self._storage.get(entidad_id)

    def get_all(self) -> List[ContratoModelo]:
        """Retorna todos los contratos registrados."""
        return list(self._storage.values())

    def save(self, entidad: ContratoModelo) -> ContratoModelo:
        """Guarda o inserta un contrato."""
        self._storage[entidad.id] = entidad
        return entidad

    def update(self, entidad_id: UUID, entidad: ContratoModelo) -> Optional[ContratoModelo]:
        """Actualiza un contrato existente."""
        if entidad_id in self._storage:
            self._storage[entidad_id] = entidad
            return entidad
        return None

    def delete(self, entidad_id: UUID) -> bool:
        """Elimina un contrato si existe."""
        if entidad_id in self._storage:
            del self._storage[entidad_id]
            return True
        return False