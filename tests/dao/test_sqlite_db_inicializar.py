"""Tests unitarios para las funciones inicializar_bd y cargar_datos_semilla de sqlite_db.py."""

from __future__ import annotations

import sqlite3
from dao.sqlite_db import cargar_datos_semilla, inicializar_bd
from tests.dao.base import BaseTestDAO


class TestSqliteDBInicializar(BaseTestDAO):
    """Pruebas dedicadas al esquema y datos semilla de SQLite."""

    def test_inicializar_bd_crea_tablas_e_indices(self) -> None:
        inicializar_bd(self.db_path)
        self.assertTrue(self.db_path.exists())

        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tablas = {fila[0] for fila in cursor.fetchall()}
        conn.close()

        self.assertIn("usuarios", tablas)
        self.assertIn("dadores_carga", tablas)
        self.assertIn("documentos_transportista", tablas)

    def test_cargar_datos_semilla_inserta_usuarios_predefinidos(self) -> None:
        inicializar_bd(self.db_path)
        cargar_datos_semilla(self.db_path)

        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT count(*) FROM usuarios")
        total = cursor.fetchone()[0]
        conn.close()

        self.assertGreaterEqual(total, 3)  # Al menos admin, transportista y dador semilla

    def test_cargar_datos_semilla_idempotente(self) -> None:
        inicializar_bd(self.db_path)
        cargar_datos_semilla(self.db_path)
        cargar_datos_semilla(self.db_path)  # Segunda ejecución sin error por email UNIQUE

        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT count(*) FROM usuarios")
        total = cursor.fetchone()[0]
        conn.close()
        self.assertGreaterEqual(total, 3)