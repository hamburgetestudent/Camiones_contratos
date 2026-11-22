"""Modulo de Servicios: Orquestacion de logica de negocio y persistencia."""

from services.contrato_service import ContratoService, ServicioContrato
from services.dependencies import (
    contrato_service,
    get_contrato_service,
    get_subasta_service,
    obt_servicio_contrato,
    obt_servicio_subasta,
    servicio_contrato,
    servicio_subasta,
    subasta_service,
)
from services.subasta_service import ServicioSubasta, SubastaService

__all__ = [
    "ServicioContrato",
    "ContratoService",
    "ServicioSubasta",
    "SubastaService",
    "servicio_contrato",
    "servicio_subasta",
    "contrato_service",
    "subasta_service",
    "obt_servicio_contrato",
    "obt_servicio_subasta",
    "get_contrato_service",
    "get_subasta_service",
]
