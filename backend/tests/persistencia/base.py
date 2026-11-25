"""Base DRY para pruebas de persistencia directa sobre SQLite."""

from __future__ import annotations

import sqlite3
from typing import Any

from tests.base import BaseTestCase


class BaseTestPersistencia(BaseTestCase):
    """Clase base DRY para pruebas de persistencia.

    Hereda de tests.base.BaseTestCase y entrega una base SQLite temporal ya
    inicializada (sin datos semilla), que ademas queda como ruta por defecto.
    """

    def setUp(self) -> None:
        super().setUp()
        self.db_path = self.preparar_bd_aislada()

    def consultar(
        self, sql: str, parametros: tuple[Any, ...] = ()
    ) -> list[sqlite3.Row]:
        """Ejecuta un SELECT crudo sobre la base temporal (verifica lo realmente guardado)."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            return conn.execute(sql, parametros).fetchall()
        finally:
            conn.close()
