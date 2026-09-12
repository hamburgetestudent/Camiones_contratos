"""Modulo DAO (Data Access Object) para abstraccion de almacenamiento de datos."""

from dao.auditoria_dao import AuditoriaDAO, AuditoriaDAOSQLite
from dao.base_dao import BaseDAO, DAOMemoria
from dao.contrato_dao import ContratoDAO, ContratoDAOMemoria
from dao.onboarding_dao import DadorCargaDAOInMemory, DocumentoDAOInMemory
from dao.postulacion_dao import PostulacionDAO, PostulacionDAOMemoria
from dao.usuario_dao import UsuarioDAO

__all__ = [
    "AuditoriaDAOSQLite",
    "AuditoriaDAO",
    "BaseDAO",
    "DAOMemoria",
    "ContratoDAO",
    "ContratoDAOMemoria",
    "DocumentoDAOInMemory",
    "DadorCargaDAOInMemory",
    "PostulacionDAO",
    "PostulacionDAOMemoria",
    "UsuarioDAO",
]
