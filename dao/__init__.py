"""Modulo DAO (Data Access Object) para abstraccion de almacenamiento de datos."""

from dao.base_dao import BaseDAO, DAOMemoria
from dao.contrato_dao import ContratoDAO, ContratoDAOMemoria
from dao.onboarding_dao import OnboardingDAO
from dao.postulacion_dao import PostulacionDAO, PostulacionDAOMemoria
from dao.usuario_dao import UsuarioDAO

__all__ = [
    "BaseDAO",
    "DAOMemoria",
    "ContratoDAO",
    "ContratoDAOMemoria",
    "OnboardingDAO",
    "PostulacionDAO",
    "PostulacionDAOMemoria",
    "UsuarioDAO",
]
