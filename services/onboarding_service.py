"""
Servicio de Negocio para el modulo de Onboarding y Verificacion de Documentacion (KYC / Fleet Compliance).

Persiste directamente en SQLite (tablas ``documentos_transportista`` y
``dadores_carga``) mediante ``database.conexion``.
"""

from __future__ import annotations

import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

from database.conexion import obtener_conexion, transaccion_exclusiva
from domain.modelos_onboarding import (
    DadorCarga,
    DatosFacturacion,
    DocumentoTransportista,
    EstadoOnboardingTransportistaDTO,
    EstadoValidacion,
    TipoDocumento,
)

DOCUMENTOS_REQUERIDOS_TRANSPORTISTA = [
    TipoDocumento.LICENCIA_CONDUCIR,
    TipoDocumento.PADRON_VEHICULO,
    TipoDocumento.REVISION_TECNICA,
    TipoDocumento.SEGURO_CARGA,
    TipoDocumento.ANTECEDENTES,
]

# ---------------------------------------------------------------------------
# SQL: documentos_transportista
# ---------------------------------------------------------------------------

_SELECT_DOCUMENTO = (
    "SELECT id, user_id, tipo, archivo, estado, created_at "
    "FROM documentos_transportista"
)


def _fila_a_documento(fila: sqlite3.Row) -> DocumentoTransportista:
    return DocumentoTransportista(
        id=UUID(fila["id"]),
        user_id=UUID(fila["user_id"]),
        tipo=TipoDocumento(fila["tipo"]),
        archivo=fila["archivo"],
        estado=EstadoValidacion(fila["estado"]),
        created_at=datetime.fromisoformat(fila["created_at"]),
    )


def _insertar_documento(
    conn: sqlite3.Connection, doc: DocumentoTransportista
) -> DocumentoTransportista:
    conn.execute(
        """
        INSERT INTO documentos_transportista (id, user_id, tipo, archivo, estado, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            str(doc.id),
            str(doc.user_id),
            TipoDocumento(doc.tipo).value,
            doc.archivo,
            EstadoValidacion(doc.estado).value,
            doc.created_at.isoformat(),
        ),
    )
    return doc


def _actualizar_documento(
    conn: sqlite3.Connection, doc: DocumentoTransportista
) -> None:
    conn.execute(
        """
        UPDATE documentos_transportista
        SET archivo = ?, estado = ?, created_at = ?
        WHERE id = ?
        """,
        (
            doc.archivo,
            EstadoValidacion(doc.estado).value,
            doc.created_at.isoformat(),
            str(doc.id),
        ),
    )


def _buscar_documento_por_id(
    conn: sqlite3.Connection, documento_id: UUID
) -> DocumentoTransportista | None:
    fila = conn.execute(
        f"{_SELECT_DOCUMENTO} WHERE id = ?", (str(documento_id),)
    ).fetchone()
    return _fila_a_documento(fila) if fila else None


def _buscar_documento_por_usuario_y_tipo(
    conn: sqlite3.Connection, user_id: UUID, tipo: TipoDocumento
) -> DocumentoTransportista | None:
    fila = conn.execute(
        f"{_SELECT_DOCUMENTO} WHERE user_id = ? AND tipo = ?",
        (str(user_id), TipoDocumento(tipo).value),
    ).fetchone()
    return _fila_a_documento(fila) if fila else None


def _buscar_documentos_por_usuario(
    conn: sqlite3.Connection, user_id: UUID
) -> list[DocumentoTransportista]:
    filas = conn.execute(
        f"{_SELECT_DOCUMENTO} WHERE user_id = ? ORDER BY created_at ASC, rowid ASC",
        (str(user_id),),
    ).fetchall()
    return [_fila_a_documento(fila) for fila in filas]


# ---------------------------------------------------------------------------
# SQL: dadores_carga
# ---------------------------------------------------------------------------

_SELECT_DADOR = (
    "SELECT id, user_id, rut_id_empresa, razon_social, direccion, "
    "correo_facturacion, estado_validacion FROM dadores_carga"
)


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


def _insertar_dador(conn: sqlite3.Connection, dador: DadorCarga) -> DadorCarga:
    conn.execute(
        """
        INSERT INTO dadores_carga (
            id, user_id, rut_id_empresa, razon_social, direccion,
            correo_facturacion, estado_validacion
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            str(dador.id),
            str(dador.user_id),
            dador.rut_id_empresa,
            dador.datos_facturacion.razon_social,
            dador.datos_facturacion.direccion,
            dador.datos_facturacion.correo_facturacion,
            EstadoValidacion(dador.estado_validacion).value,
        ),
    )
    return dador


