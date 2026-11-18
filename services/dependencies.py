"""Modulo centralizado de inyeccion de dependencias y singletons para los servicios.

Los servicios acceden directamente a SQLite (ver ``database.conexion``); aqui solo
se crean las instancias compartidas que consumen los routers.
"""

from services.contrato_service import ServicioContrato
from services.subasta_service import ServicioSubasta

# Instancias compartidas a nivel de aplicacion (usan la base de datos por defecto)
servicio_contrato = ServicioContrato()
servicio_subasta = ServicioSubasta()


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
