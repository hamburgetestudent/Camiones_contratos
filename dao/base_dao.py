"""Modulo base para el patron Data Access Object (DAO).

Define interfaces abstractas y clases base genericas de acceso a datos en espanol.
"""

from __future__ import annotations

import threading
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Generic, TypeVar

E = TypeVar("E")  # Entidad
ID = TypeVar("ID")  # Identificador


class BaseDAO(ABC, Generic[E, ID]):  # noqa: UP046
    """Interfaz abstracta generica para operaciones CRUD de persistencia."""

    @abstractmethod
    def obtener_por_id(self, entidad_id: ID) -> E | None:
        """Obtiene una entidad por su identificador unico."""
        pass

    @abstractmethod
    def obtener_todos(self) -> list[E]:
        """Retorna todas las entidades persistidas."""
        pass

    @abstractmethod
    def guardar(self, entidad: E) -> E:
        """Persiste una entidad nueva o actualizada."""
        pass

    @abstractmethod
    def actualizar(self, entidad_id: ID, entidad: E) -> E | None:
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

    # Alias para retrocompatibilidad
    def obt_por_id(self, entidad_id: ID) -> E | None:
        """Alias para obtener_por_id."""
        return self.obtener_por_id(entidad_id)

    def obt_todos(self) -> list[E]:
        """Alias para obtener_todos."""
        return self.obtener_todos()

    def get_by_id(self, entidad_id: ID) -> E | None:
        """Alias en ingles para obtener_por_id."""
        return self.obtener_por_id(entidad_id)

    def get_id(self, entidad_id: ID) -> E | None:
        """Alias en ingles para obtener_por_id."""
        return self.obtener_por_id(entidad_id)

    def get_all(self) -> list[E]:
        """Alias en ingles para obtener_todos."""
        return self.obtener_todos()

    def save(self, entidad: E) -> E:
        """Alias en ingles para guardar."""
        return self.guardar(entidad)

    def update(self, entidad_id: ID, entidad: E) -> E | None:
        """Alias en ingles para actualizar."""
        return self.actualizar(entidad_id, entidad)

    def delete(self, entidad_id: ID) -> bool:
        """Alias en ingles para eliminar."""
        return self.eliminar(entidad_id)

    def exists(self, entidad_id: ID) -> bool:
        """Alias en ingles para existe."""
        return self.existe(entidad_id)


class DAOMemoria(BaseDAO[E, ID], Generic[E, ID]):  # noqa: UP046
    """Implementacion generica de almacenamiento en memoria thread-safe.

    Proporciona operaciones CRUD basicas sincronizadas mediante un cerrojo (RLock).
    """

    def __init__(self, extractor_id: Callable[[E], ID] | None = None) -> None:
        self._almacenamiento: dict[ID, E] = {}
        self._extractor_id: Callable[[E], ID] = extractor_id or (lambda entidad: getattr(entidad, "id"))
        self._lock = threading.RLock()

    def obtener_por_id(self, entidad_id: ID) -> E | None:
        """Recupera una entidad del almacenamiento en memoria por su ID."""
        with self._lock:
            return self._almacenamiento.get(entidad_id)

    def obtener_todos(self) -> list[E]:
        """Retorna una lista con todas las entidades almacenadas."""
        with self._lock:
            return list(self._almacenamiento.values())

    def guardar(self, entidad: E) -> E:
        """Guarda o reemplaza una entidad en el almacenamiento en memoria."""
        entidad_id = self._extractor_id(entidad)
        with self._lock:
            self._almacenamiento[entidad_id] = entidad
        return entidad

    def actualizar(self, entidad_id: ID, entidad: E) -> E | None:
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

    # Alias en DAOMemoria
    obt_por_id = obtener_por_id
    obt_todos = obtener_todos
    obt_todas_entidades = obtener_todos
    get_by_id = obtener_por_id
    get_id = obtener_por_id
    get_all = obtener_todos
    save = guardar
    update = actualizar
    delete = eliminar
    exists = existe


# Alias para retrocompatibilidad con importaciones previas
BD_DAO = BaseDAO
