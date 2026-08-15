"""
Apartado solamente de contratos, agregue librerias  luego las
agregare a requeriments si es necesario

Pero es esta la principal
- Pydantic es un validador pero viene dentro de la misma fastApi

"""

from datetime import datetime, timedelta, timezone
from enum import Enum, StrEnum
from typing import Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, field_validator, model_validator, AwareDatetime

# ================================
# Enumeraciones de estados y tipos
# ================================

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

# -----------------------------------

# =======================================
# TODO: Se definio solo 3 tipos de camiones este apartado hay que mejorarlo
# Despues se puede agregar mas o definirlo solamente como carga mi nima y maxima
# que determine el usuario, por lo que queda todavia a discución
# =======================================

class TipoCamion(StrEnum):
    CAMIONETA = "CAMIONETA"
    CAMION_3_EJES = "CAMION_3_EJES"
    TRAILER = "TRAILER"

# Valores en KG 
CAPACIDAD_MAX = {
    TipoCamion.CAMIONETA : 3500,
    TipoCamion.CAMION_3_EJES : 15000,
    TipoCamion.TRAILER : 30000,
}
#----------------------------------
class Moneda(StrEnum):
    CLP = "CLP"
    UF = "UF"
    UTM = "UTM"

    # Monedas extranjeras
    USD = "USD" # Dolar
    EUR = "EUR" # Euro
    CNY = "CNY" # Yuan Chino
    BRL = "BRL" # Real Brasileño


# ===============
# Pydantic esquema
# ===============
class ContratoBase(BaseModel):
    # 1. Identificadores basicos 
    # NOTE: Los 3 puntos obliga a dar ese valor, min_length a valor minimo de cadena 
    # Ingresada
    id_empresa_generadora = UUID
    origen : str = Field(...,min_length= 3, description="Dirección o comuna de origen")
    destino : str = Field(..., min_length= 3, description="Dirección o comuna de destino")

    # 2. Fechas
    f_estimada_salida : AwareDatetime
    f_estimada_llegada : AwareDatetime
    f_cierre_postulaciones : AwareDatetime

    # 3. Carga y vehiculos (Este apartado puede ser cambiado a carga minima y maxima pero por el momento solo se ocuparan estos ejemplos base)
    """
    En pythanic se ocupa 
    gt = mayor que
    ge = mayor o igual
    lt = menor que
    le = menor o igual 
    """
    tipo_carga : TipoCarga
    peso_total: float = Field(..., gt = 0, description = "Peso en Kg")
    volumen_m3 : Optional[float] = Field(None, gt= 0)
    tipo_camion_requerido = TipoCamion

    # Requerimientos especiales , agregar despues
    requiere_termo : bool = False

    # 4. Economicos
    moneda : Moneda = Moneda.CLP
    monto_neto : float = Field(..., gt= 0)
    monto_iva : float = Field(..., ge= 0)
    monto_total : float = Field(..., gt = 0)

    # ====================
    # Validaciones de campo unico y sanitizacion
    # ====================

    """
    Separa el texto, limpia espacios y separa palabras para luego dejarlas
    en minuscula para evitar duplicados. cls llama a al modelo base
    """

    @field_validator("origen", "destino", mode="before")
    @classmethod
    def sanitizar_texto(cls, valor : str) -> str:
        if isinstance(valor, str):
            return " ".join(valor.strip().split()).upper()
        return valor


    # ============================
    # Validaciones Cruzadas
    # ============================

    @model_validator(mode = "after")
    def validar_reglas_de_negocio(self) -> "ContratoBase":
        ahora = datetime.now(timezone.utc)

        # 1. Validacion de Fechas
        if self.f_estimada_salida <= ahora + timedelta(hours=2):
            raise ValueError("La fecha estimada de salida debe programarse con al menos 2 horas de anticipación")

        if self.f_estimada_llegada <= self.f_estimada_salida:
            raise ValueError("La fecha estimada de llegada debe ser posterior a la fecha de salida")

        if self.f_cierre_postulaciones > self.f_estimada_salida:
            raise ValueError("El cierre de postulaciones no puede ser posterior a la fecha de salida")


        # 2. Validacion Geografica y de carga
        if self.origen == self.destino:
            raise ValueError("El origen y destino no pueden ser identicos")

        # FIXME: ARREGLAR
        # limite_peso = CAPACIDAD_MAX.get()
        # if self.peso_total > limite_peso:
        #     raise ValueError(
        #         f"El peso ({self.peso_total} kg) excede la capacidad del vehiculo ({self.tipo_camion_requerido.value}: {limite_peso} kg )   "
        #     )

        if self.tipo_carga == TipoCarga.REFRIGERADA and not self.requiere_termo:
            raise ValueError("Carga refrigerada, requiere Termo")

        # 3. Validación financiera (Margen de tolerancia para floats)
        # NOTE: Los valores economicos deben ser evitados para manejarlos
        # o es ocupar alguna libreria que maneje los decimales bien o buscar
        # un metodo logico para utilizarlo con python (aunque claro en este apartado no es necesario)

        diferencia = abs((self.monto_neto + self.monto_iva) - self.monto_total)
        if diferencia > 0.01:
            raise ValueError("El monto total no coincide con la suma del monto neto y el IVA")

        return self


class ContratoCrear(ContratoBase):
    """Esquema para recibir peticiones de creación"""
    pass

class ContratoModelo(ContratoBase):
    """
        Define la estructura completa de datos del contrato
    """

    #id: con UUID4 se genera un identificador unico
    id : UUID = Field(default_factory=uuid4) 
    estado : EstadoContrato = EstadoContrato.BORRADOR
    # NOTE: Esta parte hay que definirla correctamente, si sera llamada id_transportista o Rut
    id_transportista : Optional[UUID] = None
    id_camion : Optional[UUID] = None
    fecha_publicacion : Optional[datetime] = None


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
                f"TRansición de estado no permitida, no se puede pasar de {contrato.estado.value} a {nuevo_estado.value}"
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