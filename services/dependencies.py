"""
Modulo centralizado de inyeccion de dependencias y singleton para servicios y DAOs.
Evita el acoplamiento cruzado entre los routers HTTP.
"""

from dao.contrato_dao import ContratoDAOInMemory
from dao.postulacion_dao import PostulacionDAOInMemory
from services.contrato_service import ContratoService
from services.subasta_service import SubastaService

# Instancias compartidas a nivel de aplicacion
contrato_dao = ContratoDAOInMemory()
postulacion_dao = PostulacionDAOInMemory()

contrato_service = ContratoService(dao=contrato_dao)
subasta_service = SubastaService(contrato_dao=contrato_dao, postulacion_dao=postulacion_dao)


def get_contrato_service() -> ContratoService:
    """Retorna la instancia singleton del servicio de contratos."""
    return contrato_service


def get_subasta_service() -> SubastaService:
    """Retorna la instancia singleton del servicio de subastas."""
    return subasta_service
