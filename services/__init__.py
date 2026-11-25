"""Modulo de Servicios: Orquestacion de logica de negocio y persistencia.

Las instancias compartidas viven en ``core.dependencies``.
"""

from services.contrato_service import ContratoService, ServicioContrato
from services.subasta_service import ServicioSubasta, SubastaService

__all__ = [
    "ServicioContrato",
    "ContratoService",
    "ServicioSubasta",
    "SubastaService",
]
