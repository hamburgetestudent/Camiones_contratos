"""
Capa de acceso a datos (DAO) para la entidad Usuario.
"""

from typing import List, Optional
from uuid import UUID

from dao.base_dao import BaseDAO, DAOMemoria
from domain.modelos_usuario import UsuarioModelo
from dao.base_dao import BD_DAO

class UsuarioDAO(BD_DAO[UsuarioModelo, UUID]):
    def __init__(self):
        self._db: dict[UUID, UsuarioModelo] = {}

    def obt_id(self, entidad_id: UUID) -> Optional[UsuarioModelo]:
        return self._db.get(entidad_id)

    def obt_todos(self) -> List[UsuarioModelo]:
        return list(self._db.values())

    def guardar(self, entidad: UsuarioModelo) -> UsuarioModelo:
        self._db[entidad.id] = entidad
        return entidad

    def actualizar(self, entidad_id: UUID, entidad: UsuarioModelo) -> Optional[UsuarioModelo]:
        if entidad_id in self._db:
            self._db[entidad_id] = entidad
            return entidad
        return None

    def eliminar(self, entidad_id: UUID) -> bool:
        if entidad_id in self._db:
            del self._db[entidad_id]
            return True
        return False

    def obt_email(self, email: str) -> Optional[UsuarioModelo]:
        for usuario in self._db.values():
            if usuario.email == email:
                return usuario
        return None


class UsuarioDAO(BaseDAO[UsuarioModelo, UUID]):
    """Interfaz abstracta para operaciones de persistencia de usuarios."""

    def obt_por_email(self, email: str) -> Optional[UsuarioModelo]:
        """Busca un usuario por su correo electronico."""
        raise NotImplementedError


class UsuarioDAOMemoria(DAOMemoria[UsuarioModelo, UUID], UsuarioDAO):
    """Implementacion en memoria thread-safe del DAO de usuarios."""

    def obt_por_email(self, email: str) -> Optional[UsuarioModelo]:
        """Busca un usuario por su correo electronico de forma sincronizada."""
        email_normalizado = email.strip().lower()
        with self._lock:
            for usuario in self._almacenamiento.values():
                if usuario.email.strip().lower() == email_normalizado:
                    return usuario
            return None

    get_by_email = obt_por_email