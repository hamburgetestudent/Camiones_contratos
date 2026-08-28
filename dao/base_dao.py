"""
Interfaz Abstracta con el Patron: Data Access Object (DAO).
Permite abstraer el origen de datos (En Memoria, JSON, SQLite, PostgreSQL).
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional

E = TypeVar("E") # Entidad
ID = TypeVar("ID")


class BD_DAO(ABC, Generic[E, ID]):
    """Interfaz abstracta genérica para operaciones crudas."""

    # =======================
    # 1. Recibir informacion
    # =======================

    @abstractmethod
    def get_id(self, entidad_id: ID) -> Optional[E]:
        """Obtiene una entidad por su ID unico."""
        pass

    @abstractmethod
    def get_all(self) -> List[E]:
        """Obtiene el listado completo de entidades."""
        pass

    # =============================
    # 2. Modificacion de la entidad
    # =============================

    @abstractmethod
    def save(self, entidad: E) -> E:
        """Guarda o persiste una NUEVA entidad."""
        pass

    @abstractmethod
    def update(self, entidad_id: ID, entidad: E) -> Optional[E]:
        """Actualiza una entidad existente por su ID."""
        pass

    @abstractmethod
    def delete(self, entidad_id: ID) -> bool:
        """Elimina una entidad por su ID."""
        pass