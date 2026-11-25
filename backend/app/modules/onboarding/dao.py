"""DAO del modulo de onboarding: documentos de transportista y perfiles de dador."""

from __future__ import annotations

import sqlite3
from abc import abstractmethod
from datetime import datetime
from uuid import UUID

from app.db.base_dao import BaseDAO, DAOSQLite
from app.modules.onboarding.models import (
    DadorCarga,
    DatosFacturacion,
    DocumentoTransportista,
    EstadoValidacion,
    TipoDocumento,
)

# ---------------------------------------------------------------------------
# Documentos de transportista
# ---------------------------------------------------------------------------

_SELECT_DOCUMENTO = (
    "SELECT id, user_id, tipo, archivo, estado, created_at "
    "FROM documentos_transportista"
)

_SQL_GUARDAR_DOCUMENTO = """
    INSERT INTO documentos_transportista (id, user_id, tipo, archivo, estado, created_at)
    VALUES (?, ?, ?, ?, ?, ?)
    ON CONFLICT(id) DO UPDATE SET
        archivo = excluded.archivo,
        estado = excluded.estado,
        created_at = excluded.created_at
"""


def _fila_a_documento(fila: sqlite3.Row) -> DocumentoTransportista:
    return DocumentoTransportista(
        id=UUID(fila["id"]),
        user_id=UUID(fila["user_id"]),
        tipo=TipoDocumento(fila["tipo"]),
        archivo=fila["archivo"],
        estado=EstadoValidacion(fila["estado"]),
        created_at=datetime.fromisoformat(fila["created_at"]),
    )


class DocumentoDAO(BaseDAO[DocumentoTransportista, UUID]):
    """Interfaz abstracta de persistencia de documentos de habilitacion."""

    @abstractmethod
    def obtener_por_usuario_y_tipo(
        self, conn: sqlite3.Connection, user_id: UUID, tipo: TipoDocumento
    ) -> DocumentoTransportista | None:
        """Documento de un tipo concreto cargado por el usuario."""

    @abstractmethod
    def obtener_por_usuario(
        self, conn: sqlite3.Connection, user_id: UUID
    ) -> list[DocumentoTransportista]:
        """Documentos del usuario en orden de carga."""

    @abstractmethod
    def obtener_por_estado(
        self, conn: sqlite3.Connection, estado: EstadoValidacion
    ) -> list[DocumentoTransportista]:
        """Documentos en un estado de validacion dado, del mas antiguo al mas nuevo."""


class DocumentoDAOSQLite(DAOSQLite, DocumentoDAO):
    """Persistencia de documentos de transportista en SQLite."""

    def obtener_por_id(
        self, conn: sqlite3.Connection, entidad_id: UUID
    ) -> DocumentoTransportista | None:
        fila = conn.execute(
            f"{_SELECT_DOCUMENTO} WHERE id = ?", (str(entidad_id),)
        ).fetchone()
        return _fila_a_documento(fila) if fila else None

    def obtener_todos(self, conn: sqlite3.Connection) -> list[DocumentoTransportista]:
        filas = conn.execute(
            f"{_SELECT_DOCUMENTO} ORDER BY created_at ASC, rowid ASC"
        ).fetchall()
        return [_fila_a_documento(fila) for fila in filas]

    def obtener_por_usuario_y_tipo(
        self, conn: sqlite3.Connection, user_id: UUID, tipo: TipoDocumento
    ) -> DocumentoTransportista | None:
        fila = conn.execute(
            f"{_SELECT_DOCUMENTO} WHERE user_id = ? AND tipo = ?",
            (str(user_id), TipoDocumento(tipo).value),
        ).fetchone()
        return _fila_a_documento(fila) if fila else None

    def obtener_por_usuario(
        self, conn: sqlite3.Connection, user_id: UUID
    ) -> list[DocumentoTransportista]:
        filas = conn.execute(
            f"{_SELECT_DOCUMENTO} WHERE user_id = ? ORDER BY created_at ASC, rowid ASC",
            (str(user_id),),
        ).fetchall()
        return [_fila_a_documento(fila) for fila in filas]

    def obtener_por_estado(
        self, conn: sqlite3.Connection, estado: EstadoValidacion
    ) -> list[DocumentoTransportista]:
        filas = conn.execute(
            f"{_SELECT_DOCUMENTO} WHERE estado = ? ORDER BY created_at ASC, rowid ASC",
            (EstadoValidacion(estado).value,),
        ).fetchall()
        return [_fila_a_documento(fila) for fila in filas]

    def guardar(
        self, conn: sqlite3.Connection, entidad: DocumentoTransportista
    ) -> DocumentoTransportista:
        conn.execute(
            _SQL_GUARDAR_DOCUMENTO,
            (
                str(entidad.id),
                str(entidad.user_id),
                TipoDocumento(entidad.tipo).value,
                entidad.archivo,
                EstadoValidacion(entidad.estado).value,
                entidad.created_at.isoformat(),
            ),
        )
        return entidad

    def actualizar(
        self,
        conn: sqlite3.Connection,
        entidad_id: UUID,
        entidad: DocumentoTransportista,
    ) -> DocumentoTransportista | None:
        cursor = conn.execute(
            "UPDATE documentos_transportista SET archivo = ?, estado = ?, "
            "created_at = ? WHERE id = ?",
            (
                entidad.archivo,
                EstadoValidacion(entidad.estado).value,
                entidad.created_at.isoformat(),
                str(entidad_id),
            ),
        )
        return entidad if cursor.rowcount > 0 else None


