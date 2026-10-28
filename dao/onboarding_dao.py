"""Modulo DAO (En memoria y SQLite) para Onboarding y Verificacion de Documentos (KYC)."""

import sqlite3
import threading
from datetime import datetime
from pathlib import Path
from uuid import UUID

from dao.base_dao import BaseDAO
from dao.sqlite_db import DEFAULT_DB_PATH, inicializar_bd, obtener_conexion
from domain.modelos_onboarding import (
    DadorCarga,
    DatosFacturacion,
    DocumentoTransportista,
    EstadoValidacion,
    TipoDocumento,
)


class DocumentoDAOInMemory(BaseDAO[DocumentoTransportista, UUID]):
    """Repositorio en memoria para los documentos de los transportistas."""

    def __init__(self) -> None:
        self._db: dict[UUID, DocumentoTransportista] = {}

    def obtener_por_id(self, entidad_id: UUID) -> DocumentoTransportista | None:
        return self._db.get(entidad_id)

    def obtener_todos(self) -> list[DocumentoTransportista]:
        return list(self._db.values())

    def guardar(self, entidad: DocumentoTransportista) -> DocumentoTransportista:
        self._db[entidad.id] = entidad
        return entidad

    def actualizar(self, entidad_id: UUID, entidad: DocumentoTransportista) -> DocumentoTransportista | None:
        if entidad_id in self._db:
            self._db[entidad_id] = entidad
            return entidad
        return None

    def eliminar(self, entidad_id: UUID) -> bool:
        if entidad_id in self._db:
            del self._db[entidad_id]
            return True
        return False

    def existe(self, entidad_id: UUID) -> bool:
        return entidad_id in self._db

    def get_by_user_id(self, user_id: UUID) -> list[DocumentoTransportista]:
        """Obtiene todos los documentos cargados por un transportista."""
        return [doc for doc in self._db.values() if doc.user_id == user_id]

    def get_by_user_and_tipo(self, user_id: UUID, tipo: TipoDocumento) -> DocumentoTransportista | None:
        """Obtiene el documento de un tipo específico para un transportista."""
        for doc in self._db.values():
            if doc.user_id == user_id and doc.tipo == tipo:
                return doc
        return None

    def get_pendientes(self) -> list[DocumentoTransportista]:
        """Obtiene todos los documentos en estado PENDIENTE."""
        return [doc for doc in self._db.values() if doc.estado == EstadoValidacion.PENDIENTE]

    # Alias en ingles y nombres previos
    get_id = obtener_por_id
    obt_por_id = obtener_por_id
    get_all = obtener_todos
    obt_todos = obtener_todos
    save = guardar
    update = actualizar
    delete = eliminar


class DadorCargaDAOInMemory(BaseDAO[DadorCarga, UUID]):
    """Repositorio en memoria para los perfiles y datos de facturacion de dadores de carga."""

    def __init__(self) -> None:
        self._db: dict[UUID, DadorCarga] = {}

    def obtener_por_id(self, entidad_id: UUID) -> DadorCarga | None:
        return self._db.get(entidad_id)

    def obtener_todos(self) -> list[DadorCarga]:
        return list(self._db.values())

    def guardar(self, entidad: DadorCarga) -> DadorCarga:
        self._db[entidad.id] = entidad
        return entidad

    def actualizar(self, entidad_id: UUID, entidad: DadorCarga) -> DadorCarga | None:
        if entidad_id in self._db:
            self._db[entidad_id] = entidad
            return entidad
        return None

    def eliminar(self, entidad_id: UUID) -> bool:
        if entidad_id in self._db:
            del self._db[entidad_id]
            return True
        return False

    def existe(self, entidad_id: UUID) -> bool:
        return entidad_id in self._db

    def get_by_user_id(self, user_id: UUID) -> DadorCarga | None:
        """Obtiene el perfil tributario de un dador de carga por su user_id."""
        for dador in self._db.values():
            if dador.user_id == user_id:
                return dador
        return None

    def get_by_rut(self, rut_id_empresa: str) -> DadorCarga | None:
        """Obtiene el perfil dador por RUT o identificador de empresa."""
        rut_normalizado = rut_id_empresa.strip().upper().replace(".", "")
        for dador in self._db.values():
            if dador.rut_id_empresa.strip().upper().replace(".", "") == rut_normalizado:
                return dador
        return None

    def get_pendientes(self) -> list[DadorCarga]:
        """Obtiene todos los perfiles de dador de carga en estado PENDIENTE."""
        return [dador for dador in self._db.values() if dador.estado_validacion == EstadoValidacion.PENDIENTE]

    # Alias en ingles y nombres previos
    get_id = obtener_por_id
    obt_por_id = obtener_por_id
    get_all = obtener_todos
    obt_todos = obtener_todos
    save = guardar
    update = actualizar
    delete = eliminar


