"""
Capa de acceso a datos (DAO) para la entidad Contrato.
"""

from uuid import UUID

from dao.base_dao import BaseDAO, InMemoryDAO
from domain.modelos import ContratoModelo


class ContratoDAO(BaseDAO[ContratoModelo, UUID]):
    """Interfaz abstracta para operaciones de persistencia de contratos."""
    pass


class ContratoDAOInMemory(InMemoryDAO[ContratoModelo, UUID], ContratoDAO):
    """Implementacion en memoria de persistencia para ContratoModelo."""
    pass