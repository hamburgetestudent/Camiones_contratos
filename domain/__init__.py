"""
Modulo de Dominio: Reglas de negocio, maquinas de estado y modelos de datos.
Centraliza las entidades y la logica pura de la aplicacion.
"""

from domain.maquina_estados import (
    EstadoContrato,
    MaquinaEstadosBase,
    MaquinaEstadosContrato,
)
from domain.modelos import (
    ContratoBase,
    ContratoCrear,
    ContratoModelo,
    Moneda,
    TipoCarga,
    limpiar_texto,
)
from domain.postulacion import (
    TARIFA_MINIMA_POSTULACION_CLP,
    EstadoPostulacion,
    MaquinaEstadoPostulacion,
    PostulacionBase,
    PostulacionCrear,
    PostulacionModelo,
)
from domain.reglas import ReglasNegocio

__all__ = [
    # Reglas
    "ReglasNegocio",
    # Maquinas de estado
    "MaquinaEstadosBase",
    "EstadoContrato",
    "MaquinaEstadosContrato",
    "EstadoPostulacion",
    "MaquinaEstadoPostulacion",
    # Modelos Contrato
    "TipoCarga",
    "Moneda",
    "ContratoBase",
    "ContratoCrear",
    "ContratoModelo",
    "limpiar_texto",
    # Modelos Postulacion
    "TARIFA_MINIMA_POSTULACION_CLP",
    "PostulacionBase",
    "PostulacionCrear",
    "PostulacionModelo",
]
