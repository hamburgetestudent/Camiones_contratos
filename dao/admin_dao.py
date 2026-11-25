"""DAO de administración y auditoría (consultas de panel y tabla ``acciones_admin``)."""

from __future__ import annotations

import json
import sqlite3
from abc import ABC, abstractmethod
from datetime import date, timedelta
from typing import Any, Literal

from dao.base_dao import DAOSQLite

TipoElemento = Literal["contrato", "cuenta"]

# Solo consultas conocidas pueden elegir tablas y columnas. Nunca se lee el hash.
_CONSULTAS: dict[TipoElemento, str] = {
    "contrato": "SELECT * FROM contratos",
    "cuenta": "SELECT id, nombre, email, rol, estado, eliminado FROM usuarios",
}


def _fila_a_evento(fila: sqlite3.Row) -> dict[str, Any]:
    return dict(
        dict(fila),
        anterior=json.loads(fila["anterior"]),
        posterior=json.loads(fila["posterior"]),
    )


class AdminDAO(ABC):
    """Contrato de persistencia para el panel administrativo y su auditoría."""

    @abstractmethod
    def listar_elementos(
        self,
        conn: sqlite3.Connection,
        tipo: TipoElemento,
        incluir_eliminados: bool = False,
        estado: str | None = None,
    ) -> list[dict[str, Any]]:
        """Lista contratos o cuentas visibles para backoffice."""

    @abstractmethod
    def obtener_actor_vigente(
        self, conn: sqlite3.Connection, actor_id: str
    ) -> dict[str, Any] | None:
        """Retorna nombre y rol del actor si su cuenta sigue vigente (no eliminada)."""

    @abstractmethod
    def obtener_elemento_por_id(
        self, conn: sqlite3.Connection, tipo: TipoElemento, elemento_id: str
    ) -> dict[str, Any] | None:
        """Retorna el contrato o cuenta administrativa por su identificador."""

    @abstractmethod
    def marcar_eliminado(
        self, conn: sqlite3.Connection, tipo: TipoElemento, elemento_id: str
    ) -> None:
        """Aplica baja lógica (``eliminado = 1``) al elemento indicado."""

    @abstractmethod
    def registrar_accion(
        self,
        conn: sqlite3.Connection,
        *,
        operacion_id: str,
        fecha_iso: str,
        administrador_id: str,
        administrador: str,
        accion: str,
        tipo: TipoElemento,
        elemento_id: str,
        motivo: str,
        anterior: dict[str, Any] | None,
        posterior: dict[str, Any] | None,
        resultado: str,
        causa: str | None,
    ) -> None:
        """Inserta un registro de auditoría en ``acciones_admin``."""

    @abstractmethod
    def listar_historial(
        self,
        conn: sqlite3.Connection,
        *,
        desde: date | None = None,
        hasta: date | None = None,
        administrador: Any = None,
        accion: Any = None,
        resultado: Any = None,
        tipo: Any = None,
        elemento_id: Any = None,
    ) -> list[dict[str, Any]]:
        """Consulta el historial de auditoría aplicando filtros opcionales."""

    @abstractmethod
    def obtener_resumen(
        self, conn: sqlite3.Connection, hoy: date
    ) -> dict[str, Any]:
        """Obtiene los indicadores y los 10 eventos recientes en una sola instantánea."""


