"""Acceso directo a la base de datos SQLite (conexion, esquema y datos semilla)."""

from database.conexion import (
    DEFAULT_DB_PATH,
    cargar_datos_semilla,
    inicializar_bd,
    obtener_conexion,
    transaccion_exclusiva,
)

__all__ = [
    "DEFAULT_DB_PATH",
    "cargar_datos_semilla",
    "inicializar_bd",
    "obtener_conexion",
    "transaccion_exclusiva",
]
