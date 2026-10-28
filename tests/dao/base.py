"""Base DRY para pruebas de DAOs y SQLite."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from tests.base import BaseTestCase


class BaseTestDAO(BaseTestCase):
    """Clase base DRY para pruebas de persistencia.
    
    Hereda de tests.base.BaseTestCase y provee aislamiento
    completo de bases de datos SQLite en disco temporal.
    """

    def setUp(self) -> None:
        super().setUp()
        self.temp_dir = self.crear_directorio_temporal()
        self.db_path = self.temp_dir / "test_storage.db"

    def obtener_conexion_sqlite(self) -> sqlite3.Connection:
        """Abre conexión SQLite sobre la base temporal aislada."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

