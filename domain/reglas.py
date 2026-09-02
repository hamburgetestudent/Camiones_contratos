"""
Modulo de reglas de negocio globales y configuracion parametrizable.
Implementado con patron Singleton para asegurar un estado unico en memoria.
"""

from typing import Dict, Any, Optional


class ReglasNegocio:
    """
    Parametros globales de las monedas, IVA, tolerancias financieras
    y tiempos minimos de programacion.
    """
    _instancia = None

    IVA_PORCENTAJE: float = 0.19
    TOLERANCIA_MAX: float = 0.01
    ANTICIPACION_MIN_H: int = 2

    def __new__(cls):
        if cls._instancia is None:
            cls._instancia = super(ReglasNegocio, cls).__new__(cls)
        return cls._instancia

    @classmethod
    def obtener_configuracion(cls) -> Dict[str, Any]:
        """Retorna la configuracion actual como diccionario."""
        return {
            "iva_porcentaje": cls.IVA_PORCENTAJE,
            "tolerancia_max": cls.TOLERANCIA_MAX,
            "anticipacion_min_h": cls.ANTICIPACION_MIN_H,
        }

    @classmethod
    def actualizar_configuracion(
        cls,
        iva_porcentaje: Optional[float] = None,
        tolerancia_max: Optional[float] = None,
        anticipacion_min_h: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Actualiza los parametros globales validando los rangos permitidos.
        """
        if iva_porcentaje is not None:
            if not (0 <= iva_porcentaje <= 1):
                raise ValueError("El porcentaje del IVA debe estar entre 0 y 1 (ej: 0.19 para 19%)")
            cls.IVA_PORCENTAJE = iva_porcentaje

        if tolerancia_max is not None:
            if tolerancia_max < 0:
                raise ValueError("La tolerancia financiera no puede ser negativa")
            cls.TOLERANCIA_MAX = tolerancia_max

        if anticipacion_min_h is not None:
            if anticipacion_min_h < 0:
                raise ValueError("La anticipacion minima no puede ser negativa")
            cls.ANTICIPACION_MIN_H = anticipacion_min_h

        return cls.obtener_configuracion()
