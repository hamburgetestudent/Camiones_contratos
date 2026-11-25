"""DAO de revocación de sesiones JWT (tabla ``sesiones_cerradas`` en SQLite)."""

from __future__ import annotations

import sqlite3
from abc import ABC, abstractmethod

from dao.base_dao import DAOSQLite


class SesionDAO(ABC):
    """Contrato de persistencia para la lista de sesiones revocadas."""

    @abstractmethod
    def esta_revocada(self, conn: sqlite3.Connection, huella: str) -> bool:
        """Indica si la huella SHA-256 de un token ya fue revocada."""

    @abstractmethod
    def revocar_y_purgar(
        self, conn: sqlite3.Connection, huella: str, expira: int, ahora: int
    ) -> None:
        """Elimina huellas expiradas y registra una nueva huella revocada."""


class SesionDAOSQLite(DAOSQLite, SesionDAO):
    """Implementación SQLite del DAO de sesiones revocadas."""

    def esta_revocada(self, conn: sqlite3.Connection, huella: str) -> bool:
        fila = conn.execute(
            "SELECT 1 FROM sesiones_cerradas WHERE huella = ?",
            (huella,),
        ).fetchone()
        return fila is not None

    def revocar_y_purgar(
        self, conn: sqlite3.Connection, huella: str, expira: int, ahora: int
    ) -> None:
        conn.execute("DELETE FROM sesiones_cerradas WHERE expira < ?", (ahora,))
        conn.execute(
            "INSERT OR IGNORE INTO sesiones_cerradas (huella, expira) VALUES (?, ?)",
            (huella, expira),
        )
