"""Interfaz base del patron DAO (Data Access Object) sobre SQLite.

Un DAO encapsula todo el SQL de una entidad y expone operaciones en terminos del
modelo de dominio. Los servicios dependen de la interfaz abstracta y reciben la
implementacion concreta por inyeccion (ver ``core/dependencies.py``).

Las operaciones reciben una conexion abierta. Asi un servicio puede combinar
varios DAO (p. ej. contratos y postulaciones) dentro de una misma transaccion
y garantizar la postcondicion "todo o nada".
"""

from __future__ import annotations

import sqlite3
from abc import ABC, abstractmethod
from contextlib import AbstractContextManager
from pathlib import Path
from typing import Generic, TypeVar

from database.conexion import obtener_conexion, transaccion_exclusiva

E = TypeVar("E")  # Entidad de dominio
ID = TypeVar("ID")  # Tipo del identificador


class BaseDAO(ABC, Generic[E, ID]):  # noqa: UP046
    """Operaciones CRUD minimas que todo DAO persistente debe ofrecer."""

    @abstractmethod
    def obtener_por_id(self, conn: sqlite3.Connection, entidad_id: ID) -> E | None:
        """Retorna la entidad con ese ID, o None si no existe."""

    @abstractmethod
    def obtener_todos(self, conn: sqlite3.Connection) -> list[E]:
        """Retorna todas las entidades en orden de insercion."""

    @abstractmethod
    def guardar(self, conn: sqlite3.Connection, entidad: E) -> E:
        """Inserta la entidad o, si su ID ya existe, reemplaza todos sus campos."""

    @abstractmethod
    def actualizar(
        self, conn: sqlite3.Connection, entidad_id: ID, entidad: E
    ) -> E | None:
        """Actualiza una entidad existente. Retorna None si el ID no existe."""


class DAOSQLite:
    """Mixin que resuelve la base de datos y abre conexiones/transacciones.

    ``db_path=None`` usa ``DEFAULT_DB_PATH`` evaluado en cada llamada, de modo que
    la ruta puede redirigirse (p. ej. en pruebas) sin reconstruir el DAO.
    """

    def __init__(self, db_path: str | Path | None = None) -> None:
        self._db_path = db_path

    @property
    def db_path(self) -> str | Path | None:
        """Ruta del archivo SQLite configurada (None = base por defecto)."""
        return self._db_path

    def conexion(self) -> AbstractContextManager[sqlite3.Connection]:
        """Abre una conexion con commit/rollback automatico."""
        return obtener_conexion(self._db_path)

    def transaccion(self) -> AbstractContextManager[sqlite3.Connection]:
        """Abre una transaccion exclusiva (lectura + escritura atomicas)."""
        return transaccion_exclusiva(self._db_path)
