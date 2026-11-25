"""DAO de la entidad Usuario (tabla ``usuarios`` en SQLite)."""

from __future__ import annotations

import sqlite3
from abc import abstractmethod
from uuid import UUID

from dao.base_dao import BaseDAO, DAOSQLite
from domain.modelos_usuario import EstadoUsuario, RolUsuario, UsuarioModelo

_SQL_SELECT = "SELECT id, nombre, email, rol, password_hash, estado FROM usuarios"

_SQL_GUARDAR = """
    INSERT INTO usuarios (id, nombre, email, rol, password_hash, estado)
    VALUES (?, ?, ?, ?, ?, ?)
    ON CONFLICT(id) DO UPDATE SET
        nombre = excluded.nombre,
        email = excluded.email,
        rol = excluded.rol,
        password_hash = excluded.password_hash,
        estado = excluded.estado
"""

_SQL_ACTUALIZAR = (
    "UPDATE usuarios SET nombre = ?, email = ?, rol = ?, password_hash = ?, "
    "estado = ? WHERE id = ? AND eliminado = 0"
)


def _fila_a_usuario(fila: sqlite3.Row) -> UsuarioModelo:
    """Convierte una fila de SQLite en una instancia de UsuarioModelo."""
    return UsuarioModelo(
        id=UUID(fila["id"]),
        nombre=fila["nombre"],
        email=fila["email"],
        rol=RolUsuario(fila["rol"]),
        password_hash=fila["password_hash"],
        estado=EstadoUsuario(fila["estado"]),
    )


def _a_parametros(usuario: UsuarioModelo) -> tuple[str, ...]:
    """Parametros (sin el ID) comunes a insertar y actualizar; el correo va en minusculas."""
    return (
        usuario.nombre,
        usuario.email.strip().lower(),
        RolUsuario(usuario.rol).value,
        usuario.password_hash,
        EstadoUsuario(usuario.estado).value,
    )


class UsuarioDAO(BaseDAO[UsuarioModelo, UUID]):
    """Interfaz abstracta de persistencia de usuarios."""

    @abstractmethod
    def obtener_por_email(
        self, conn: sqlite3.Connection, email: str
    ) -> UsuarioModelo | None:
        """Busca un usuario por correo (insensible a mayusculas y espacios extremos)."""

    @abstractmethod
    def existe_email(self, conn: sqlite3.Connection, email: str) -> bool:
        """True si el correo ya esta vinculado a una cuenta, incluso dada de baja."""


class UsuarioDAOSQLite(DAOSQLite, UsuarioDAO):
    """Persistencia de usuarios en SQLite. Ignora las cuentas dadas de baja."""

    def obtener_por_id(
        self, conn: sqlite3.Connection, entidad_id: UUID
    ) -> UsuarioModelo | None:
        fila = conn.execute(
            f"{_SQL_SELECT} WHERE id = ? AND eliminado = 0", (str(entidad_id),)
        ).fetchone()
        return _fila_a_usuario(fila) if fila else None

    def obtener_por_email(
        self, conn: sqlite3.Connection, email: str
    ) -> UsuarioModelo | None:
        fila = conn.execute(
            f"{_SQL_SELECT} WHERE lower(trim(email)) = ? AND eliminado = 0",
            (email.strip().lower(),),
        ).fetchone()
        return _fila_a_usuario(fila) if fila else None

    def existe_email(self, conn: sqlite3.Connection, email: str) -> bool:
        fila = conn.execute(
            "SELECT 1 FROM usuarios WHERE email = ?", (email.strip(),)
        ).fetchone()
        return fila is not None

    def obtener_todos(self, conn: sqlite3.Connection) -> list[UsuarioModelo]:
        filas = conn.execute(
            f"{_SQL_SELECT} WHERE eliminado = 0 ORDER BY created_at ASC, rowid ASC"
        ).fetchall()
        return [_fila_a_usuario(fila) for fila in filas]

    def guardar(
        self, conn: sqlite3.Connection, entidad: UsuarioModelo
    ) -> UsuarioModelo:
        conn.execute(_SQL_GUARDAR, (str(entidad.id), *_a_parametros(entidad)))
        return entidad

    def actualizar(
        self, conn: sqlite3.Connection, entidad_id: UUID, entidad: UsuarioModelo
    ) -> UsuarioModelo | None:
        cursor = conn.execute(
            _SQL_ACTUALIZAR, (*_a_parametros(entidad), str(entidad_id))
        )
        return entidad if cursor.rowcount > 0 else None
