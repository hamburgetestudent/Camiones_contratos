"""DAO de la entidad Postulacion (tabla ``postulaciones`` en SQLite)."""

from __future__ import annotations

import sqlite3
from abc import abstractmethod
from datetime import datetime
from uuid import UUID

from dao.base_dao import BaseDAO, DAOSQLite
from domain.postulacion import EstadoPostulacion, PostulacionModelo

_SQL_SELECT = (
    "SELECT id, carga_id, transportista_id, precio_oferta, tiempo_entrega_horas, "
    "comentario, estado, creado_en FROM postulaciones"
)

_SQL_GUARDAR = """
    INSERT INTO postulaciones (
        id, carga_id, transportista_id, precio_oferta, tiempo_entrega_horas,
        comentario, estado, creado_en
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(id) DO UPDATE SET
        carga_id = excluded.carga_id,
        transportista_id = excluded.transportista_id,
        precio_oferta = excluded.precio_oferta,
        tiempo_entrega_horas = excluded.tiempo_entrega_horas,
        comentario = excluded.comentario,
        estado = excluded.estado,
        creado_en = excluded.creado_en
"""

_SQL_ACTUALIZAR = (
    "UPDATE postulaciones SET carga_id = ?, transportista_id = ?, precio_oferta = ?, "
    "tiempo_entrega_horas = ?, comentario = ?, estado = ?, creado_en = ? WHERE id = ?"
)


def _fila_a_postulacion(fila: sqlite3.Row) -> PostulacionModelo:
    """Reconstruye una postulacion ya validada al momento de crearse (sin revalidar)."""
    return PostulacionModelo.model_construct(
        id=UUID(fila["id"]),
        carga_id=UUID(fila["carga_id"]),
        transportista_id=UUID(fila["transportista_id"]),
        precio_oferta=fila["precio_oferta"],
        tiempo_entrega_horas=fila["tiempo_entrega_horas"],
        comentario=fila["comentario"],
        estado=EstadoPostulacion(fila["estado"]),
        creado_en=datetime.fromisoformat(fila["creado_en"]),
    )


def _a_parametros(p: PostulacionModelo) -> tuple[object, ...]:
    return (
        str(p.id),
        str(p.carga_id),
        str(p.transportista_id),
        p.precio_oferta,
        p.tiempo_entrega_horas,
        p.comentario,
        EstadoPostulacion(p.estado).value,
        p.creado_en.isoformat(),
    )


class PostulacionDAO(BaseDAO[PostulacionModelo, UUID]):
    """Interfaz abstracta de persistencia de postulaciones."""

    @abstractmethod
    def obtener_por_contrato(
        self, conn: sqlite3.Connection, contrato_id: UUID
    ) -> list[PostulacionModelo]:
        """Postulaciones asociadas a un contrato o carga."""

    @abstractmethod
    def obtener_por_transportista(
        self, conn: sqlite3.Connection, transportista_id: UUID
    ) -> list[PostulacionModelo]:
        """Postulaciones enviadas por un transportista."""

    @abstractmethod
    def existe_para_contrato(self, conn: sqlite3.Connection, contrato_id: UUID) -> bool:
        """True si el contrato recibio al menos una postulacion."""

    @abstractmethod
    def actualizar_estado(
        self,
        conn: sqlite3.Connection,
        postulacion_id: UUID,
        estado: EstadoPostulacion,
    ) -> None:
        """Cambia solo el estado de una postulacion."""

    @abstractmethod
    def rechazar_competidoras(
        self, conn: sqlite3.Connection, contrato_id: UUID, ganadora_id: UUID
    ) -> None:
        """Marca como RECHAZADA toda postulacion del contrato excepto la ganadora."""


class PostulacionDAOSQLite(DAOSQLite, PostulacionDAO):
    """Persistencia de postulaciones en SQLite."""

    def obtener_por_id(
        self, conn: sqlite3.Connection, entidad_id: UUID
    ) -> PostulacionModelo | None:
        fila = conn.execute(
            f"{_SQL_SELECT} WHERE id = ?", (str(entidad_id),)
        ).fetchone()
        return _fila_a_postulacion(fila) if fila else None

    def obtener_todos(self, conn: sqlite3.Connection) -> list[PostulacionModelo]:
        filas = conn.execute(f"{_SQL_SELECT} ORDER BY rowid").fetchall()
        return [_fila_a_postulacion(fila) for fila in filas]

    def obtener_por_contrato(
        self, conn: sqlite3.Connection, contrato_id: UUID
    ) -> list[PostulacionModelo]:
        filas = conn.execute(
            f"{_SQL_SELECT} WHERE carga_id = ? ORDER BY rowid", (str(contrato_id),)
        ).fetchall()
        return [_fila_a_postulacion(fila) for fila in filas]

    def obtener_por_transportista(
        self, conn: sqlite3.Connection, transportista_id: UUID
    ) -> list[PostulacionModelo]:
        filas = conn.execute(
            f"{_SQL_SELECT} WHERE transportista_id = ? ORDER BY rowid",
            (str(transportista_id),),
        ).fetchall()
        return [_fila_a_postulacion(fila) for fila in filas]

    def existe_para_contrato(self, conn: sqlite3.Connection, contrato_id: UUID) -> bool:
        fila = conn.execute(
            "SELECT 1 FROM postulaciones WHERE carga_id = ? LIMIT 1",
            (str(contrato_id),),
        ).fetchone()
        return fila is not None

    def guardar(
        self, conn: sqlite3.Connection, entidad: PostulacionModelo
    ) -> PostulacionModelo:
        conn.execute(_SQL_GUARDAR, _a_parametros(entidad))
        return entidad

    def actualizar(
        self, conn: sqlite3.Connection, entidad_id: UUID, entidad: PostulacionModelo
    ) -> PostulacionModelo | None:
        cursor = conn.execute(
            _SQL_ACTUALIZAR, (*_a_parametros(entidad)[1:], str(entidad_id))
        )
        return entidad if cursor.rowcount > 0 else None

    def actualizar_estado(
        self,
        conn: sqlite3.Connection,
        postulacion_id: UUID,
        estado: EstadoPostulacion,
    ) -> None:
        conn.execute(
            "UPDATE postulaciones SET estado = ? WHERE id = ?",
            (EstadoPostulacion(estado).value, str(postulacion_id)),
        )

    def rechazar_competidoras(
        self, conn: sqlite3.Connection, contrato_id: UUID, ganadora_id: UUID
    ) -> None:
        conn.execute(
            "UPDATE postulaciones SET estado = ? "
            "WHERE carga_id = ? AND id != ? AND estado != ?",
            (
                EstadoPostulacion.RECHAZADA.value,
                str(contrato_id),
                str(ganadora_id),
                EstadoPostulacion.RECHAZADA.value,
            ),
        )
