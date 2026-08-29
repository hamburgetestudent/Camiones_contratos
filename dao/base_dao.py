"""
Modulo base para el patron Data Access Object (DAO).
Define interfaces abstractas y clases base genericas de acceso a datos en espanol.
"""

from abc import ABC, abstractmethod
from typing import Callable, Dict, Generic, List, Optional, TypeVar

E = TypeVar("E")  # Entidad
ID = TypeVar("ID")  # Identificador


class BaseDAO(ABC, Generic[E, ID]):
    """Interfaz abstracta generica para operaciones CRUD de persistencia."""

    @abstractmethod
    def obtener_por_id(self, entidad_id: ID) -> Optional[E]:
        """Obtiene una entidad por su identificador unico."""
        pass

    @abstractmethod
    def obtener_todos(self) -> List[E]:
        """Retorna todas las entidades persistidas."""
        pass

    @abstractmethod
    def guardar(self, entidad: E) -> E:
        """Persiste una entidad nueva o actualizada."""
        pass

    @abstractmethod
    def actualizar(self, entidad_id: ID, entidad: E) -> Optional[E]:
        """Actualiza una entidad existente identificada por su ID."""
        pass

    @abstractmethod
    def eliminar(self, entidad_id: ID) -> bool:
        """Elimina una entidad por su ID. Retorna True si existia y fue eliminada."""
        pass

    @abstractmethod
    def existe(self, entidad_id: ID) -> bool:
        """Verifica la existencia de una entidad por su ID."""
        pass

    # Alias para compatibilidad hacia atras
    def get_by_id(self, entity_id: ID) -> Optional[E]:
        return self.obtener_por_id(entity_id)

    def get_id(self, entity_id: ID) -> Optional[E]:
        return self.obtener_por_id(entity_id)

    def get_all(self) -> List[E]:
        return self.obtener_todos()

    def save(self, entity: E) -> E:
        return self.guardar(entity)

    def update(self, entity_id: ID, entity: E) -> Optional[E]:
        return self.actualizar(entity_id, entity)

    def delete(self, entity_id: ID) -> bool:
        return self.eliminar(entity_id)

    def exists(self, entity_id: ID) -> bool:
        return self.existe(entity_id)


# Alias para retrocompatibilidad
BD_DAO = BaseDAO


class DAOMemoria(BaseDAO[E, ID], Generic[E, ID]):
    """
    Implementacion generica de almacenamiento en memoria.
    Proporciona operaciones CRUD basicas sobre un diccionario indexado por ID.
    """

    def __init__(self, extractor_id: Optional[Callable[[E], ID]] = None) -> None:
        self._almacenamiento: Dict[ID, E] = {}
        self._extractor_id: Callable[[E], ID] = extractor_id or (lambda entidad: getattr(entidad, "id"))

    @property
    def _storage(self) -> Dict[ID, E]:
        """Propiedad de compatibilidad con codigo legado."""
        return self._almacenamiento

    def obtener_por_id(self, entidad_id: ID) -> Optional[E]:
        """Recupera una entidad del almacenamiento en memoria por su ID."""
        return self._almacenamiento.get(entidad_id)

    def obtener_todos(self) -> List[E]:
        """Retorna una lista con todas las entidades almacenadas."""
        return list(self._almacenamiento.values())

    def guardar(self, entidad: E) -> E:
        """Guarda o reemplaza una entidad en el almacenamiento en memoria."""
        entidad_id = self._extractor_id(entidad)
        self._almacenamiento[entidad_id] = entidad
        return entidad

    def actualizar(self, entidad_id: ID, entidad: E) -> Optional[E]:
        """Actualiza una entidad existente. Retorna None si no existe."""
        if entidad_id not in self._almacenamiento:
            return None
        self._almacenamiento[entidad_id] = entidad
        return entidad

    def eliminar(self, entidad_id: ID) -> bool:
        """Elimina una entidad si existe. Retorna True si fue eliminada, False de lo contrario."""
        if entidad_id in self._almacenamiento:
            del self._almacenamiento[entidad_id]
            return True
        return False

    def existe(self, entidad_id: ID) -> bool:
        """Retorna True si el ID existe en el almacenamiento, False en caso contrario."""
        return entidad_id in self._almacenamiento


# Alias para retrocompatibilidad
InMemoryDAO = DAOMemoria