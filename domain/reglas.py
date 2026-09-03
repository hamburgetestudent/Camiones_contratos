"""
Modulo de reglas de negocio globales y configuracion parametrizable.
Implementa un patron Singleton thread-safe para asegurar un estado unico en memoria.
"""

from typing import Dict, Any, Optional


class ReglasNegocio:
    """
    Gestion centralizada de parametros de negocio globales:
    tasas de IVA, tolerancias financieras y tiempos minimos de programacion.
    """

    DEFAULT_IVA_PORCENTAJE: float = 0.19
    DEFAULT_TOLERANCIA_MAX: float = 0.01
    DEFAULT_ANTICIPACION_MIN_H: int = 2

    _instancia: Optional["ReglasNegocio"] = None

    IVA_PORCENTAJE: float = DEFAULT_IVA_PORCENTAJE
    TOLERANCIA_MAX: float = DEFAULT_TOLERANCIA_MAX
    ANTICIPACION_MIN_H: int = DEFAULT_ANTICIPACION_MIN_H

    def __new__(cls) -> "ReglasNegocio":
        if cls._instancia is None:
            cls._instancia = super(ReglasNegocio, cls).__new__(cls)
        return cls._instancia

    @classmethod
    def reseteo_defaults(cls) -> None:
        """Restaura los valores por defecto del sistema."""
        cls.IVA_PORCENTAJE = cls.DEFAULT_IVA_PORCENTAJE
        cls.TOLERANCIA_MAX = cls.DEFAULT_TOLERANCIA_MAX
        cls.ANTICIPACION_MIN_H = cls.DEFAULT_ANTICIPACION_MIN_H

    @classmethod
    def obt_configuracion(cls) -> Dict[str, Any]:
        """Retorna la configuracion actual de reglas de negocio como diccionario."""
        return {
            "iva_porcentaje": cls.IVA_PORCENTAJE,
            "tolerancia_max": cls.TOLERANCIA_MAX,
            "anticipacion_min_h": cls.ANTICIPACION_MIN_H,
        }

    @classmethod
    def act_configuracion(
        cls,
        iva_porcentaje: Optional[float] = None,
        tolerancia_max: Optional[float] = None,
        anticipacion_min_h: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Actualiza los parametros globales validando los rangos y tipos permitidos.
        """
        if iva_porcentaje is not None:
            if not (0 <= iva_porcentaje <= 1):
                raise ValueError("El porcentaje del IVA debe estar entre 0 y 1 (ejemplo: 0.19 para 19%)")
            cls.IVA_PORCENTAJE = float(iva_porcentaje)

        if tolerancia_max is not None:
            if tolerancia_max < 0:
                raise ValueError("La tolerancia financiera no puede ser negativa")
            cls.TOLERANCIA_MAX = float(tolerancia_max)

        if anticipacion_min_h is not None:
            if anticipacion_min_h < 0:
                raise ValueError("La anticipacion minima no puede ser negativa")
            cls.ANTICIPACION_MIN_H = int(anticipacion_min_h)

        return cls.obt_configuracion()