"""
Servicio de Negocio para el modulo de Onboarding y Verificacion de Documentacion (KYC / Fleet Compliance).

La persistencia se delega en ``DocumentoDAO`` y ``DadorCargaDAO`` inyectados
(por defecto sus implementaciones SQLite); el servicio no contiene SQL.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

from dao.onboarding_dao import (
    DadorCargaDAO,
    DadorCargaDAOSQLite,
    DocumentoDAO,
    DocumentoDAOSQLite,
)
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
# Servicio
# ---------------------------------------------------------------------------


class OnboardingService:
    """Servicio que implementa las reglas de negocio de onboarding y validacion documental."""

    def __init__(
        self,
        db_path: str | Path | None = None,
        documento_dao: DocumentoDAO | None = None,
        dador_dao: DadorCargaDAO | None = None,
    ) -> None:
        """Crea el servicio.

        Args:
            db_path: Archivo SQLite para los DAO que no se inyecten. Si es None se
                usa ``DEFAULT_DB_PATH``.
            documento_dao: Almacen de documentos de transportista.
            dador_dao: Almacen de perfiles de dador de carga. Ambos DAO deben
                apuntar a la misma base para compartir transaccion.
        """
        self._documentos: DocumentoDAO = documento_dao or DocumentoDAOSQLite(db_path)
        self._dadores: DadorCargaDAO = dador_dao or DadorCargaDAOSQLite(db_path)

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
        with self._documentos.transaccion() as conn:
            existente = self._documentos.obtener_por_usuario_y_tipo(conn, user_id, tipo)
            if existente:
                existente.archivo = archivo
                existente.estado = EstadoValidacion.PENDIENTE
                existente.created_at = datetime.now(UTC)
                self._documentos.guardar(conn, existente)
                return existente

            nuevo_doc = DocumentoTransportista(
                user_id=user_id,
                tipo=tipo,
                archivo=archivo,
                estado=EstadoValidacion.PENDIENTE,
            )
            return self._documentos.guardar(conn, nuevo_doc)

    def listar_documentos_transportista(
        self, user_id: UUID
    ) -> list[DocumentoTransportista]:
        """Obtiene la lista de todos los documentos cargados por el transportista."""
        with self._documentos.conexion() as conn:
            return self._documentos.obtener_por_usuario(conn, user_id)

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
        with self._dadores.transaccion() as conn:
            existente = self._dadores.obtener_por_usuario(conn, user_id)
            if existente:
                existente.rut_id_empresa = rut_id_empresa
                existente.datos_facturacion = datos_facturacion
                existente.estado_validacion = EstadoValidacion.PENDIENTE
                self._dadores.guardar(conn, existente)
                return existente

            nuevo_perfil = DadorCarga(
                user_id=user_id,
                rut_id_empresa=rut_id_empresa,
                datos_facturacion=datos_facturacion,
                estado_validacion=EstadoValidacion.PENDIENTE,
            )
            return self._dadores.guardar(conn, nuevo_perfil)

    def obtener_perfil_dador(self, user_id: UUID) -> DadorCarga | None:
        """Obtiene el perfil del dador de carga por su UUID de usuario."""
        with self._dadores.conexion() as conn:
            return self._dadores.obtener_por_usuario(conn, user_id)

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
        with self._documentos.conexion() as conn:
            return self._documentos.obtener_por_estado(conn, EstadoValidacion.PENDIENTE)

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
        with self._documentos.transaccion() as conn:
            doc = self._documentos.obtener_por_id(conn, documento_id)
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
            self._documentos.guardar(conn, doc)
            return doc

    def listar_dadores_pendientes_admin(self) -> list[DadorCarga]:
        """Lista todos los dadores de carga pendientes de validacion tributaria."""
        with self._dadores.conexion() as conn:
            return self._dadores.obtener_por_estado(conn, EstadoValidacion.PENDIENTE)

    def validar_dador(
        self, dador_id: UUID, nuevo_estado: EstadoValidacion
    ) -> DadorCarga:
        """Aprueba o rechaza el perfil tributario de un dador de carga."""
        with self._dadores.transaccion() as conn:
            dador = self._dadores.obtener_por_id(conn, dador_id)
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
            self._dadores.guardar(conn, dador)
            return dador


# Instancia compartida del servicio (usa la base de datos por defecto, resuelta en cada llamada)
onboarding_service_instancia = OnboardingService()