class AdminDAOSQLite(DAOSQLite, AdminDAO):
    """Implementación SQLite del DAO administrativo."""

    def listar_elementos(
        self,
        conn: sqlite3.Connection,
        tipo: TipoElemento,
        incluir_eliminados: bool = False,
        estado: str | None = None,
    ) -> list[dict[str, Any]]:
        sql = _CONSULTAS[tipo] + " WHERE (? OR eliminado = 0)"
        valores: list[Any] = [incluir_eliminados]
        if estado:
            sql += " AND estado = ?"
            valores.append(estado)
        return [
            dict(fila)
            for fila in conn.execute(sql + " ORDER BY rowid DESC", valores)
        ]

    def obtener_actor_vigente(
        self, conn: sqlite3.Connection, actor_id: str
    ) -> dict[str, Any] | None:
        fila = conn.execute(
            "SELECT nombre, rol FROM usuarios WHERE id = ? AND eliminado = 0",
            (actor_id,),
        ).fetchone()
        return dict(fila) if fila else None

    def obtener_elemento_por_id(
        self, conn: sqlite3.Connection, tipo: TipoElemento, elemento_id: str
    ) -> dict[str, Any] | None:
        fila = conn.execute(
            _CONSULTAS[tipo] + " WHERE id = ?",
            (elemento_id,),
        ).fetchone()
        return dict(fila) if fila else None

    def marcar_eliminado(
        self, conn: sqlite3.Connection, tipo: TipoElemento, elemento_id: str
    ) -> None:
        tabla = "contratos" if tipo == "contrato" else "usuarios"
        conn.execute(
            f"UPDATE {tabla} SET eliminado = 1 WHERE id = ?", (elemento_id,)
        )

    def registrar_accion(
        self,
        conn: sqlite3.Connection,
        *,
        operacion_id: str,
        fecha_iso: str,
        administrador_id: str,
        administrador: str,
        accion: str,
        tipo: TipoElemento,
        elemento_id: str,
        motivo: str,
        anterior: dict[str, Any] | None,
        posterior: dict[str, Any] | None,
        resultado: str,
        causa: str | None,
    ) -> None:
        conn.execute(
            """INSERT INTO acciones_admin
            (id, fecha, administrador_id, administrador, accion, tipo, elemento_id,
             motivo, anterior, posterior, resultado, causa) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                operacion_id,
                fecha_iso,
                administrador_id,
                administrador,
                accion,
                tipo,
                elemento_id,
                motivo,
                json.dumps(anterior),
                json.dumps(posterior),
                resultado,
                causa,
            ),
        )

    def listar_historial(
        self,
        conn: sqlite3.Connection,
        *,
        desde: date | None = None,
        hasta: date | None = None,
        administrador: Any = None,
        accion: Any = None,
        resultado: Any = None,
        tipo: Any = None,
        elemento_id: Any = None,
    ) -> list[dict[str, Any]]:
        condiciones: list[str] = []
        valores: list[Any] = []
        for campo, valor in (
            ("accion", accion),
            ("resultado", resultado),
            ("tipo", tipo),
            ("elemento_id", elemento_id),
        ):
            if valor:
                condiciones.append(f"{campo} = ?")
                valores.append(str(valor))
        if administrador:
            condiciones.append(
                "(instr(lower(administrador), lower(?)) > 0 OR administrador_id = ?)"
            )
            valores.extend([administrador, administrador])
        if desde:
            condiciones.append("fecha >= ?")
            valores.append(desde.isoformat())
        if hasta:
            condiciones.append("substr(fecha,1,10) <= ?")
            valores.append(hasta.isoformat())
        where = " WHERE " + " AND ".join(condiciones) if condiciones else ""
        filas = conn.execute(
            "SELECT * FROM acciones_admin" + where + " ORDER BY fecha DESC, rowid DESC",
            valores,
        )
        return [_fila_a_evento(fila) for fila in filas]

    def obtener_resumen(
        self, conn: sqlite3.Connection, hoy: date
    ) -> dict[str, Any]:
        """Una sola instantánea mantiene coherentes los indicadores y los últimos eventos."""
        conn.execute("BEGIN")
        return {
            "publicados": conn.execute(
                "SELECT count(*) FROM contratos WHERE estado='PUBLICADO' AND eliminado=0"
            ).fetchone()[0],
            "activas": conn.execute(
                "SELECT count(*) FROM usuarios WHERE eliminado=0"
            ).fetchone()[0],
            "hoy": hoy.isoformat(),
            "acciones": conn.execute(
                "SELECT count(*) FROM acciones_admin WHERE resultado='Completado' AND fecha >= ? AND fecha < ?",
                (hoy.isoformat(), (hoy + timedelta(days=1)).isoformat()),
            ).fetchone()[0],
            "recientes": [
                _fila_a_evento(f)
                for f in conn.execute(
                    "SELECT * FROM acciones_admin ORDER BY fecha DESC, rowid DESC LIMIT 10"
                )
            ],
        }
