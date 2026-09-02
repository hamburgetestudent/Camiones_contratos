from typing import List, Optional
from uuid import UUID
from domain.modelos_usuario import UsuarioModelo
from dao.base_dao import BD_DAO

class UsuarioDAO(BD_DAO[UsuarioModelo, UUID]):
    def __init__(self):
        self._db: dict[UUID, UsuarioModelo] = {}

    def get_id(self, entidad_id: UUID) -> Optional[UsuarioModelo]:
        return self._db.get(entidad_id)

    def get_all(self) -> List[UsuarioModelo]:
        return list(self._db.values())

    def save(self, entidad: UsuarioModelo) -> UsuarioModelo:
        self._db[entidad.id] = entidad
        return entidad

    def update(self, entidad_id: UUID, entidad: UsuarioModelo) -> Optional[UsuarioModelo]:
        if entidad_id in self._db:
            self._db[entidad_id] = entidad
            return entidad
        return None

    def delete(self, entidad_id: UUID) -> bool:
        if entidad_id in self._db:
            del self._db[entidad_id]
            return True
        return False

    def get_by_email(self, email: str) -> Optional[UsuarioModelo]:
        for usuario in self._db.values():
            if usuario.email == email:
                return usuario
        return None

