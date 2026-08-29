"""Modulo DAO (Data Access Object) para abstraccion de almacenamiento de datos."""

from dao.base_dao import BaseDAO, BD_DAO, DAOMemoria, InMemoryDAO
from dao.contrato_dao import ContratoDAO, ContratoDAOMemoria, ContratoDAOInMemory
from dao.postulacion_dao import PostulacionDAO, PostulacionDAOMemoria, PostulacionDAOInMemory

__all__ = [
    "BaseDAO",
    "BD_DAO",
    "DAOMemoria",
    "InMemoryDAO",
    "ContratoDAO",
    "ContratoDAOMemoria",
    "ContratoDAOInMemory",
    "PostulacionDAO",
    "PostulacionDAOMemoria",
    "PostulacionDAOInMemory",
]