class DocumentoDAOSQLite(BaseDAO[DocumentoTransportista, UUID]):
    """Repositorio persistente en SQLite para los documentos de los transportistas."""

    def __init__(self, db_path: str | Path | None = None, cargar_semilla: bool = True) -> None:
        self._db_path = Path(db_path) if db_path else DEFAULT_DB_PATH
        self._lock = threading.RLock()
        inicializar_bd(self._db_path, cargar_semilla=cargar_semilla)

    @staticmethod
    def _fila_a_modelo(fila: sqlite3.Row) -> DocumentoTransportista:
        return DocumentoTransportista(
            id=UUID(fila["id"]),
            user_id=UUID(fila["user_id"]),
            tipo=TipoDocumento(fila["tipo"]),
            archivo=fila["archivo"],
            estado=EstadoValidacion(fila["estado"]),
            created_at=datetime.fromisoformat(fila["created_at"]),
        )

    def obtener_por_id(self, entidad_id: UUID) -> DocumentoTransportista | None:
        with self._lock, obtener_conexion(self._db_path) as conn:
            cursor = conn.execute(
                "SELECT id, user_id, tipo, archivo, estado, created_at FROM documentos_transportista WHERE id = ?",
                (str(entidad_id),),
            )
            fila = cursor.fetchone()
            return self._fila_a_modelo(fila) if fila else None

    def obtener_todos(self) -> list[DocumentoTransportista]:
        with self._lock, obtener_conexion(self._db_path) as conn:
            cursor = conn.execute(
                "SELECT id, user_id, tipo, archivo, estado, created_at FROM documentos_transportista ORDER BY created_at ASC"
            )
            return [self._fila_a_modelo(fila) for fila in cursor.fetchall()]

    def guardar(self, entidad: DocumentoTransportista) -> DocumentoTransportista:
        with self._lock, obtener_conexion(self._db_path) as conn:
            conn.execute(
                """
                INSERT INTO documentos_transportista (id, user_id, tipo, archivo, estado, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id, tipo) DO UPDATE SET
                    id = excluded.id,
                    archivo = excluded.archivo,
                    estado = excluded.estado,
                    created_at = excluded.created_at
                """,
                (
                    str(entidad.id),
                    str(entidad.user_id),
                    entidad.tipo.value if isinstance(entidad.tipo, TipoDocumento) else str(entidad.tipo),
                    entidad.archivo,
                    entidad.estado.value if isinstance(entidad.estado, EstadoValidacion) else str(entidad.estado),
                    entidad.created_at.isoformat(),
                ),
            )
        return entidad

    def actualizar(self, entidad_id: UUID, entidad: DocumentoTransportista) -> DocumentoTransportista | None:
        with self._lock, obtener_conexion(self._db_path) as conn:
            cursor = conn.execute(
                """
                UPDATE documentos_transportista
                SET user_id = ?, tipo = ?, archivo = ?, estado = ?, created_at = ?
                WHERE id = ?
                """,
                (
                    str(entidad.user_id),
                    entidad.tipo.value if isinstance(entidad.tipo, TipoDocumento) else str(entidad.tipo),
                    entidad.archivo,
                    entidad.estado.value if isinstance(entidad.estado, EstadoValidacion) else str(entidad.estado),
                    entidad.created_at.isoformat(),
                    str(entidad_id),
                ),
            )
            if cursor.rowcount == 0:
                return None
            return entidad

    def eliminar(self, entidad_id: UUID) -> bool:
        with self._lock, obtener_conexion(self._db_path) as conn:
            cursor = conn.execute(
                "DELETE FROM documentos_transportista WHERE id = ?",
                (str(entidad_id),),
            )
            return cursor.rowcount > 0

    def existe(self, entidad_id: UUID) -> bool:
        with self._lock, obtener_conexion(self._db_path) as conn:
            cursor = conn.execute(
                "SELECT 1 FROM documentos_transportista WHERE id = ?",
                (str(entidad_id),),
            )
            return cursor.fetchone() is not None

    def get_by_user_id(self, user_id: UUID) -> list[DocumentoTransportista]:
        """Obtiene todos los documentos cargados por un transportista desde SQLite."""
        with self._lock, obtener_conexion(self._db_path) as conn:
            cursor = conn.execute(
                "SELECT id, user_id, tipo, archivo, estado, created_at FROM documentos_transportista WHERE user_id = ? ORDER BY created_at ASC",
                (str(user_id),),
            )
            return [self._fila_a_modelo(fila) for fila in cursor.fetchall()]

    def get_by_user_and_tipo(self, user_id: UUID, tipo: TipoDocumento) -> DocumentoTransportista | None:
        """Obtiene el documento de un tipo específico para un transportista desde SQLite."""
        valor_tipo = tipo.value if isinstance(tipo, TipoDocumento) else str(tipo)
        with self._lock, obtener_conexion(self._db_path) as conn:
            cursor = conn.execute(
                "SELECT id, user_id, tipo, archivo, estado, created_at FROM documentos_transportista WHERE user_id = ? AND tipo = ?",
                (str(user_id), valor_tipo),
            )
            fila = cursor.fetchone()
            return self._fila_a_modelo(fila) if fila else None

    def get_pendientes(self) -> list[DocumentoTransportista]:
        """Obtiene todos los documentos en estado PENDIENTE desde SQLite."""
        with self._lock, obtener_conexion(self._db_path) as conn:
            cursor = conn.execute(
                "SELECT id, user_id, tipo, archivo, estado, created_at FROM documentos_transportista WHERE estado = ? ORDER BY created_at ASC",
                (EstadoValidacion.PENDIENTE.value,),
            )
            return [self._fila_a_modelo(fila) for fila in cursor.fetchall()]

    get_id = obtener_por_id
    obt_por_id = obtener_por_id
    get_all = obtener_todos
    obt_todos = obtener_todos
    save = guardar
    update = actualizar
    delete = eliminar


