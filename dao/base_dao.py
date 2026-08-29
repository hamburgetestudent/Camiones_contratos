"""
Modulo base para el patron Data Access Object (DAO).
Define interfaces abstractas y clases base genericas de acceso a datos.
"""

from abc import ABC, abstractmethod
from typing import Callable, Dict, Generic, List, Optional, TypeVar

E = TypeVar("E") # Entidad
ID = TypeVar("ID")


class BaseDAO(ABC, Generic[E, ID]):
    """Interfaz abstracta generica para operaciones CRUD de persistencia."""

    @abstractmethod
    def get_por_id(self, entidad_id: ID) -> Optional[E]:
        """Obtiene una entidad por su identificador unico."""
        pass

    def get_id(self, entidad_id: ID) -> Optional[E]:
        """Alias de compatibilidad hacia atras para get_por_id."""
        return self.get_por_id(entidad_id)

    @abstractmethod
    def get_todos(self) -> List[E]:
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
BD_DAO = BaseDAO


class InMemoryDAO(BaseDAO[E, ID], Generic[E, ID]):
    """
    Implementacion generica de almacenamiento en memoria.
    Proporciona operaciones CRUD basicas sobre un diccionario indexado por ID.
    """

    def __init__(self, id_getter: Optional[Callable[[E], ID]] = None) -> None:
        self._storage: Dict[ID, E] = {}
        self._id_getter: Callable[[E], ID] = id_getter or (lambda entidad: getattr(entidad, "id"))

    def get_by_id(self, entidad_id: ID) -> Optional[E]:
        """Recupera una entidad del almacenamiento en memoria por su ID."""
        return self._storage.get(entidad_id)

    def get_all(self) -> List[E]:
        """Retorna una lista con todas las entidades almacenadas."""
        return list(self._storage.values())

    def save(self, entidad: E) -> E:
        """Guarda o reemplaza una entidad en el almacenamiento en memoria."""
        entidad_id = self._id_getter(entidad)
        self._storage[entidad_id] = entidad
        return entidad

    def update(self, entidad_id: ID, entidad: E) -> Optional[E]:
        """Actualiza una entidad existente. Retorna None si no existe."""
        if entidad_id not in self._storage:
            return None
        self._storage[entidad_id] = entidad
        return entidad

    def delete(self, entidad_id: ID) -> bool:
        """Elimina una entidad si existe. Retorna True si fue eliminada, False de lo contrario."""
        if entidad_id in self._storage:
            del self._storage[entidad_id]
            return True
        return False

    def exists(self, entidad_id: ID) -> bool:
        """Retorna True si el ID existe en el almacenamiento, False en caso contrario."""
        return entidad_id in self._storage