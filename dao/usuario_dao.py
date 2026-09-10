"""Capa de acceso a datos (DAO) para la entidad Usuario."""

from abc import abstractmethod
from uuid import UUID

from dao.base_dao import BaseDAO, DAOMemoria
from domain.modelos_usuario import UsuarioModelo


class UsuarioDAO(BaseDAO[UsuarioModelo, UUID]):
    """Interfaz abstracta para operaciones de persistencia de usuarios."""

    @abstractmethod
    def obtener_por_email(self, email: str) -> UsuarioModelo | None:
        """Busca un usuario por su correo electronico."""
        pass

    # Alias para retrocompatibilidad
    def obt_por_email(self, email: str) -> UsuarioModelo | None:
        """Alias para obtener_por_email."""
        return self.obtener_por_email(email)

    def obt_email(self, email: str) -> UsuarioModelo | None:
        """Alias para obtener_por_email."""
        return self.obtener_por_email(email)

    def get_by_email(self, email: str) -> UsuarioModelo | None:
        """Alias en ingles para obtener_por_email."""
        return self.obtener_por_email(email)


class UsuarioDAOMemoria(DAOMemoria[UsuarioModelo, UUID], UsuarioDAO):
    """Implementacion en memoria thread-safe del DAO de usuarios."""

    def obtener_por_email(self, email: str) -> UsuarioModelo | None:
        """Busca un usuario por su correo electronico de forma sincronizada."""
        email_normalizado = email.strip().lower()
        with self._lock:
            for usuario in self._almacenamiento.values():
                if usuario.email.strip().lower() == email_normalizado:
                    return usuario
            return None

    obt_por_email = obtener_por_email
    obt_email = obtener_por_email
    get_by_email = obtener_por_email
