import uuid
from domain.enums import Rol

class Usuario:
    def __init__(self, nombre: str, email: str, rol: Rol):
        self.id = id or uuid.uuid4()
        self.nombre = nombre
        self.rol = rol

