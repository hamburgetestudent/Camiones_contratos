"""
Capa de acceso a datos (DAO) para la entidad Usuario.
"""

from typing import Optional
from uuid import UUID

from dao.base_dao import BaseDAO, DAOMemoria
from domain.modelos_usuario import UsuarioModelo


class UsuarioDAO(BaseDAO[UsuarioModelo, UUID]):
    """Interfaz abstracta para operaciones de persistencia de usuarios."""

    def get_by_email(self, email: str) -> Optional[UsuarioModelo]:
        """Busca un usuario por su correo electronico."""
        return self.obtener_por_email(email)

    def obtener_por_email(self, email: str) -> Optional[UsuarioModelo]:
        """Busca un usuario por su correo electronico."""
        raise NotImplementedError


class UsuarioDAOMemoria(DAOMemoria[UsuarioModelo, UUID], UsuarioDAO):
    """Implementacion en memoria del DAO de usuarios."""

    def obtener_por_email(self, email: str) -> Optional[UsuarioModelo]:
        """Busca un usuario por su correo electronico."""
        email_normalizado = email.strip().lower()
        for usuario in self._almacenamiento.values():
            if usuario.email.strip().lower() == email_normalizado:
                return usuario
        return None

    def get_by_email(self, email: str) -> Optional[UsuarioModelo]:
        return self.obtener_por_email(email)


# Instancia por defecto
UsuarioDAO = UsuarioDAOMemoria
