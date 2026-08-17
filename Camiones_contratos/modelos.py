"""
Apartado solamente de contratos, agregue librerias  luego las
agregare a requeriments si es necesario

Pero es esta la principal
- Pydantic es un validador pero viene dentro de la misma fastApi

"""

from datetime import datetime, timedelta, timezone
from enum import StrEnum
from typing import Optional, Annotated
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, model_validator, AwareDatetime, BeforeValidator

# =========================================
# Enumeraciones de estados y tipos de datos
# =========================================

def limpiar_texto(valor : str) -> str:
    # Limpieza de texto, convierte palabras a string para eliminar espacios y evitar duplicados
    if isinstance(valor, str):
        return " ".join(valor.strip().split()).upper()
    return valor

# Tipo retulizable de limpiar texto
TextoNormalizado = Annotated[str, BeforeValidator(limpiar_texto)]

class ReglasNegocio:
    """
    Parametros globales de las monedas y sus configuraciones
    NOTE: Por cambiar si el contrato esta fuera de Chile
    """

    IVA_PORCENTAJE: float = 0.19

    # Tolerancia maxima permitida en discrepancia en numeros financieros flotantes
    TOLERANCIA_MAX: float = 0.01

    # Tiempo de anticipacion minima para agendar la hora de salida
    ANTICIPACION_MIN_H: int = 2

class EstadoContrato(StrEnum):
    BORRADOR = "BORRADOR"
    PUBLICADO = "PUBLICADO"
    EN_POSTULACION = "EN_POSTULACION"
    ADJUDICADO = "ADJUDICADO"
    EN_TRANSITO = "EN_TRANSITO"
    ENTREGADO = "ENTREGADO"
    FINALIZADO = "FINALIZADO"
    CANCELADO = "CANCELADO"
    EN_DISPUTA = "EN_DISPUTA"

class TipoCarga(StrEnum):
    # Opciones generales
    GENERAL = "GENERAL"
    REFRIGERADA = "REFRIGERADA"
    PELIGROSA = "PELIGROSA"

    # Opciones especiales 
    # TODO: requiere validaciones adicionales todavia no creadas
    FRAGIL = "FRAGIL" # Req: Embalaje especial
    GRANEL_LIQUIDO = "GRANEL_LIQUIDO" # Req: Cisterna/Tanque
    GRANEL_SOLIDO = "GRANEL_SOLIDO" # Req: Tolva/Silos
    PERECEDERA = "PERECEDERA" # Req: Depende ----
    SOBREDIMENSIONADA = "SOBREDIMENSIONADA" # Req: Esta es la mas compleja ya que requiere de diversos permisos y equipo
    VIVA = "VIVA" # Ganado, animales , etc
    VALORES = "VALORES" # Req: Las cargas con valores requieren en su mayoria automoviles blindados
    VEHICULAR = "VEHICULAR" # Req: tipo de camion cigueña/nodriza

class Moneda(StrEnum):
    CLP = "CLP"
    UF = "UF"
    UTM = "UTM"

    # Monedas extranjeras / En general no utilizables todavia
    USD = "USD" # Dolar
    EUR = "EUR" # Euro
    CNY = "CNY" # Yuan Chino
    BRL = "BRL" # Real Brasileño


# ================================
# Esquema general de los contratos
# ================================


