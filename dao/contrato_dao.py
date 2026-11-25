"""DAO de la entidad Contrato (tabla ``contratos`` en SQLite)."""

from __future__ import annotations

import sqlite3
from abc import abstractmethod
from datetime import datetime
from uuid import UUID

from dao.base_dao import BaseDAO, DAOSQLite
from domain.maquina_estados import EstadoContrato
from domain.modelos import ContratoModelo, Moneda, TipoCarga

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

_SQL_SELECT = f"SELECT {', '.join(_COLUMNAS_CONTRATO)} FROM contratos"

_SQL_GUARDAR = (
    f"INSERT INTO contratos ({', '.join(_COLUMNAS_CONTRATO)}) "
    f"VALUES ({', '.join(':' + c for c in _COLUMNAS_CONTRATO)}) "
    "ON CONFLICT(id) DO UPDATE SET "
    + ", ".join(f"{c} = excluded.{c}" for c in _COLUMNAS_CONTRATO if c != "id")
)

_SQL_ACTUALIZAR = (
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


class ContratoDAO(BaseDAO[ContratoModelo, UUID]):
    """Interfaz abstracta de persistencia de contratos."""

    @abstractmethod
    def obtener_por_empresa(
        self, conn: sqlite3.Connection, empresa_id: UUID
    ) -> list[ContratoModelo]:
        """Retorna los contratos publicados por una empresa generadora."""


class ContratoDAOSQLite(DAOSQLite, ContratoDAO):
    """Persistencia de contratos en SQLite. Ignora los contratos dados de baja."""

    def obtener_por_id(
        self, conn: sqlite3.Connection, entidad_id: UUID
    ) -> ContratoModelo | None:
        fila = conn.execute(
            f"{_SQL_SELECT} WHERE id = ? AND eliminado = 0", (str(entidad_id),)
        ).fetchone()
        return _fila_a_contrato(fila) if fila else None

    def obtener_todos(self, conn: sqlite3.Connection) -> list[ContratoModelo]:
        filas = conn.execute(
            f"{_SQL_SELECT} WHERE eliminado = 0 ORDER BY rowid"
        ).fetchall()
        return [_fila_a_contrato(fila) for fila in filas]

    def obtener_por_empresa(
        self, conn: sqlite3.Connection, empresa_id: UUID
    ) -> list[ContratoModelo]:
        filas = conn.execute(
            f"{_SQL_SELECT} WHERE id_empresa_generadora = ? AND eliminado = 0 "
            "ORDER BY rowid",
            (str(empresa_id),),
        ).fetchall()
        return [_fila_a_contrato(fila) for fila in filas]

    def guardar(
        self, conn: sqlite3.Connection, entidad: ContratoModelo
    ) -> ContratoModelo:
        conn.execute(_SQL_GUARDAR, _contrato_a_parametros(entidad))
        return entidad

    def actualizar(
        self, conn: sqlite3.Connection, entidad_id: UUID, entidad: ContratoModelo
    ) -> ContratoModelo | None:
        parametros = _contrato_a_parametros(entidad)
        parametros["id"] = str(entidad_id)
        cursor = conn.execute(_SQL_ACTUALIZAR, parametros)
        return entidad if cursor.rowcount > 0 else None
