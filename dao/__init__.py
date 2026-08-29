"""Modulo DAO (Data Access Object) para abstraccion de almacenamiento de datos."""

from dao.base_dao import BaseDAO, BD_DAO, InMemoryDAO
from dao.contrato_dao import ContratoDAO, ContratoDAOInMemory
from dao.postulacion_dao import PostulacionDAO, PostulacionDAOInMemory

__all__ = [
    "BaseDAO",
    "BD_DAO",
    "InMemoryDAO",
    "ContratoDAO",
    "ContratoDAOInMemory",
    "PostulacionDAO",
    "PostulacionDAOInMemory",
]
