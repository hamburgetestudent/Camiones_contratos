import uuid
from datetime import datetime
from domain.enums import TipoDocumento, EstadoValidacion

class Documento:
    def __init__(self,
        user_id: uuid.UUID,
        tipo: TipoDocumento,
        archivo: str,
        id: uuid.UUID | None = None,
        estado: EstadoValidacion = EstadoValidacion.PENDIENTE,
        creado_en: datetime | None = None):

        self.id = id or uuid.uuid4()
        self.user_id = user_id
        self.tipo = tipo
        self.archivo = archivo
        self.estado = estado
        self.creado_en = creado_en or datetime.now()
        