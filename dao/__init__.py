"""Modulo DAO (Data Access Object) para abstraccion de almacenamiento de datos."""

from dao.base_dao import BaseDAO, DAOMemoria
from dao.contrato_dao import ContratoDAO, ContratoDAOMemoria
from dao.postulacion_dao import PostulacionDAO, PostulacionDAOMemoria

__all__ = [
    "BaseDAO",
    "DAOMemoria",
    "ContratoDAO",
    "ContratoDAOMemoria",
    "PostulacionDAO",
    "PostulacionDAOMemoria",
]
