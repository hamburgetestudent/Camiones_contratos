"""Servicio de negocio para la gestion del ciclo de vida de los contratos.

Orquesta los modelos de dominio y la maquina de estados. La persistencia se
delega en un ``ContratoDAO`` inyectado (por defecto ``ContratoDAOSQLite``), por
lo que el servicio no contiene SQL.
"""

from __future__ import annotations

from pathlib import Path
from uuid import UUID

from app.modules.contratos.dao import ContratoDAO, ContratoDAOSQLite
from app.modules.contratos.maquina_estados import EstadoContrato, MaquinaEstadosContrato
from app.modules.contratos.models import ContratoCrear, ContratoModelo
from app.modules.onboarding.service import OnboardingService


class ServicioContrato:
    """Servicio que encapsula los casos de uso principales de Contratos."""

    def __init__(
        self,
        db_path: str | Path | None = None,
        onboarding_service: OnboardingService | None = None,
        dao: ContratoDAO | None = None,
    ) -> None:
        """Crea el servicio.

        Args:
            db_path: Archivo SQLite a usar si no se inyecta ``dao``. Si es None se
                usa ``DEFAULT_DB_PATH``.
            onboarding_service: Servicio de KYC. Si es None se crea uno sobre la misma base.
            dao: Almacen persistente de contratos. Si es None se crea un
                ``ContratoDAOSQLite`` sobre ``db_path``.
        """
        self._dao: ContratoDAO = dao or ContratoDAOSQLite(db_path)
        self.onboarding_service = onboarding_service or OnboardingService(
            db_path=db_path
        )

    @property
    def dao(self) -> ContratoDAO:
        """DAO de contratos que usa este servicio."""
        return self._dao

    def crear_contrato(self, datos: ContratoCrear) -> ContratoModelo:
        """Crea un nuevo contrato en estado BORRADOR y lo persiste.

        Precondiciones:
            - ``datos`` ya cumple las reglas de ``ContratoBase`` (fechas, capacidad,
              requisitos por tipo de carga, coherencia financiera).
            - La empresa generadora tiene su KYC/Onboarding en estado APROBADO.

        Postcondiciones:
            - El contrato queda persistido con estado BORRADOR y un ``id`` nuevo.
            - Si la empresa no esta aprobada, no se persiste nada.

        Raises:
            PermissionError: Si el dador de carga no esta aprobado.
        """
        if not self.onboarding_service.es_dador_aprobado(datos.id_empresa_generadora):
            raise PermissionError(
                f"La empresa generadora {datos.id_empresa_generadora} no cuenta con su "
                "verificacion KYC/Onboarding en estado APROBADO."
            )

        nuevo_contrato = ContratoModelo(**datos.model_dump())
        with self._dao.conexion() as conn:
            return self._dao.guardar(conn, nuevo_contrato)

    def obtener_contrato(self, contrato_id: UUID) -> ContratoModelo:
        """Recupera un contrato por su ID unico. Lanza ValueError si no existe."""
        with self._dao.conexion() as conn:
            contrato = self._dao.obtener_por_id(conn, contrato_id)
        if not contrato:
            raise ValueError(f"El contrato con ID {contrato_id} no fue encontrado")
        return contrato

    def listar_contratos(self) -> list[ContratoModelo]:
        """Obtiene la lista completa de todos los contratos registrados."""
        with self._dao.conexion() as conn:
            return self._dao.obtener_todos(conn)

    def cambiar_estado(
        self,
        contrato_id: UUID,
        nuevo_estado: EstadoContrato,
        id_transportista: UUID | None = None,
        id_camion: UUID | None = None,
    ) -> ContratoModelo:
        """Solicita un cambio de estado evaluando las reglas de la Maquina de Estados
        y persiste los cambios aplicados.

        La lectura, la validacion y la escritura ocurren en una sola transaccion:
        si la maquina de estados rechaza la transicion, nada se modifica.
        """
        with self._dao.transaccion() as conn:
            contrato = self._dao.obtener_por_id(conn, contrato_id)
            if not contrato:
                raise ValueError(f"El contrato con ID {contrato_id} no fue encontrado")

            contrato_actualizado = MaquinaEstadosContrato.cambiar_estado(
                contrato_data=contrato,
                nuevo_estado=nuevo_estado,
                id_transportista=id_transportista,
                id_camion=id_camion,
            )
            self._dao.actualizar(conn, contrato_id, contrato_actualizado)
        return contrato_actualizado


# Alias para retrocompatibilidad
ContratoService = ServicioContrato
