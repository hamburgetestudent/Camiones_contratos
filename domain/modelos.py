"""
Modelos de dominio y esquemas de validacion Pydantic para Contratos de Camiones.
Refactorizados con validaciones modulares y desacoplados para mayor escalabilidad.
"""

from datetime import datetime, timedelta, timezone
try:
    from enum import StrEnum
except ImportError:
    from enum import Enum
    class StrEnum(str, Enum):
        pass
from typing import Optional, Annotated
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, model_validator, AwareDatetime, BeforeValidator

from domain.reglas import ReglasNegocio
from domain.maquina_estados import EstadoContrato


# =========================================
# Utilitarios y Sanitizacion de Datos
# =========================================

def limpiar_texto(valor: str) -> str:
    """Limpieza de texto: remueve espacios superfluos y convierte a mayúsculas."""
    if isinstance(valor, str):
        return " ".join(valor.strip().split()).upper()
    return valor


TextoNormalizado = Annotated[str, BeforeValidator(limpiar_texto)]


# =========================================
# Enumeraciones
# =========================================

class TipoCarga(StrEnum):
    # Opciones generales
    GENERAL = "GENERAL"
    REFRIGERADA = "REFRIGERADA"
    PELIGROSA = "PELIGROSA"

    # Opciones especiales con requerimientos de negocio
    FRAGIL = "FRAGIL"
    GRANEL_LIQUIDO = "GRANEL_LIQUIDO"
    GRANEL_SOLIDO = "GRANEL_SOLIDO"
    PERECEDERA = "PERECEDERA"
    SOBREDIMENSIONADA = "SOBREDIMENSIONADA"
    VIVA = "VIVA"
    VALORES = "VALORES"
    VEHICULAR = "VEHICULAR"


class Moneda(StrEnum):
    CLP = "CLP"
    UF = "UF"
    UTM = "UTM"
    USD = "USD"
    EUR = "EUR"
    CNY = "CNY"
    BRL = "BRL"


# =========================================
# Esquema Base del Contrato y Validaciones
# =========================================

class ContratoBase(BaseModel):
    # 1. Identificadores basicos y ubicacion
    id_empresa_generadora: UUID = Field(..., description="ID unico de la empresa generadora de carga")
    origen: TextoNormalizado = Field(..., min_length=3, description="Direccion o comuna de origen")
    destino: TextoNormalizado = Field(..., min_length=3, description="Direccion o comuna de destino")

    # 2. Fechas de operacion
    f_estimada_salida: AwareDatetime = Field(..., description="Fecha y hora estimada de salida")
    f_estimada_llegada: AwareDatetime = Field(..., description="Fecha y hora estimada de llegada")
    f_cierre_postulaciones: AwareDatetime = Field(..., description="Fecha y hora limite de postulacion")

    # 3. Especificaciones de carga y capacidad
    input_camionKG: float = Field(..., gt=0, description="Capacidad maxima del camion en KG")
    tipo_carga: TipoCarga = Field(..., description="Tipo de carga transportada")
    peso_total: float = Field(..., gt=0, description="Peso total de la carga en KG")
    volumen_m3: Optional[float] = Field(None, gt=0, description="Volumen estimado en metros cubicos")

    # 4. Requerimientos especiales
    requiere_termo: bool = Field(default=False, description="Indica si requiere equipo de refrigeracion/termo")
    numero_onu: Optional[str] = Field(default=None, description="Codigo ONU de 4 digitos para carga peligrosa")
    req_embalaje: Optional[str] = Field(default=None, min_length=10, description="Instrucciones detalladas de embalaje")
    req_blindaje: bool = Field(default=False, description="Indica si requiere transporte blindado")

    # 5. Aspectos economicos y financieros
    moneda: Moneda = Field(default=Moneda.CLP, description="Moneda de pago del contrato")
    monto_neto: float = Field(..., gt=0, description="Monto Neto del contrato")
    monto_iva: float = Field(..., ge=0, description="Monto del IVA")
    monto_total: float = Field(..., gt=0, description="Monto Total (Neto + IVA)")

    # =========================================
    # Sub-Validadores Modulares
    # =========================================

    def _validar_fechas(self) -> None:
        ahora = datetime.now(timezone.utc)
        limite_salida = ahora + timedelta(hours=ReglasNegocio.ANTICIPACION_MIN_H)

        if self.f_estimada_salida <= limite_salida:
            raise ValueError(
                f"La fecha estimada de salida debe programarse con al menos {ReglasNegocio.ANTICIPACION_MIN_H} horas de anticipacion"
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
        if self.tipo_carga == TipoCarga.REFRIGERADA and not self.requiere_termo:
            raise ValueError("La carga refrigerada requiere activar la opcion de termo/refrigeracion")

        if self.tipo_carga == TipoCarga.PELIGROSA:
            if not self.numero_onu:
                raise ValueError("Las cargas peligrosas requieren un codigo ONU obligatorio")
            onu_limpio = self.numero_onu.strip().upper()
            es_valido = (
                (onu_limpio.startswith("UN") and len(onu_limpio) == 6 and onu_limpio[2:].isdigit()) or
                (len(onu_limpio) == 4 and onu_limpio.isdigit())
            )
            if not es_valido:
                raise ValueError(f"Codigo ONU '{self.numero_onu}' invalido. Debe constar de 4 digitos (ej: 1234 o UN1234)")

        if self.tipo_carga == TipoCarga.VALORES and not self.req_blindaje:
            raise ValueError("Las cargas de valores requieren obligatoriamente un camion blindado")

        if self.tipo_carga == TipoCarga.FRAGIL:
            if not self.req_embalaje or len(self.req_embalaje.strip()) < 10:
                raise ValueError("La carga fragil requiere una especificacion de embalaje de al menos 10 caracteres")

    def _validar_coherencia_financiera(self) -> None:
        diferencia = abs((self.monto_neto + self.monto_iva) - self.monto_total)
        if diferencia > ReglasNegocio.TOLERANCIA_MAX:
            raise ValueError(
                f"El monto total ({self.monto_total}) no coincide con la suma del neto ({self.monto_neto}) e IVA ({self.monto_iva})"
            )

        if self.moneda == Moneda.CLP:
            iva_esperado = self.monto_neto * ReglasNegocio.IVA_PORCENTAJE
            diferencia_iva = abs(self.monto_iva - iva_esperado)
            if diferencia_iva > 5.0:
                raise ValueError(
                    f"El monto del IVA ({self.monto_iva}) no corresponde al {ReglasNegocio.IVA_PORCENTAJE * 100}% del neto"
                )

    @model_validator(mode="after")
    def validar_reglas_de_negocio(self) -> "ContratoBase":
        """Ejecuta los validadores de dominio en orden logico."""
        self._validar_fechas()
        self._validar_carga_y_capacidad()
        self._validar_requerimientos_especiales()
        self._validar_coherencia_financiera()
        return self


class ContratoCrear(ContratoBase):
    """Modelo DTO para la solicitud de creacion de un contrato."""
    pass


class ContratoModelo(ContratoBase):
    """Modelo completo de persistencia y entidad del contrato."""
    id: UUID = Field(default_factory=uuid4, description="ID unico del contrato")
    estado: EstadoContrato = Field(default=EstadoContrato.BORRADOR, description="Estado actual en el ciclo de vida")
    id_transportista: Optional[UUID] = Field(default=None, description="ID del transportista asignado")
    id_camion: Optional[UUID] = Field(default=None, description="ID del camion asignado")
    fecha_publicacion: Optional[datetime] = Field(default=None, description="Fecha de publicacion del contrato")