def _actualizar_dador(conn: sqlite3.Connection, dador: DadorCarga) -> None:
    conn.execute(
        """
        UPDATE dadores_carga
        SET rut_id_empresa = ?, razon_social = ?, direccion = ?,
            correo_facturacion = ?, estado_validacion = ?
        WHERE id = ?
        """,
        (
            dador.rut_id_empresa,
            dador.datos_facturacion.razon_social,
            dador.datos_facturacion.direccion,
            dador.datos_facturacion.correo_facturacion,
            EstadoValidacion(dador.estado_validacion).value,
            str(dador.id),
        ),
    )


def _buscar_dador_por_usuario(
    conn: sqlite3.Connection, user_id: UUID
) -> DadorCarga | None:
    fila = conn.execute(
        f"{_SELECT_DADOR} WHERE user_id = ?", (str(user_id),)
    ).fetchone()
    return _fila_a_dador(fila) if fila else None


def _buscar_dador_por_id(conn: sqlite3.Connection, dador_id: UUID) -> DadorCarga | None:
    fila = conn.execute(f"{_SELECT_DADOR} WHERE id = ?", (str(dador_id),)).fetchone()
    return _fila_a_dador(fila) if fila else None


# ---------------------------------------------------------------------------
# Servicio
# ---------------------------------------------------------------------------


