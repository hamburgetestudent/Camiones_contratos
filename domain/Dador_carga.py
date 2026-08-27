import uuid
from domain.enums import EstadoValidacion

class Datos_facturados:
    def __init__(self, razon_social: str, direccion: str, correo_facturacion: str):
        self.id = id or uuid.uuid4()
        self.razon_social = razon_social
        self.direccion = direccion
        self.correo_facturacion = correo_facturacion

class Dador_carga:
    def __init__(self, nombre: str, rut_empresa: str, datos_facturados: Datos_facturados, estado_validacion: EstadoValidacion = EstadoValidacion.Pendiente):
        self.id = id or uuid.uuid4()
        self.nombre = nombre
        self.rut_empresa = rut_empresa
        self.datos_facturados = datos_facturados
        self.estado_validacion = estado_validacion