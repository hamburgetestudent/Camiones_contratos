"""
Modulo centralizado de inyeccion de dependencias y singletons para servicios y DAOs.
Evita acoplamiento cruzado y facilita sustitucion de adaptadores.
"""

from dao.contrato_dao import ContratoDAOMemoria
from dao.postulacion_dao import PostulacionDAOMemoria
from services.contrato_service import ServicioContrato
from services.subasta_service import ServicioSubasta

# Instancias compartidas a nivel de aplicacion
contrato_dao = ContratoDAOMemoria()
postulacion_dao = PostulacionDAOMemoria()

servicio_contrato = ServicioContrato(dao=contrato_dao)
servicio_subasta = ServicioSubasta(contrato_dao=contrato_dao, postulacion_dao=postulacion_dao)


def obt_servicio_contrato() -> ServicioContrato:
    """Retorna la instancia singleton del servicio de contratos."""
    return servicio_contrato


def obt_servicio_subasta() -> ServicioSubasta:
    """Retorna la instancia singleton del servicio de subastas."""
    return servicio_subasta


# Alias para retrocompatibilidad
get_contrato_service = obt_servicio_contrato
get_subasta_service = obt_servicio_subasta
obtener_servicio_contrato = obt_servicio_contrato
obtener_servicio_subasta = obt_servicio_subasta
contrato_service = servicio_contrato
subasta_service = servicio_subasta