class OnboardingService:
    """Servicio que implementa las reglas de negocio de onboarding y validacion documental."""

    def __init__(self, db_path: str | Path | None = None) -> None:
        """Crea el servicio.

        Args:
            db_path: Archivo SQLite a usar. Si es None se usa ``DEFAULT_DB_PATH``.
        """
        self._db_path = db_path

    # =========================================
    # Operaciones del Transportista
    # =========================================

    def cargar_documento(
        self, user_id: UUID, tipo: TipoDocumento, archivo: str
    ) -> DocumentoTransportista:
        """
        Carga o actualiza un documento para el transportista.
        Si ya existe un documento del mismo tipo, se actualiza el archivo y se reinicia a PENDIENTE.
        """
        with transaccion_exclusiva(self._db_path) as conn:
            existente = _buscar_documento_por_usuario_y_tipo(conn, user_id, tipo)
            if existente:
                existente.archivo = archivo
                existente.estado = EstadoValidacion.PENDIENTE
                existente.created_at = datetime.now(UTC)
                _actualizar_documento(conn, existente)
                return existente

            nuevo_doc = DocumentoTransportista(
                user_id=user_id,
                tipo=tipo,
                archivo=archivo,
                estado=EstadoValidacion.PENDIENTE,
            )
            return _insertar_documento(conn, nuevo_doc)

    def listar_documentos_transportista(
        self, user_id: UUID
    ) -> list[DocumentoTransportista]:
        """Obtiene la lista de todos los documentos cargados por el transportista."""
        with obtener_conexion(self._db_path) as conn:
            return _buscar_documentos_por_usuario(conn, user_id)

    def obtener_estado_transportista(
        self, user_id: UUID
    ) -> EstadoOnboardingTransportistaDTO:
        """
        Calcula el estado global de onboarding del transportista:
        - APROBADO: Si y solo si los 5 documentos requeridos existen y estan todos APROBADOS.
        - RECHAZADO: Si al menos un documento cargado esta RECHAZADO.
        - PENDIENTE: En cualquier otro caso (faltan documentos o estan en revision).
        """
        documentos = self.listar_documentos_transportista(user_id)
        docs_por_tipo = {doc.tipo: doc for doc in documentos}

        # Verificar si alguno esta rechazado
        tiene_rechazados = any(
            doc.estado == EstadoValidacion.RECHAZADO for doc in documentos
        )

        # Verificar si todos los requeridos existen y estan aprobados
        todos_cargados = all(
            tipo in docs_por_tipo for tipo in DOCUMENTOS_REQUERIDOS_TRANSPORTISTA
        )
        todos_aprobados = todos_cargados and all(
            docs_por_tipo[tipo].estado == EstadoValidacion.APROBADO
            for tipo in DOCUMENTOS_REQUERIDOS_TRANSPORTISTA
        )

        if tiene_rechazados:
            estado_global = EstadoValidacion.RECHAZADO
        elif todos_aprobados:
            estado_global = EstadoValidacion.APROBADO
        else:
            estado_global = EstadoValidacion.PENDIENTE

        faltantes = [
            tipo
            for tipo in DOCUMENTOS_REQUERIDOS_TRANSPORTISTA
            if tipo not in docs_por_tipo
        ]

        return EstadoOnboardingTransportistaDTO(
            user_id=user_id,
            estado_global=estado_global,
            documentos_requeridos=DOCUMENTOS_REQUERIDOS_TRANSPORTISTA,
            documentos_cargados=documentos,
            faltantes=faltantes,
        )

    def es_transportista_aprobado(self, user_id: UUID) -> bool:
        """Verifica si el transportista tiene su onboarding completado y aprobado."""
        estado_dto = self.obtener_estado_transportista(user_id)
        return estado_dto.estado_global == EstadoValidacion.APROBADO

    # =========================================
    # Operaciones del Dador de Carga
    # =========================================

    def registrar_o_actualizar_perfil_dador(
        self,
        user_id: UUID,
        rut_id_empresa: str,
        datos_facturacion: DatosFacturacion,
    ) -> DadorCarga:
        """Registra o actualiza los datos tributarios del dador de carga, reiniciando validacion a PENDIENTE."""
        with transaccion_exclusiva(self._db_path) as conn:
            existente = _buscar_dador_por_usuario(conn, user_id)
            if existente:
                existente.rut_id_empresa = rut_id_empresa
                existente.datos_facturacion = datos_facturacion
                existente.estado_validacion = EstadoValidacion.PENDIENTE
                _actualizar_dador(conn, existente)
                return existente

            nuevo_perfil = DadorCarga(
                user_id=user_id,
                rut_id_empresa=rut_id_empresa,
                datos_facturacion=datos_facturacion,
                estado_validacion=EstadoValidacion.PENDIENTE,
            )
            return _insertar_dador(conn, nuevo_perfil)

    def obtener_perfil_dador(self, user_id: UUID) -> DadorCarga | None:
        """Obtiene el perfil del dador de carga por su UUID de usuario."""
        with obtener_conexion(self._db_path) as conn:
            return _buscar_dador_por_usuario(conn, user_id)

    def es_dador_aprobado(self, user_id: UUID) -> bool:
        """Verifica si el dador de carga cuenta con su validacion tributaria APROBADA."""
        perfil = self.obtener_perfil_dador(user_id)
        if not perfil:
            return False
        return perfil.estado_validacion == EstadoValidacion.APROBADO

    # =========================================
    # Operaciones de Backoffice / Admin
    # =========================================

    def listar_documentos_pendientes_admin(self) -> list[DocumentoTransportista]:
        """Lista todos los documentos de transportistas pendientes de revision."""
        with obtener_conexion(self._db_path) as conn:
            filas = conn.execute(
                f"{_SELECT_DOCUMENTO} WHERE estado = ? ORDER BY created_at ASC, rowid ASC",
                (EstadoValidacion.PENDIENTE.value,),
            ).fetchall()
            return [_fila_a_documento(fila) for fila in filas]

    def validar_documento(
        self, documento_id: UUID, nuevo_estado: EstadoValidacion
    ) -> DocumentoTransportista:
        """Aprueba o rechaza un documento especifico.

        Precondiciones:
            - El documento ``documento_id`` existe.
            - ``nuevo_estado`` es APROBADO o RECHAZADO (no se puede volver a PENDIENTE).

        Postcondiciones:
            - El documento queda persistido con ``nuevo_estado``.
            - El estado global del transportista se recalcula en
              ``obtener_estado_transportista``: APROBADO solo si los 5 documentos
              requeridos estan APROBADOS.

        Raises:
            ValueError: Si el documento no existe o el estado no es valido.
        """
        with transaccion_exclusiva(self._db_path) as conn:
            doc = _buscar_documento_por_id(conn, documento_id)
            if not doc:
                raise ValueError(f"No se encontro el documento con ID {documento_id}")

            if nuevo_estado not in (
                EstadoValidacion.APROBADO,
                EstadoValidacion.RECHAZADO,
            ):
                raise ValueError(
                    "El estado de validacion debe ser APROBADO o RECHAZADO"
                )

            doc.estado = nuevo_estado
            _actualizar_documento(conn, doc)
            return doc

    def listar_dadores_pendientes_admin(self) -> list[DadorCarga]:
        """Lista todos los dadores de carga pendientes de validacion tributaria."""
        with obtener_conexion(self._db_path) as conn:
            filas = conn.execute(
                f"{_SELECT_DADOR} WHERE estado_validacion = ? ORDER BY rowid ASC",
                (EstadoValidacion.PENDIENTE.value,),
            ).fetchall()
            return [_fila_a_dador(fila) for fila in filas]

    def validar_dador(
        self, dador_id: UUID, nuevo_estado: EstadoValidacion
    ) -> DadorCarga:
        """Aprueba o rechaza el perfil tributario de un dador de carga."""
        with transaccion_exclusiva(self._db_path) as conn:
            dador = _buscar_dador_por_id(conn, dador_id)
            if not dador:
                raise ValueError(f"No se encontro el perfil dador con ID {dador_id}")

            if nuevo_estado not in (
                EstadoValidacion.APROBADO,
                EstadoValidacion.RECHAZADO,
            ):
                raise ValueError(
                    "El estado de validacion debe ser APROBADO o RECHAZADO"
                )

            dador.estado_validacion = nuevo_estado
            _actualizar_dador(conn, dador)
            return dador


# Instancia compartida del servicio (usa la base de datos por defecto, resuelta en cada llamada)
onboarding_service_instancia = OnboardingService()
