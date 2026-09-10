"""Modelos de dominio y esquemas de validacion Pydantic para Contratos de Camiones.

Refactorizados con validaciones modulares y desacoplados para mayor robustez y escalabilidad.
"""

import re
from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import Annotated
from uuid import UUID, uuid4

try:
    from enum import StrEnum
except ImportError:
    from enum import Enum

    class StrEnum(str, Enum):  # noqa: UP042
        pass


from pydantic import AwareDatetime, BaseModel, BeforeValidator, ConfigDict, Field, model_validator

from domain.maquina_estados import EstadoContrato
from domain.reglas import ReglasNegocio

# Numeros ONU, representan el nivel de peligrosidad de carga
ONU_REGEX = re.compile(r"^(UN)?\d{4}$", re.IGNORECASE)

TOLERANCIA_IVA_CLP: float = 5.0
MIN_LONGITUD_EMBALAJE: int = 10


def limpiar_texto(valor: str) -> str:
    """Remueve espacios superfluos y normaliza a mayusculas."""
    if isinstance(valor, str):
        return " ".join(valor.strip().split()).upper()
    return valor


TextoNormalizado = Annotated[str, BeforeValidator(limpiar_texto)]


class TipoCarga(StrEnum):
    """Clasificacion de tipos de carga para transporte terrestre."""

    GENERAL = "GENERAL"
    REFRIGERADA = "REFRIGERADA"
    PELIGROSA = "PELIGROSA"
    FRAGIL = "FRAGIL"
    GRANEL_LIQUIDO = "GRANEL_LIQUIDO"
    GRANEL_SOLIDO = "GRANEL_SOLIDO"
    PERECEDERA = "PERECEDERA"
    SOBREDIMENSIONADA = "SOBREDIMENSIONADA"
    VIVA = "VIVA"
    VALORES = "VALORES"
    VEHICULAR = "VEHICULAR"


class Moneda(StrEnum):
    """Monedas admitidas para valorizacion de contratos."""

    CLP = "CLP"
    UF = "UF"
    UTM = "UTM"
    USD = "USD"
    EUR = "EUR"
    CNY = "CNY"
    BRL = "BRL"