class ContratoBase(BaseModel):
    # 1. Identificadores basicos 
    # NOTE: Los 3 puntos obliga a dar ese valor, min_length a valor minimo de cadena 
    # Ingresada
    id_empresa_generadora: UUID = Field(..., description= "ID de la empresa")
    origen: str = Field(...,min_length= 3, description="Dirección o comuna de origen")
    destino: str = Field(..., min_length= 3, description="Dirección o comuna de destino")

    # 2. Fechas
    f_estimada_salida: AwareDatetime = Field(..., description="Fecha y hora estimada de salida")
    f_estimada_llegada: AwareDatetime = Field(..., description="Fecha y hora de llegada estimada")
    f_cierre_postulaciones: AwareDatetime = Field(..., description="Fecha y hora limite de postulacion")

    # 3. Carga y vehiculos (Este apartado puede ser cambiado a carga minima y maxima pero por el momento solo se ocuparan estos ejemplos base)
    """
    En pythanic se ocupa 
    gt = mayor que
    ge = mayor o igual
    lt = menor que
    le = menor o igual 
    """
    input_camionKG: float = Field(..., gt= 0, description= "Capacidad en KG")
    tipo_carga : TipoCarga = Field(..., description="Tipo de carga transportada")
    peso_total: float = Field(..., gt = 0, description = "Peso en Kg")
    volumen_m3 : Optional[float] = Field(None, gt= 0, description= "Volumen en metros cubicos")

    # 4. Requerimientos especiales
    requiere_termo : bool = Field(default= False, description="Indica si el camion requiere refrigeracion/termo")
    numero_onu: Optional[str] = Field(default= None, description= "Los numeros onu de 4 digitos son hechas para cuando la carga es peligrosa")
    req_embalaje: Optional[str] = Field(default= None,min_length=10, description="Instrucciones especificas de emabalaje")
    req_blindaje: bool = Field(default= False, description= "Requerimiento de blindaje")

    # 5. Economicos
    moneda : Moneda = Field(default=Moneda.CLP, description= "Moneda de pago del contrato")
    monto_neto : float = Field(..., gt= 0, description= "Monto Neto")
    monto_iva : float = Field(..., ge= 0, description= "Monto IVA")
    monto_total : float = Field(..., gt = 0, description= "Monto total: Monto IVA + Neto")

    # ============================
    # Validaciones Cruzadas
    # ============================

    @model_validator(mode = "after")
    def validar_reglas_de_negocio(self) -> "ContratoBase":

        ahora = datetime.now(timezone.utc)
        limite_salida = ahora + timedelta(hours=ReglasNegocio.ANTICIPACION_MIN_H)

        # A. Validacion de Fechas
        if self.f_estimada_salida <= limite_salida:
            raise ValueError("La fecha estimada de salida debe programarse con al menos 2 horas de anticipación")

        if self.f_estimada_llegada <= self.f_estimada_salida:
            raise ValueError("La fecha estimada de llegada debe ser posterior a la fecha de salida")

        if self.f_cierre_postulaciones > self.f_estimada_salida:
            raise ValueError("El cierre de postulaciones no puede ser posterior a la fecha de salida")

        # B. Validacion Geografica y de carga
        if self.origen == self.destino:
            raise ValueError("El origen y destino no pueden ser identicos")

        # C. Validacion de Vehiculo
        if self.peso_total > self.input_camionKG:
            raise ValueError(
                f"El valor de la carga supera a la capacidad del camion por {self.peso_total - self.input_camionKG}"
            )

        # D. Configuraciones especiales / extras

        # 1. Carga refrigerada
        if self.tipo_carga == TipoCarga.REFRIGERADA and not self.requiere_termo:
            raise ValueError("Requiere carga refrigerada requiere activar la opcion termo")

        # 2. Carga peligrosa
        if self.tipo_carga == TipoCarga.PELIGROSA:
            if not self.numero_onu:
                raise ValueError("Las cargas peligrosas requieren de un numero ONU")
            onu_limpio = self.numero_onu.strip().upper()
            es_valido = (
                (onu_limpio.startswith("UN") and len(onu_limpio) == 6 and onu_limpio[2:].isdigit()) or
                (len(onu_limpio) == 4 and onu_limpio.isdigit())
            )
            if not es_valido:
                raise ValueError(
                    f"Codigo ONU {self.numero_onu} invalido. Debe ser de solo 4 digitos ej: (1234)"
                )

        # 3. Blindaje
        if self.tipo_carga == TipoCarga.VALORES and not self.req_blindaje:
            raise ValueError(
                f"Las cargas de valores requieren un camion con blindaje"
            )

        # 4. Fragil
        if self.tipo_carga == TipoCarga.FRAGIL:
            if not self.req_embalaje or len(self.req_embalaje.strip()) < 10:
                raise ValueError(
                    f"Carga fragil requiere una especificacion de al menos 10 caracteres."
                )

        # E. Coherencia financiera
        diferencia = abs((self.monto_neto + self.monto_iva)- self.monto_total)
        if diferencia > ReglasNegocio.TOLERANCIA_MAX:
            raise ValueError(
                f"El monto total: ({self.monto_total}) no coincide con la suma del neto e iva"
            )

        if self.moneda == Moneda.CLP:
            iva_esperado = self.monto_neto * ReglasNegocio.IVA_PORCENTAJE
            diferencia_iva = abs(self.monto_iva - iva_esperado)
            # Tolerancia de 5 pesos por redondeo
            if diferencia_iva > 5.0:
                raise ValueError(
                    f"El monto del IVA ({self.monto_iva}) no corresponde al {ReglasNegocio.IVA_PORCENTAJE * 100}%"
                )
        return self

