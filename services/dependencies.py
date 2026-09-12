"""Modulo centralizado de inyeccion de dependencias y singletons para servicios y DAOs.

Evita acoplamiento cruzado y facilita sustitucion de adaptadores.
"""

import os

from dao.auditoria_dao import AuditoriaDAOSQLite
from dao.contrato_dao import ContratoDAOMemoria
from dao.postulacion_dao import PostulacionDAOMemoria
from services.auditoria_service import ServicioAuditoria
from services.contrato_service import ServicioContrato
from services.subasta_service import ServicioSubasta

# Instancias compartidas a nivel de aplicacion
auditoria_dao = AuditoriaDAOSQLite(os.getenv("AUDIT_DB_PATH", "data/auditoria.sqlite3"))
servicio_auditoria = ServicioAuditoria(dao=auditoria_dao)
contrato_dao = ContratoDAOMemoria()
postulacion_dao = PostulacionDAOMemoria()

servicio_contrato = ServicioContrato(dao=contrato_dao, auditoria_service=servicio_auditoria)
servicio_subasta = ServicioSubasta(
    contrato_dao=contrato_dao,
    postulacion_dao=postulacion_dao,
    auditoria_service=servicio_auditoria,
)


def obtener_servicio_auditoria() -> ServicioAuditoria:
    """Retorna la instancia singleton del servicio de auditoria."""
    return servicio_auditoria


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
get_auditoria_service = obtener_servicio_auditoria
contrato_service = servicio_contrato
subasta_service = servicio_subasta
auditoria_service = servicio_auditoria
