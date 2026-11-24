"""Modulo centralizado de inyeccion de dependencias y singletons para los servicios.

Aqui se construyen los almacenes persistentes (DAO sobre SQLite) y se inyectan
en los servicios. Contratos y subastas comparten los mismos DAO, de modo que
todo el estado de negocio sobrevive a un reinicio de la aplicacion.
"""

from dao.contrato_dao import ContratoDAO, ContratoDAOSQLite
from dao.postulacion_dao import PostulacionDAO, PostulacionDAOSQLite
from services.contrato_service import ServicioContrato
from services.subasta_service import ServicioSubasta

# Almacenes persistentes compartidos (usan la base de datos por defecto)
contrato_dao: ContratoDAO = ContratoDAOSQLite()
postulacion_dao: PostulacionDAO = PostulacionDAOSQLite()

# Instancias compartidas a nivel de aplicacion
servicio_contrato = ServicioContrato(dao=contrato_dao)
servicio_subasta = ServicioSubasta(
    contrato_dao=contrato_dao, postulacion_dao=postulacion_dao
)


def obtener_contrato_dao() -> ContratoDAO:
    """Retorna el DAO persistente de contratos."""
    return contrato_dao


def obtener_postulacion_dao() -> PostulacionDAO:
    """Retorna el DAO persistente de postulaciones."""
    return postulacion_dao


def obtener_servicio_contrato() -> ServicioContrato:
    """Retorna la instancia singleton del servicio de contratos."""
    return servicio_contrato


def obtener_servicio_subasta() -> ServicioSubasta:
    """Retorna la instancia singleton del servicio de subastas."""
    return servicio_subasta


# Alias para retrocompatibilidad
obt_servicio_contrato = obtener_servicio_contrato
obt_servicio_subasta = obtener_servicio_subasta
get_contrato_service = obtener_servicio_contrato
get_subasta_service = obtener_servicio_subasta
contrato_service = servicio_contrato
subasta_service = servicio_subasta
