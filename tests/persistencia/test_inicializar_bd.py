"""Tests unitarios de database.conexion: esquema, datos semilla, conexiones y transacciones."""

from __future__ import annotations

import sqlite3

from database.conexion import (
    cargar_datos_semilla,
    inicializar_bd,
    obtener_conexion,
    transaccion_exclusiva,
)
from tests.base import BaseTestCase

TABLAS_ESPERADAS = {
    "usuarios",
    "dadores_carga",
    "documentos_transportista",
    "contratos",
    "postulaciones",
}


def _tablas(ruta) -> set[str]:
    conn = sqlite3.connect(str(ruta))
    try:
        filas = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        return {fila[0] for fila in filas.fetchall()}
    finally:
        conn.close()


def _contar_usuarios(ruta) -> int:
    conn = sqlite3.connect(str(ruta))
    try:
        return conn.execute("SELECT count(*) FROM usuarios").fetchone()[0]
    finally:
        conn.close()


class TestConexionYEsquema(BaseTestCase):
    """Pruebas dedicadas al esquema, la conexion y los datos semilla de SQLite."""

    def setUp(self) -> None:
        super().setUp()
        self.db_path = self.crear_directorio_temporal() / "nueva.db"

    def test_inicializar_bd_crea_todas_las_tablas(self) -> None:
        inicializar_bd(self.db_path, cargar_semilla=False)
        self.assertTrue(self.db_path.exists())
        self.assertTrue(TABLAS_ESPERADAS.issubset(_tablas(self.db_path)))

    def test_obtener_conexion_crea_el_esquema_en_una_base_nueva(self) -> None:
        # Sin llamar a inicializar_bd: la primera conexion aplica el esquema
        with obtener_conexion(self.db_path) as conn:
            conn.execute("SELECT count(*) FROM contratos").fetchone()
        self.assertTrue(TABLAS_ESPERADAS.issubset(_tablas(self.db_path)))

    def test_esquema_se_aplica_sobre_base_existente_sin_perder_datos(self) -> None:
        # Base "antigua": solo tiene la tabla usuarios con un registro
        conn = sqlite3.connect(str(self.db_path))
        conn.execute(
            """
            CREATE TABLE usuarios (
                id TEXT PRIMARY KEY, nombre TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE COLLATE NOCASE, rol TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                estado TEXT NOT NULL DEFAULT 'EN_REVISION',
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """
        )
        conn.execute(
            "INSERT INTO usuarios (id, nombre, email, rol, password_hash) "
            "VALUES ('u1', 'Previo', 'previo@test.cl', 'TRANSPORTISTA', 'h')"
        )
        conn.commit()
        conn.close()

        with obtener_conexion(self.db_path) as conn:
            nombre = conn.execute("SELECT nombre FROM usuarios").fetchone()["nombre"]

        self.assertEqual(nombre, "Previo")
        self.assertTrue(TABLAS_ESPERADAS.issubset(_tablas(self.db_path)))

    def test_cargar_datos_semilla_inserta_usuarios_predefinidos(self) -> None:
        inicializar_bd(self.db_path)
        # Al menos admin, transportista y dador semilla
        self.assertGreaterEqual(_contar_usuarios(self.db_path), 3)

    def test_cargar_datos_semilla_idempotente(self) -> None:
        inicializar_bd(self.db_path)
        total = _contar_usuarios(self.db_path)
        cargar_datos_semilla(self.db_path)  # segunda ejecucion: no duplica ni falla
        self.assertEqual(_contar_usuarios(self.db_path), total)

    def test_obtener_conexion_confirma_al_salir_sin_error(self) -> None:
        with obtener_conexion(self.db_path) as conn:
            conn.execute(
                "INSERT INTO usuarios (id, nombre, email, rol, password_hash) "
                "VALUES ('u1', 'A', 'a@test.cl', 'TRANSPORTISTA', 'h')"
            )
        self.assertEqual(_contar_usuarios(self.db_path), 1)

    def test_obtener_conexion_hace_rollback_ante_una_excepcion(self) -> None:
        with self.assertRaises(RuntimeError):
            with obtener_conexion(self.db_path) as conn:
                conn.execute(
                    "INSERT INTO usuarios (id, nombre, email, rol, password_hash) "
                    "VALUES ('u1', 'A', 'a@test.cl', 'TRANSPORTISTA', 'h')"
                )
                raise RuntimeError("fallo a mitad de la operacion")
        self.assertEqual(_contar_usuarios(self.db_path), 0)

    def test_transaccion_exclusiva_es_todo_o_nada(self) -> None:
        with self.assertRaises(sqlite3.IntegrityError):
            with transaccion_exclusiva(self.db_path) as conn:
                conn.execute(
                    "INSERT INTO usuarios (id, nombre, email, rol, password_hash) "
                    "VALUES ('u1', 'A', 'dup@test.cl', 'TRANSPORTISTA', 'h')"
                )
                # Email duplicado (UNIQUE, insensible a mayusculas) => falla y revierte u1
                conn.execute(
                    "INSERT INTO usuarios (id, nombre, email, rol, password_hash) "
                    "VALUES ('u2', 'B', 'DUP@test.cl', 'TRANSPORTISTA', 'h')"
                )
        self.assertEqual(_contar_usuarios(self.db_path), 0)
