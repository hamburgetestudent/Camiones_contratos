"""Capa DAO (Data Access Object): el SQL de las entidades de negocio vive aqui."""

from dao.admin_dao import AdminDAO, AdminDAOSQLite
from dao.base_dao import BaseDAO, DAOSQLite
from dao.contrato_dao import ContratoDAO, ContratoDAOSQLite
from dao.onboarding_dao import (
    DadorCargaDAO,
    DadorCargaDAOSQLite,
    DocumentoDAO,
    DocumentoDAOSQLite,
)
from dao.postulacion_dao import PostulacionDAO, PostulacionDAOSQLite
from dao.sesion_dao import SesionDAO, SesionDAOSQLite
from dao.usuario_dao import UsuarioDAO, UsuarioDAOSQLite

__all__ = [
    "AdminDAO",
    "AdminDAOSQLite",
    "BaseDAO",
    "ContratoDAO",
    "ContratoDAOSQLite",
    "DAOSQLite",
    "DadorCargaDAO",
    "DadorCargaDAOSQLite",
    "DocumentoDAO",
    "DocumentoDAOSQLite",
    "PostulacionDAO",
    "PostulacionDAOSQLite",
    "SesionDAO",
    "SesionDAOSQLite",
    "UsuarioDAO",
    "UsuarioDAOSQLite",
]
