"""Servicio de negocio para la gestion del ciclo de vida de los Contratos.

Orquesta los modelos de dominio y la maquina de estados, y persiste directamente
en SQLite (tabla ``contratos``) mediante ``database.conexion``.

Las funciones de lectura/escritura de la tabla ``contratos`` (``buscar_contrato``,
``guardar_contrato``, etc.) reciben una conexion abierta para que otros servicios
(p. ej. subastas) puedan combinarlas con sus propias consultas dentro de una
misma transaccion.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from uuid import UUID

from database.conexion import obtener_conexion, transaccion_exclusiva
from domain.maquina_estados import EstadoContrato, MaquinaEstadosContrato
from domain.modelos import ContratoCrear, ContratoModelo, Moneda, TipoCarga
from services.onboarding_service import OnboardingService

# ---------------------------------------------------------------------------
# SQL de la tabla ``contratos``
# ---------------------------------------------------------------------------

_COLUMNAS_CONTRATO = (
    "id",
    "id_empresa_generadora",
    "origen",
    "destino",
    "f_estimada_salida",
    "f_estimada_llegada",
    "f_cierre_postulaciones",
    "input_camion_kg",
    "tipo_carga",
    "peso_total",
    "volumen_m3",
    "distancia_km",
    "requiere_termo",
    "numero_onu",
    "req_embalaje",
    "req_blindaje",
    "moneda",
    "monto_neto",
    "monto_iva",
    "monto_total",
    "estado",
    "id_transportista",
    "id_camion",
    "fecha_publicacion",
)

_SQL_SELECT_CONTRATO = f"SELECT {', '.join(_COLUMNAS_CONTRATO)} FROM contratos"

_SQL_GUARDAR_CONTRATO = (
    f"INSERT INTO contratos ({', '.join(_COLUMNAS_CONTRATO)}) "
    f"VALUES ({', '.join(':' + c for c in _COLUMNAS_CONTRATO)}) "
    "ON CONFLICT(id) DO UPDATE SET "
    + ", ".join(f"{c} = excluded.{c}" for c in _COLUMNAS_CONTRATO if c != "id")
)

_SQL_ACTUALIZAR_CONTRATO = (
    "UPDATE contratos SET "
    + ", ".join(f"{c} = :{c}" for c in _COLUMNAS_CONTRATO if c != "id")
    + " WHERE id = :id"
)


def _a_texto(valor: UUID | datetime | None) -> str | None:
    """Serializa UUID y fechas a TEXT (los None se almacenan como NULL)."""
    if valor is None:
        return None
    if isinstance(valor, datetime):
        return valor.isoformat()
    return str(valor)


def _contrato_a_parametros(contrato: ContratoModelo) -> dict[str, object]:
    """Convierte un ContratoModelo en los parametros nombrados de las sentencias SQL."""
    return {
        "id": str(contrato.id),
        "id_empresa_generadora": str(contrato.id_empresa_generadora),
        "origen": contrato.origen,
        "destino": contrato.destino,
        "f_estimada_salida": _a_texto(contrato.f_estimada_salida),
        "f_estimada_llegada": _a_texto(contrato.f_estimada_llegada),
        "f_cierre_postulaciones": _a_texto(contrato.f_cierre_postulaciones),
        "input_camion_kg": contrato.input_camionKG,
        "tipo_carga": TipoCarga(contrato.tipo_carga).value,
        "peso_total": contrato.peso_total,
        "volumen_m3": contrato.volumen_m3,
        "distancia_km": contrato.distancia_km,
        "requiere_termo": int(contrato.requiere_termo),
        "numero_onu": contrato.numero_onu,
        "req_embalaje": contrato.req_embalaje,
        "req_blindaje": int(contrato.req_blindaje),
        "moneda": Moneda(contrato.moneda).value,
        "monto_neto": contrato.monto_neto,
        "monto_iva": contrato.monto_iva,
        "monto_total": contrato.monto_total,
        "estado": EstadoContrato(contrato.estado).value,
        "id_transportista": _a_texto(contrato.id_transportista),
        "id_camion": _a_texto(contrato.id_camion),
        "fecha_publicacion": _a_texto(contrato.fecha_publicacion),
    }


def _fila_a_contrato(fila: sqlite3.Row) -> ContratoModelo:
    """Reconstruye un ContratoModelo desde una fila de la tabla ``contratos``.

    Usa ``model_construct`` a proposito: los datos ya fueron validados al crearse
    y revalidarlos ahora rechazaria contratos antiguos (p. ej. por la regla de
    anticipacion minima de salida, que depende de la hora actual).
    """
    return ContratoModelo.model_construct(
        id=UUID(fila["id"]),
        id_empresa_generadora=UUID(fila["id_empresa_generadora"]),
        origen=fila["origen"],
        destino=fila["destino"],
        f_estimada_salida=datetime.fromisoformat(fila["f_estimada_salida"]),
        f_estimada_llegada=datetime.fromisoformat(fila["f_estimada_llegada"]),
        f_cierre_postulaciones=datetime.fromisoformat(fila["f_cierre_postulaciones"]),
        input_camionKG=fila["input_camion_kg"],
        tipo_carga=TipoCarga(fila["tipo_carga"]),
        peso_total=fila["peso_total"],
        volumen_m3=fila["volumen_m3"],
        distancia_km=fila["distancia_km"],
        requiere_termo=bool(fila["requiere_termo"]),
        numero_onu=fila["numero_onu"],
        req_embalaje=fila["req_embalaje"],
        req_blindaje=bool(fila["req_blindaje"]),
        moneda=Moneda(fila["moneda"]),
        monto_neto=fila["monto_neto"],
        monto_iva=fila["monto_iva"],
        monto_total=fila["monto_total"],
        estado=EstadoContrato(fila["estado"]),
        id_transportista=(
            UUID(fila["id_transportista"]) if fila["id_transportista"] else None
        ),
        id_camion=UUID(fila["id_camion"]) if fila["id_camion"] else None,
        fecha_publicacion=(
            datetime.fromisoformat(fila["fecha_publicacion"])
            if fila["fecha_publicacion"]
            else None
        ),
    )


def buscar_contrato(
    conn: sqlite3.Connection, contrato_id: UUID
) -> ContratoModelo | None:
    """Obtiene un contrato por su ID, o None si no existe."""
    fila = conn.execute(
        f"{_SQL_SELECT_CONTRATO} WHERE id = ?", (str(contrato_id),)
    ).fetchone()
    return _fila_a_contrato(fila) if fila else None


def buscar_todos_los_contratos(conn: sqlite3.Connection) -> list[ContratoModelo]:
    """Retorna todos los contratos en orden de insercion."""
    filas = conn.execute(f"{_SQL_SELECT_CONTRATO} ORDER BY rowid").fetchall()
    return [_fila_a_contrato(fila) for fila in filas]


def guardar_contrato(
    conn: sqlite3.Connection, contrato: ContratoModelo
) -> ContratoModelo:
    """Inserta el contrato o, si su ID ya existe, reemplaza todos sus campos."""
    conn.execute(_SQL_GUARDAR_CONTRATO, _contrato_a_parametros(contrato))
    return contrato


def actualizar_contrato(
    conn: sqlite3.Connection, contrato_id: UUID, contrato: ContratoModelo
) -> ContratoModelo | None:
    """Actualiza un contrato existente. Retorna None si el ID no existe."""
    parametros = _contrato_a_parametros(contrato)
    parametros["id"] = str(contrato_id)
    cursor = conn.execute(_SQL_ACTUALIZAR_CONTRATO, parametros)
    return contrato if cursor.rowcount > 0 else None


# ---------------------------------------------------------------------------
# Servicio
# ---------------------------------------------------------------------------


class ServicioContrato:
    """Servicio que encapsula los casos de uso principales de Contratos."""

    def __init__(
        self,
        db_path: str | Path | None = None,
        onboarding_service: OnboardingService | None = None,
    ) -> None:
        """Crea el servicio.

        Args:
            db_path: Archivo SQLite a usar. Si es None se usa ``DEFAULT_DB_PATH``.
            onboarding_service: Servicio de KYC. Si es None se crea uno sobre la misma base.
        """
        self._db_path = db_path
        self.onboarding_service = onboarding_service or OnboardingService(
            db_path=db_path
        )

    def crear_contrato(self, datos: ContratoCrear) -> ContratoModelo:
        """Crea un nuevo contrato en estado BORRADOR y lo persiste en SQLite.

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
        with obtener_conexion(self._db_path) as conn:
            return guardar_contrato(conn, nuevo_contrato)

    def obtener_contrato(self, contrato_id: UUID) -> ContratoModelo:
        """Recupera un contrato por su ID unico. Lanza ValueError si no existe."""
        with obtener_conexion(self._db_path) as conn:
            contrato = buscar_contrato(conn, contrato_id)
        if not contrato:
            raise ValueError(f"El contrato con ID {contrato_id} no fue encontrado")
        return contrato

    def listar_contratos(self) -> list[ContratoModelo]:
        """Obtiene la lista completa de todos los contratos registrados."""
        with obtener_conexion(self._db_path) as conn:
            return buscar_todos_los_contratos(conn)

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
        with transaccion_exclusiva(self._db_path) as conn:
            contrato = buscar_contrato(conn, contrato_id)
            if not contrato:
                raise ValueError(f"El contrato con ID {contrato_id} no fue encontrado")

            contrato_actualizado = MaquinaEstadosContrato.cambiar_estado(
                contrato_data=contrato,
                nuevo_estado=nuevo_estado,
                id_transportista=id_transportista,
                id_camion=id_camion,
            )
            actualizar_contrato(conn, contrato_id, contrato_actualizado)
        return contrato_actualizado


# Alias para retrocompatibilidad
ContratoService = ServicioContrato