class DadorCargaDAOSQLite(BaseDAO[DadorCarga, UUID]):
    """Repositorio persistente en SQLite para perfiles y correos de facturación de dadores de carga."""

    def __init__(self, db_path: str | Path | None = None, cargar_semilla: bool = True) -> None:
        self._db_path = Path(db_path) if db_path else DEFAULT_DB_PATH
        self._lock = threading.RLock()
        inicializar_bd(self._db_path, cargar_semilla=cargar_semilla)

    @staticmethod
    def _fila_a_modelo(fila: sqlite3.Row) -> DadorCarga:
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

    def obtener_por_id(self, entidad_id: UUID) -> DadorCarga | None:
        with self._lock, obtener_conexion(self._db_path) as conn:
            cursor = conn.execute(
                """
                SELECT id, user_id, rut_id_empresa, razon_social, direccion, correo_facturacion, estado_validacion
                FROM dadores_carga WHERE id = ?
                """,
                (str(entidad_id),),
            )
            fila = cursor.fetchone()
            return self._fila_a_modelo(fila) if fila else None

    def obtener_todos(self) -> list[DadorCarga]:
        with self._lock, obtener_conexion(self._db_path) as conn:
            cursor = conn.execute(
                """
                SELECT id, user_id, rut_id_empresa, razon_social, direccion, correo_facturacion, estado_validacion
                FROM dadores_carga
                """
            )
            return [self._fila_a_modelo(fila) for fila in cursor.fetchall()]

    def guardar(self, entidad: DadorCarga) -> DadorCarga:
        with self._lock, obtener_conexion(self._db_path) as conn:
            conn.execute(
                """
                INSERT INTO dadores_carga (
                    id, user_id, rut_id_empresa, razon_social, direccion, correo_facturacion, estado_validacion
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    id = excluded.id,
                    rut_id_empresa = excluded.rut_id_empresa,
                    razon_social = excluded.razon_social,
                    direccion = excluded.direccion,
                    correo_facturacion = excluded.correo_facturacion,
                    estado_validacion = excluded.estado_validacion
                """,
                (
                    str(entidad.id),
                    str(entidad.user_id),
                    entidad.rut_id_empresa,
                    entidad.datos_facturacion.razon_social,
                    entidad.datos_facturacion.direccion,
                    entidad.datos_facturacion.correo_facturacion,
                    entidad.estado_validacion.value
                    if isinstance(entidad.estado_validacion, EstadoValidacion)
                    else str(entidad.estado_validacion),
                ),
            )
        return entidad

    def actualizar(self, entidad_id: UUID, entidad: DadorCarga) -> DadorCarga | None:
        with self._lock, obtener_conexion(self._db_path) as conn:
            cursor = conn.execute(
                """
                UPDATE dadores_carga
                SET user_id = ?, rut_id_empresa = ?, razon_social = ?, direccion = ?,
                    correo_facturacion = ?, estado_validacion = ?
                WHERE id = ?
                """,
                (
                    str(entidad.user_id),
                    entidad.rut_id_empresa,
                    entidad.datos_facturacion.razon_social,
                    entidad.datos_facturacion.direccion,
                    entidad.datos_facturacion.correo_facturacion,
                    entidad.estado_validacion.value
                    if isinstance(entidad.estado_validacion, EstadoValidacion)
                    else str(entidad.estado_validacion),
                    str(entidad_id),
                ),
            )
            if cursor.rowcount == 0:
                return None
            return entidad

    def eliminar(self, entidad_id: UUID) -> bool:
        with self._lock, obtener_conexion(self._db_path) as conn:
            cursor = conn.execute("DELETE FROM dadores_carga WHERE id = ?", (str(entidad_id),))
            return cursor.rowcount > 0

    def existe(self, entidad_id: UUID) -> bool:
        with self._lock, obtener_conexion(self._db_path) as conn:
            cursor = conn.execute("SELECT 1 FROM dadores_carga WHERE id = ?", (str(entidad_id),))
            return cursor.fetchone() is not None

    def get_by_user_id(self, user_id: UUID) -> DadorCarga | None:
        """Obtiene el perfil tributario de un dador de carga por su user_id desde SQLite."""
        with self._lock, obtener_conexion(self._db_path) as conn:
            cursor = conn.execute(
                """
                SELECT id, user_id, rut_id_empresa, razon_social, direccion, correo_facturacion, estado_validacion
                FROM dadores_carga WHERE user_id = ?
                """,
                (str(user_id),),
            )
            fila = cursor.fetchone()
            return self._fila_a_modelo(fila) if fila else None

    def get_by_rut(self, rut_id_empresa: str) -> DadorCarga | None:
        """Obtiene el perfil dador por RUT o identificador de empresa desde SQLite."""
        rut_normalizado = rut_id_empresa.strip().upper().replace(".", "")
        with self._lock, obtener_conexion(self._db_path) as conn:
            cursor = conn.execute(
                """
                SELECT id, user_id, rut_id_empresa, razon_social, direccion, correo_facturacion, estado_validacion
                FROM dadores_carga
                WHERE replace(upper(trim(rut_id_empresa)), '.', '') = ?
                """,
                (rut_normalizado,),
            )
            fila = cursor.fetchone()
            return self._fila_a_modelo(fila) if fila else None

    def get_pendientes(self) -> list[DadorCarga]:
        """Obtiene todos los perfiles de dador de carga en estado PENDIENTE desde SQLite."""
        with self._lock, obtener_conexion(self._db_path) as conn:
            cursor = conn.execute(
                """
                SELECT id, user_id, rut_id_empresa, razon_social, direccion, correo_facturacion, estado_validacion
                FROM dadores_carga WHERE estado_validacion = ?
                """,
                (EstadoValidacion.PENDIENTE.value,),
            )
            return [self._fila_a_modelo(fila) for fila in cursor.fetchall()]

    get_id = obtener_por_id
    obt_por_id = obtener_por_id
    get_all = obtener_todos
    obt_todos = obtener_todos
    save = guardar
    update = actualizar
    delete = eliminar

