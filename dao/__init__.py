"""Modulo DAO (Data Access Object) para abstraccion de almacenamiento de datos."""

from dao.base_dao import BaseDAO, DAOMemoria
from dao.contrato_dao import ContratoDAO, ContratoDAOMemoria
from dao.onboarding_dao import (
    DadorCargaDAOInMemory,
    DadorCargaDAOSQLite,
    DocumentoDAOInMemory,
    DocumentoDAOSQLite,
)
from dao.postulacion_dao import PostulacionDAO, PostulacionDAOMemoria
from dao.sqlite_db import DEFAULT_DB_PATH, inicializar_bd, obtener_conexion
from dao.usuario_dao import UsuarioDAO, UsuarioDAOMemoria, UsuarioDAOSQLite

# Alias para compatibilidad
OnboardingDAO = DocumentoDAOInMemory

__all__ = [
    "DEFAULT_DB_PATH",
    "BaseDAO",
    "ContratoDAO",
    "ContratoDAOMemoria",
    "DAOMemoria",
    "DadorCargaDAOInMemory",
    "DadorCargaDAOSQLite",
    "DocumentoDAOInMemory",
    "DocumentoDAOSQLite",
    "OnboardingDAO",
    "PostulacionDAO",
    "PostulacionDAOMemoria",
    "UsuarioDAO",
    "UsuarioDAOMemoria",
    "UsuarioDAOSQLite",
    "inicializar_bd",
    "obtener_conexion",
]