class ContratoBase(BaseModel):
    """Esquema base con todas las especificaciones y reglas de validacion de un contrato."""

    id_empresa_generadora: UUID = Field(..., description="ID unico de la empresa generadora de carga")
    origen: TextoNormalizado = Field(..., min_length=3, description="Direccion o comuna de origen")
    destino: TextoNormalizado = Field(..., min_length=3, description="Direccion o comuna de destino")

    f_estimada_salida: AwareDatetime = Field(..., description="Fecha y hora estimada de salida")
    f_estimada_llegada: AwareDatetime = Field(..., description="Fecha y hora estimada de llegada")
    f_cierre_postulaciones: AwareDatetime = Field(..., description="Fecha y hora limite de postulacion")

    input_camionKG: float = Field(..., gt=0, description="Capacidad maxima del camion en KG")  # noqa: N815
    tipo_carga: TipoCarga = Field(..., description="Tipo de carga transportada")
    peso_total: float = Field(..., gt=0, description="Peso total de la carga en KG")
    volumen_m3: float | None = Field(None, gt=0, description="Volumen estimado en metros cubicos")
    distancia_km: float | None = Field(default=None, ge=0, description="Distancia estimada de la ruta en kilometros")

    requiere_termo: bool = Field(default=False, description="Indica si requiere equipo de refrigeracion/termo")
    numero_onu: str | None = Field(default=None, description="Codigo ONU de 4 digitos para carga peligrosa")
    req_embalaje: str | None = Field(
        default=None, min_length=MIN_LONGITUD_EMBALAJE, description="Instrucciones detalladas de embalaje"
    )
    req_blindaje: bool = Field(default=False, description="Indica si requiere transporte blindado")

    moneda: Moneda = Field(default=Moneda.CLP, description="Moneda de pago del contrato")
    monto_neto: float = Field(..., gt=0, description="Monto Neto del contrato")
    monto_iva: float = Field(..., ge=0, description="Monto del IVA")
    monto_total: float = Field(..., gt=0, description="Monto Total (Neto + IVA)")

    model_config = ConfigDict(str_strip_whitespace=True)

    def _validar_fechas(self) -> None:
        ahora = datetime.now(UTC)
        limite_salida = ahora + timedelta(hours=ReglasNegocio.ANTICIPACION_MIN_H)

        if self.f_estimada_salida <= limite_salida:
            raise ValueError(
                "La fecha estimada de salida debe programarse con al menos "
                f"{ReglasNegocio.ANTICIPACION_MIN_H} horas de anticipacion"
            )

        if self.f_estimada_llegada <= self.f_estimada_salida:
            raise ValueError("La fecha estimada de llegada debe ser posterior a la fecha de salida")

        if self.f_cierre_postulaciones > self.f_estimada_salida:
            raise ValueError("El cierre de postulaciones no puede ser posterior a la fecha de salida")

    def _validar_carga_y_capacidad(self) -> None:
        if self.origen == self.destino:
            raise ValueError("El origen y destino no pueden ser identicos")

        if self.peso_total > self.input_camionKG:
            exceso = self.peso_total - self.input_camionKG
            raise ValueError(f"El peso de la carga supera la capacidad del camion por {exceso} KG")

    def _validar_requerimientos_especiales(self) -> None:
        if self.tipo_carga in (TipoCarga.REFRIGERADA, TipoCarga.PERECEDERA) and not self.requiere_termo:
            raise ValueError(f"La carga {self.tipo_carga.value} requiere activar la opcion de termo/refrigeracion")

        if self.tipo_carga == TipoCarga.PELIGROSA:
            if not self.numero_onu:
                raise ValueError("Las cargas peligrosas requieren un codigo ONU obligatorio")
            if not ONU_REGEX.match(self.numero_onu.strip()):
                raise ValueError(
                    f"Codigo ONU '{self.numero_onu}' invalido. Debe constar de 4 digitos (ej: 1234 o UN1234)"
                )

        if self.tipo_carga == TipoCarga.VALORES and not self.req_blindaje:
            raise ValueError("Las cargas de valores requieren obligatoriamente un camion blindado")

        if self.tipo_carga == TipoCarga.FRAGIL:
            if not self.req_embalaje or len(self.req_embalaje.strip()) < MIN_LONGITUD_EMBALAJE:
                raise ValueError(
                    "La carga fragil requiere una especificacion de embalaje de al menos "
                    f"{MIN_LONGITUD_EMBALAJE} caracteres"
                )

    def _validar_coherencia_financiera(self) -> None:
        diferencia = abs((self.monto_neto + self.monto_iva) - self.monto_total)
        if diferencia > ReglasNegocio.TOLERANCIA_MAX:
            raise ValueError(
                f"El monto total ({self.monto_total}) no coincide con la suma del neto "
                f"({self.monto_neto}) e IVA ({self.monto_iva})"
            )

        if self.moneda == Moneda.CLP:
            iva_esperado = self.monto_neto * ReglasNegocio.IVA_PORCENTAJE
            diferencia_iva = abs(self.monto_iva - iva_esperado)
            if diferencia_iva > TOLERANCIA_IVA_CLP:
                raise ValueError(
                    f"El monto del IVA ({self.monto_iva}) no corresponde al "
                    f"{ReglasNegocio.IVA_PORCENTAJE * 100}% del neto"
                )

    @model_validator(mode="after")
    def validar_reglas_de_negocio(self) -> "ContratoBase":
        """Ejecuta todos los validadores de dominio en secuencia logica."""
        self._validar_fechas()
        self._validar_carga_y_capacidad()
        self._validar_requerimientos_especiales()
        self._validar_coherencia_financiera()
        return self

    # Alias para retrocompatibilidad
    _vali_fechas = _validar_fechas
    _vali_carga_y_capacidad = _validar_carga_y_capacidad
    _vali_requerimientos_especiales = _validar_requerimientos_especiales
    _vali_coherencia_financiera = _validar_coherencia_financiera
    vali_reglas_de_negocio = validar_reglas_de_negocio


class ContratoCrear(ContratoBase):
    """Modelo DTO para la solicitud de creacion de un contrato."""

    pass


class ContratoModelo(ContratoBase):
    """Modelo de entidad y persistencia del contrato."""

    id: UUID = Field(default_factory=uuid4, description="ID unico del contrato")
    estado: EstadoContrato = Field(default=EstadoContrato.BORRADOR, description="Estado actual en el ciclo de vida")
    id_transportista: UUID | None = Field(default=None, description="ID del transportista asignado")
    id_camion: UUID | None = Field(default=None, description="ID del camion asignado")
    fecha_publicacion: datetime | None = Field(default=None, description="Fecha de publicacion del contrato")