# ---------------------------------------------------------------------------
# Perfiles de dador de carga
# ---------------------------------------------------------------------------

_SELECT_DADOR = (
    "SELECT id, user_id, rut_id_empresa, razon_social, direccion, "
    "correo_facturacion, estado_validacion FROM dadores_carga"
)

_SQL_GUARDAR_DADOR = """
    INSERT INTO dadores_carga (
        id, user_id, rut_id_empresa, razon_social, direccion,
        correo_facturacion, estado_validacion
    )
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(id) DO UPDATE SET
        rut_id_empresa = excluded.rut_id_empresa,
        razon_social = excluded.razon_social,
        direccion = excluded.direccion,
        correo_facturacion = excluded.correo_facturacion,
        estado_validacion = excluded.estado_validacion
"""


def _fila_a_dador(fila: sqlite3.Row) -> DadorCarga:
    return DadorCarga(
        id=UUID(fila["id"]),
        user_id=UUID(fila["user_id"]),
        rut_id_empresa=fila["rut_id_empresa"],
        datos_facturacion=DatosFacturacion(
            razon_social=fila["razon_social"],
            direccion=fila["direccion"],
            correo_facturacion=fila["correo_facturacion"],
        ),
        estado_validacion=EstadoValidacion(fila["estado_validacion"]),
    )


class DadorCargaDAO(BaseDAO[DadorCarga, UUID]):
    """Interfaz abstracta de persistencia de perfiles tributarios de dadores."""

    @abstractmethod
    def obtener_por_usuario(
        self, conn: sqlite3.Connection, user_id: UUID
    ) -> DadorCarga | None:
        """Perfil asociado a un usuario."""

    @abstractmethod
    def obtener_por_estado(
        self, conn: sqlite3.Connection, estado: EstadoValidacion
    ) -> list[DadorCarga]:
        """Perfiles en un estado de validacion dado."""


class DadorCargaDAOSQLite(DAOSQLite, DadorCargaDAO):
    """Persistencia de perfiles de dador de carga en SQLite."""

    def obtener_por_id(
        self, conn: sqlite3.Connection, entidad_id: UUID
    ) -> DadorCarga | None:
        fila = conn.execute(
            f"{_SELECT_DADOR} WHERE id = ?", (str(entidad_id),)
        ).fetchone()
        return _fila_a_dador(fila) if fila else None

    def obtener_todos(self, conn: sqlite3.Connection) -> list[DadorCarga]:
        filas = conn.execute(f"{_SELECT_DADOR} ORDER BY rowid ASC").fetchall()
        return [_fila_a_dador(fila) for fila in filas]

    def obtener_por_usuario(
        self, conn: sqlite3.Connection, user_id: UUID
    ) -> DadorCarga | None:
        fila = conn.execute(
            f"{_SELECT_DADOR} WHERE user_id = ?", (str(user_id),)
        ).fetchone()
        return _fila_a_dador(fila) if fila else None

    def obtener_por_estado(
        self, conn: sqlite3.Connection, estado: EstadoValidacion
    ) -> list[DadorCarga]:
        filas = conn.execute(
            f"{_SELECT_DADOR} WHERE estado_validacion = ? ORDER BY rowid ASC",
            (EstadoValidacion(estado).value,),
        ).fetchall()
        return [_fila_a_dador(fila) for fila in filas]

    def guardar(self, conn: sqlite3.Connection, entidad: DadorCarga) -> DadorCarga:
        conn.execute(
            _SQL_GUARDAR_DADOR,
            (
                str(entidad.id),
                str(entidad.user_id),
                entidad.rut_id_empresa,
                entidad.datos_facturacion.razon_social,
                entidad.datos_facturacion.direccion,
                entidad.datos_facturacion.correo_facturacion,
                EstadoValidacion(entidad.estado_validacion).value,
            ),
        )
        return entidad

    def actualizar(
        self, conn: sqlite3.Connection, entidad_id: UUID, entidad: DadorCarga
    ) -> DadorCarga | None:
        cursor = conn.execute(
            "UPDATE dadores_carga SET rut_id_empresa = ?, razon_social = ?, "
            "direccion = ?, correo_facturacion = ?, estado_validacion = ? WHERE id = ?",
            (
                entidad.rut_id_empresa,
                entidad.datos_facturacion.razon_social,
                entidad.datos_facturacion.direccion,
                entidad.datos_facturacion.correo_facturacion,
                EstadoValidacion(entidad.estado_validacion).value,
                str(entidad_id),
            ),
        )
        return entidad if cursor.rowcount > 0 else None
