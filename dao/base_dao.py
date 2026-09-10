"""
Modulo base para el patron Data Access Object (DAO).
Define interfaces abstractas y clases base genericas de acceso a datos en espanol.
"""

from abc import ABC
import threading
from typing import Callable, Dict, Generic, List, Optional, TypeVar

E = TypeVar("E")  # Entidad
ID = TypeVar("ID")  # Identificador


class BaseDAO(ABC, Generic[E, ID]):
    """Interfaz abstracta generica para operaciones CRUD de persistencia."""

    def obt_por_id(self, entidad_id: ID) -> Optional[E]:
        """Obtiene una entidad por su identificador unico."""
        if hasattr(self, "get_id"):
            return self.get_id(entidad_id)
        return None

    def obt_todos(self) -> List[E]:
        """Retorna todas las entidades persistidas."""
        if hasattr(self, "get_all"):
            return self.get_all()
        return []

    def guardar(self, entidad: E) -> E:
        """Persiste una entidad nueva o actualizada."""
        if hasattr(self, "save"):
            return self.save(entidad)
        return entidad

    def actualizar(self, entidad_id: ID, entidad: E) -> Optional[E]:
        """Actualiza una entidad existente identificada por su ID."""
        if hasattr(self, "update"):
            return self.update(entidad_id, entidad)
        return None

    def eliminar(self, entidad_id: ID) -> bool:
        """Elimina una entidad por su ID. Retorna True si existia y fue eliminada."""
        if hasattr(self, "delete"):
            return self.delete(entidad_id)
        return False

    def existe(self, entidad_id: ID) -> bool:
        """Verifica la existencia de una entidad por su ID."""
        return self.obt_por_id(entidad_id) is not None

    get_id = obt_por_id
    get_all = obt_todos
    save = guardar
    update = actualizar
    delete = eliminar


class DAOMemoria(BaseDAO[E, ID], Generic[E, ID]):
    """
    Implementacion generica de almacenamiento en memoria thread-safe.
    Proporciona operaciones CRUD basicas sincronizadas mediante un cerrojo (RLock).
    """

    def __init__(self, extractor_id: Optional[Callable[[E], ID]] = None) -> None:
        self._almacenamiento: Dict[ID, E] = {}
        self._extractor_id: Callable[[E], ID] = extractor_id or (lambda entidad: getattr(entidad, "id"))
        self._lock = threading.RLock()

    def obt_por_id(self, entidad_id: ID) -> Optional[E]:
        """Recupera una entidad del almacenamiento en memoria por su ID."""
        with self._lock:
            return self._almacenamiento.get(entidad_id)

    def obt_todos(self) -> List[E]:
        """Retorna una lista con todas las entidades almacenadas."""
        with self._lock:
            return list(self._almacenamiento.values())

    def guardar(self, entidad: E) -> E:
        """Guarda o reemplaza una entidad en el almacenamiento en memoria."""
        entidad_id = self._extractor_id(entidad)
        with self._lock:
            self._almacenamiento[entidad_id] = entidad
        return entidad

    def actualizar(self, entidad_id: ID, entidad: E) -> Optional[E]:
        """Actualiza una entidad existente. Retorna None si no existe."""
        with self._lock:
            if entidad_id not in self._almacenamiento:
                return None
            self._almacenamiento[entidad_id] = entidad
            return entidad

    def eliminar(self, entidad_id: ID) -> bool:
        """Elimina una entidad si existe. Retorna True si fue eliminada, False de lo contrario."""
        with self._lock:
            if entidad_id in self._almacenamiento:
                del self._almacenamiento[entidad_id]
                return True
            return False

    def existe(self, entidad_id: ID) -> bool:
        """Retorna True si el ID existe en el almacenamiento, False en caso contrario."""
        with self._lock:
            return entidad_id in self._almacenamiento

    obt_todas_entidades = obt_todos
    obtener_todos = obt_todos
    obtener_por_id = obt_por_id
    save = guardar
    get_id = obt_por_id
    get_all = obt_todos
    update = actualizar
    delete = eliminar


BD_DAO = BaseDAO