class ContratoCrear(ContratoBase):
    """
    Modelo de contrato para la creación de contratos
    """
    pass

class ContratoModelo(ContratoBase):
    """
        Define la estructura completa de datos del contrato
    """
    # NOTE: Esta parte hay que definirla correctamente, si sera llamada id_transportista o Rut
    #id: con UUID4 se genera un identificador unico
    id : UUID = Field(default_factory=uuid4, description="ID único del contrato") 
    estado : EstadoContrato = Field(EstadoContrato.BORRADOR, description="Estado del contrato")
    id_transportista : Optional[UUID] = Field(default=None, description="Transportista asignado")
    id_camion : Optional[UUID] = Field(default=None, description="ID del camion asignado")
    fecha_publicacion : Optional[datetime] = Field(default=None, description="Fecha de la publicación del contrato")

# =====================
# Maquina de estados (transiciones y cambios)
# =====================

class MaquinaEstadosContrato:
    """Clase encargada de controlar y permitir transiciones 
    válidas de estado."""

    """
    Valga la redundancia este apartado define las transiciones permitidas
    Aunque hay que destacar los estados cancelado y finalizado ocupan un
    "set()" para que no se puedan alterar las transiciones nuevamente
    """
    TRANSICIONES_PERMITIDAS = {
        EstadoContrato.BORRADOR: {
            EstadoContrato.PUBLICADO, 
            EstadoContrato.CANCELADO
            },
        EstadoContrato.PUBLICADO: {
            EstadoContrato.EN_POSTULACION, 
            EstadoContrato.CANCELADO
            },
        EstadoContrato.EN_POSTULACION: {
            EstadoContrato.ADJUDICADO, 
            EstadoContrato.CANCELADO
            },
        EstadoContrato.ADJUDICADO: {
            EstadoContrato.EN_TRANSITO, 
            EstadoContrato.CANCELADO
            },
        EstadoContrato.EN_TRANSITO: {
            EstadoContrato.ENTREGADO, 
            EstadoContrato.EN_DISPUTA
            },
        EstadoContrato.ENTREGADO: {
            EstadoContrato.FINALIZADO, 
            EstadoContrato.EN_DISPUTA
            },
        EstadoContrato.CANCELADO: set(),
        EstadoContrato.FINALIZADO: set(),
        EstadoContrato.EN_DISPUTA: {
            EstadoContrato.FINALIZADO, 
            EstadoContrato.CANCELADO
            },
    }

    @classmethod
    def cambiar_estado(
        cls,
        contrato: ContratoModelo,
        nuevo_estado: EstadoContrato,
        id_transportista: Optional[UUID] = None,
        id_camion: Optional[UUID] = None,
    ) -> ContratoModelo:

        estados_posibles = cls.TRANSICIONES_PERMITIDAS.get(contrato.estado, set())

        # Verifica si la trancision esta dentro del diccionario, si no ValueError
        if nuevo_estado not in estados_posibles:
            raise ValueError(
                f"Transición de estado no permitida, no se puede pasar de {contrato.estado.value} a {nuevo_estado.value}"
            )

        # Aqui verifica si el cambio a publicado lleva informacion relevante id del camion y transportista
        if nuevo_estado == EstadoContrato.PUBLICADO:
            if contrato.id_transportista is not None:
                raise ValueError("Un contrato en estado 'publicado' no puede tener un transportista asignado.")
            contrato.fecha_publicacion = datetime.now(timezone.utc)

        elif nuevo_estado == EstadoContrato.ADJUDICADO:
            if not id_transportista or not id_camion:
                raise ValueError("Para adjudicar un contrato se requiere indicar obligatoriamente el 'id_transportista' y 'id_camion'")
            contrato.id_transportista = id_transportista
            contrato.id_camion = id_camion

        contrato.estado = nuevo_estado
        return contrato