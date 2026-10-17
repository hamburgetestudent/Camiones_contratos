"""Capa de acceso a datos (DAO) para la entidad Usuario."""

import sqlite3
import threading
from abc import abstractmethod
from pathlib import Path
from uuid import UUID

from dao.base_dao import BaseDAO, DAOMemoria
from dao.sqlite_db import DEFAULT_DB_PATH, inicializar_bd, obtener_conexion
from domain.modelos_usuario import EstadoUsuario, RolUsuario, UsuarioModelo


class UsuarioDAO(BaseDAO[UsuarioModelo, UUID]):
    """Interfaz abstracta para operaciones de persistencia de usuarios."""

    @abstractmethod
    def obtener_por_email(self, email: str) -> UsuarioModelo | None:
        """Busca un usuario por su correo electronico."""

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


class UsuarioDAOSQLite(UsuarioDAO):
    """Implementacion persistente en SQLite del DAO de usuarios."""

    def __init__(self, db_path: str | Path | None = None, cargar_semilla: bool = True) -> None:
        self._db_path = Path(db_path) if db_path else DEFAULT_DB_PATH
        self._lock = threading.RLock()
        inicializar_bd(self._db_path, cargar_semilla=cargar_semilla)

    @staticmethod
    def _fila_a_modelo(fila: sqlite3.Row) -> UsuarioModelo:
        """Convierte una fila de SQLite en una instancia de UsuarioModelo."""
        return UsuarioModelo(
            id=UUID(fila["id"]),
            nombre=fila["nombre"],
            email=fila["email"],
            rol=RolUsuario(fila["rol"]),
            password_hash=fila["password_hash"],
            estado=EstadoUsuario(fila["estado"]),
        )

    def obtener_por_id(self, entidad_id: UUID) -> UsuarioModelo | None:
        """Obtiene un usuario desde SQLite por su UUID."""
        with self._lock, obtener_conexion(self._db_path) as conn:
            cursor = conn.execute(
                "SELECT id, nombre, email, rol, password_hash, estado FROM usuarios WHERE id = ?",
                (str(entidad_id),),
            )
            fila = cursor.fetchone()
            return self._fila_a_modelo(fila) if fila else None

    def obtener_todos(self) -> list[UsuarioModelo]:
        """Retorna todos los usuarios registrados en SQLite."""
        with self._lock, obtener_conexion(self._db_path) as conn:
            cursor = conn.execute(
                "SELECT id, nombre, email, rol, password_hash, estado FROM usuarios ORDER BY created_at ASC"
            )
            return [self._fila_a_modelo(fila) for fila in cursor.fetchall()]

    def obtener_por_email(self, email: str) -> UsuarioModelo | None:
        """Busca un usuario por correo electrónico (insensible a mayúsculas/minúsculas)."""
        email_normalizado = email.strip().lower()
        with self._lock, obtener_conexion(self._db_path) as conn:
            cursor = conn.execute(
                "SELECT id, nombre, email, rol, password_hash, estado FROM usuarios WHERE lower(trim(email)) = ?",
                (email_normalizado,),
            )
            fila = cursor.fetchone()
            return self._fila_a_modelo(fila) if fila else None

    def guardar(self, entidad: UsuarioModelo) -> UsuarioModelo:
        """Inserta o reemplaza un usuario en la tabla usuarios de SQLite."""
        with self._lock, obtener_conexion(self._db_path) as conn:
            conn.execute(
                """
                INSERT INTO usuarios (id, nombre, email, rol, password_hash, estado)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    nombre = excluded.nombre,
                    email = excluded.email,
                    rol = excluded.rol,
                    password_hash = excluded.password_hash,
                    estado = excluded.estado
                """,
                (
                    str(entidad.id),
                    entidad.nombre,
                    entidad.email.strip().lower(),
                    entidad.rol.value if isinstance(entidad.rol, RolUsuario) else str(entidad.rol),
                    entidad.password_hash,
                    entidad.estado.value if isinstance(entidad.estado, EstadoUsuario) else str(entidad.estado),
                ),
            )
        return entidad

    def actualizar(self, entidad_id: UUID, entidad: UsuarioModelo) -> UsuarioModelo | None:
        """Actualiza un usuario existente en SQLite. Retorna None si no existe."""
        with self._lock, obtener_conexion(self._db_path) as conn:
            cursor = conn.execute(
                """
                UPDATE usuarios
                SET nombre = ?, email = ?, rol = ?, password_hash = ?, estado = ?
                WHERE id = ?
                """,
                (
                    entidad.nombre,
                    entidad.email.strip().lower(),
                    entidad.rol.value if isinstance(entidad.rol, RolUsuario) else str(entidad.rol),
                    entidad.password_hash,
                    entidad.estado.value if isinstance(entidad.estado, EstadoUsuario) else str(entidad.estado),
                    str(entidad_id),
                ),
            )
            if cursor.rowcount == 0:
                return None
            return entidad

    def eliminar(self, entidad_id: UUID) -> bool:
        """Elimina un usuario por su UUID en SQLite."""
        with self._lock, obtener_conexion(self._db_path) as conn:
            cursor = conn.execute("DELETE FROM usuarios WHERE id = ?", (str(entidad_id),))
            return cursor.rowcount > 0

    def existe(self, entidad_id: UUID) -> bool:
        """Verifica si el usuario existe en SQLite."""
        with self._lock, obtener_conexion(self._db_path) as conn:
            cursor = conn.execute("SELECT 1 FROM usuarios WHERE id = ?", (str(entidad_id),))
            return cursor.fetchone() is not None

    obt_por_email = obtener_por_email
    obt_email = obtener_por_email
    get_by_email = obtener_por_email

