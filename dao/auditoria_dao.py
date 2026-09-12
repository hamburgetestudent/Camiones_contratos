"""Persistencia append-only para eventos de auditoria.

SQLite permite conservar la evidencia entre reinicios sin acoplar los servicios a
un motor externo. Dos triggers impiden UPDATE y DELETE sobre el ledger.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
import threading
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Protocol
from uuid import UUID, uuid4

from pydantic import BaseModel

from domain.auditoria import (
    EventoAuditoria,
    EventoAuditoriaCrear,
    ResultadoIntegridadAuditoria,
    normalizar_fecha_utc,
)


class AuditoriaDAO(Protocol):
    """Contrato de persistencia requerido por el servicio de auditoria."""

    def registrar(self, datos_evento: EventoAuditoriaCrear) -> EventoAuditoria:
        """Anexa un evento al ledger."""
        ...

    def obtener_por_id(self, evento_id: UUID) -> EventoAuditoria | None:
        """Obtiene un evento por su identificador."""
        ...

    def listar_por_transporte(
        self,
        transporte_id: UUID,
        hasta: datetime | None = None,
    ) -> list[EventoAuditoria]:
        """Lista eventos de un transporte hasta una fecha opcional."""
        ...

    def verificar_integridad(self) -> ResultadoIntegridadAuditoria:
        """Verifica la cadena de integridad del ledger."""
        ...


class AuditoriaDAOSQLite:
    """Ledger persistente, inmutable y encadenado por transporte."""

    def __init__(self, ruta_base_datos: str | Path = "data/auditoria.sqlite3") -> None:
        self.ruta_base_datos = str(ruta_base_datos)
        if self.ruta_base_datos != ":memory:":
            Path(self.ruta_base_datos).parent.mkdir(parents=True, exist_ok=True)

        self._lock = threading.RLock()
        self._conexion = sqlite3.connect(self.ruta_base_datos, check_same_thread=False)
        self._conexion.row_factory = sqlite3.Row
        self._crear_esquema()

    def _crear_esquema(self) -> None:
        """Crea tabla, indices y protecciones de inmutabilidad."""
        with self._lock:
            self._conexion.executescript(
                """
                PRAGMA foreign_keys = ON;

                CREATE TABLE IF NOT EXISTS eventos_auditoria (
                    secuencia INTEGER PRIMARY KEY AUTOINCREMENT,
                    id TEXT NOT NULL UNIQUE,
                    transporte_id TEXT NOT NULL,
                    entidad TEXT NOT NULL,
                    entidad_id TEXT NOT NULL,
                    accion TEXT NOT NULL,
                    actor_id TEXT NOT NULL,
                    ocurrido_en TEXT NOT NULL,
                    datos_json TEXT NOT NULL,
                    bases_aplicadas_json TEXT NOT NULL,
                    informacion_utilizada_json TEXT NOT NULL,
                    evento_corregido_id TEXT,
                    motivo_correccion TEXT,
                    hash_anterior TEXT,
                    hash_evento TEXT NOT NULL UNIQUE
                );

                CREATE INDEX IF NOT EXISTS idx_auditoria_transporte_fecha
                    ON eventos_auditoria (transporte_id, ocurrido_en, secuencia);

                CREATE TRIGGER IF NOT EXISTS auditoria_impedir_actualizacion
                BEFORE UPDATE ON eventos_auditoria
                BEGIN
                    SELECT RAISE(ABORT, 'El registro de auditoria es inmutable');
                END;

                CREATE TRIGGER IF NOT EXISTS auditoria_impedir_eliminacion
                BEFORE DELETE ON eventos_auditoria
                BEGIN
                    SELECT RAISE(ABORT, 'El registro de auditoria es inmutable');
                END;
                """
            )
            self._conexion.commit()

    def registrar(self, datos_evento: EventoAuditoriaCrear) -> EventoAuditoria:
        """Anexa un evento y calcula su hash enlazado con el evento previo.

        Args:
            datos_evento: Hecho de negocio ya validado que se desea conservar.

        Returns:
            El evento persistido con UUID, secuencia y hashes de integridad.

        Raises:
            sqlite3.DatabaseError: Si SQLite no puede persistir el evento.
        """
        evento_id = uuid4()
        ocurrido_en = normalizar_fecha_utc(datos_evento.ocurrido_en)
        datos = _normalizar_json(datos_evento.datos)
        bases_aplicadas = _normalizar_json(datos_evento.bases_aplicadas)
        informacion_utilizada = _normalizar_json(datos_evento.informacion_utilizada)

        with self._lock:
            try:
                self._conexion.execute("BEGIN IMMEDIATE")
                fila_anterior = self._conexion.execute(
                    """
                    SELECT hash_evento
                    FROM eventos_auditoria
                    WHERE transporte_id = ?
                    ORDER BY secuencia DESC
                    LIMIT 1
                    """,
                    (str(datos_evento.transporte_id),),
                ).fetchone()
                hash_anterior = fila_anterior["hash_evento"] if fila_anterior else None

                material = _material_hash(
                    evento_id=evento_id,
                    datos_evento=datos_evento,
                    ocurrido_en=ocurrido_en,
                    datos=datos,
                    bases_aplicadas=bases_aplicadas,
                    informacion_utilizada=informacion_utilizada,
                    hash_anterior=hash_anterior,
                )
                hash_evento = hashlib.sha256(_serializar_canonico(material).encode("utf-8")).hexdigest()

                cursor = self._conexion.execute(
                    """
                    INSERT INTO eventos_auditoria (
                        id, transporte_id, entidad, entidad_id, accion, actor_id,
                        ocurrido_en, datos_json, bases_aplicadas_json,
                        informacion_utilizada_json, evento_corregido_id,
                        motivo_correccion, hash_anterior, hash_evento
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        str(evento_id),
                        str(datos_evento.transporte_id),
                        datos_evento.entidad.value,
                        str(datos_evento.entidad_id),
                        datos_evento.accion.value,
                        str(datos_evento.actor_id),
                        ocurrido_en.isoformat(),
                        _serializar_canonico(datos),
                        _serializar_canonico(bases_aplicadas),
                        _serializar_canonico(informacion_utilizada),
                        str(datos_evento.evento_corregido_id) if datos_evento.evento_corregido_id else None,
                        datos_evento.motivo_correccion,
                        hash_anterior,
                        hash_evento,
                    ),
                )
                secuencia = int(cursor.lastrowid)
                self._conexion.commit()
            except Exception:
                self._conexion.rollback()
                raise

        return EventoAuditoria(
            **datos_evento.model_dump(exclude={"ocurrido_en", "datos", "bases_aplicadas", "informacion_utilizada"}),
            ocurrido_en=ocurrido_en,
            datos=datos,
            bases_aplicadas=bases_aplicadas,
            informacion_utilizada=informacion_utilizada,
            secuencia=secuencia,
            id=evento_id,
            hash_anterior=hash_anterior,
            hash_evento=hash_evento,
        )

    def obtener_por_id(self, evento_id: UUID) -> EventoAuditoria | None:
        """Busca un evento por UUID sin modificar el ledger."""
        with self._lock:
            fila = self._conexion.execute(
                "SELECT * FROM eventos_auditoria WHERE id = ?",
                (str(evento_id),),
            ).fetchone()
        return self._fila_a_evento(fila) if fila else None

    def listar_por_transporte(
        self,
        transporte_id: UUID,
        hasta: datetime | None = None,
    ) -> list[EventoAuditoria]:
        """Lista cronologicamente los hechos de un transporte hasta una fecha opcional."""
        parametros: list[str] = [str(transporte_id)]
        consulta = "SELECT * FROM eventos_auditoria WHERE transporte_id = ?"
        if hasta is not None:
            consulta += " AND ocurrido_en <= ?"
            parametros.append(normalizar_fecha_utc(hasta).isoformat())
        consulta += " ORDER BY ocurrido_en ASC, secuencia ASC"

        with self._lock:
            filas = self._conexion.execute(consulta, parametros).fetchall()
        return [self._fila_a_evento(fila) for fila in filas]

    def listar_todos(self) -> list[EventoAuditoria]:
        """Retorna todos los eventos en el orden en que fueron anexados."""
        with self._lock:
            filas = self._conexion.execute("SELECT * FROM eventos_auditoria ORDER BY secuencia ASC").fetchall()
        return [self._fila_a_evento(fila) for fila in filas]

    def verificar_integridad(self) -> ResultadoIntegridadAuditoria:
        """Recalcula los hashes y comprueba cada cadena por transporte."""
        anteriores: dict[UUID, str | None] = {}
        eventos = self.listar_todos()

        for indice, evento in enumerate(eventos):
            hash_anterior_esperado = anteriores.get(evento.transporte_id)
            material = _material_hash(
                evento_id=evento.id,
                datos_evento=evento,
                ocurrido_en=evento.ocurrido_en,
                datos=evento.datos,
                bases_aplicadas=evento.bases_aplicadas,
                informacion_utilizada=evento.informacion_utilizada,
                hash_anterior=hash_anterior_esperado,
            )
            hash_esperado = hashlib.sha256(_serializar_canonico(material).encode("utf-8")).hexdigest()
            if evento.hash_anterior != hash_anterior_esperado or evento.hash_evento != hash_esperado:
                return ResultadoIntegridadAuditoria(
                    integra=False,
                    eventos_verificados=indice,
                    primer_evento_invalido=evento.id,
                )
            anteriores[evento.transporte_id] = evento.hash_evento

        return ResultadoIntegridadAuditoria(integra=True, eventos_verificados=len(eventos))

    def cerrar(self) -> None:
        """Cierra explicitamente la conexion SQLite."""
        with self._lock:
            self._conexion.close()

    @staticmethod
    def _fila_a_evento(fila: sqlite3.Row) -> EventoAuditoria:
        """Convierte una fila SQLite en un modelo validado."""
        return EventoAuditoria(
            secuencia=fila["secuencia"],
            id=UUID(fila["id"]),
            transporte_id=UUID(fila["transporte_id"]),
            entidad=fila["entidad"],
            entidad_id=UUID(fila["entidad_id"]),
            accion=fila["accion"],
            actor_id=UUID(fila["actor_id"]),
            ocurrido_en=datetime.fromisoformat(fila["ocurrido_en"]),
            datos=json.loads(fila["datos_json"]),
            bases_aplicadas=json.loads(fila["bases_aplicadas_json"]),
            informacion_utilizada=json.loads(fila["informacion_utilizada_json"]),
            evento_corregido_id=UUID(fila["evento_corregido_id"]) if fila["evento_corregido_id"] else None,
            motivo_correccion=fila["motivo_correccion"],
            hash_anterior=fila["hash_anterior"],
            hash_evento=fila["hash_evento"],
        )


def _normalizar_json(valor: Any) -> Any:
    """Transforma modelos, UUID, fechas y enums a valores JSON estables."""
    return json.loads(json.dumps(valor, default=_valor_json, ensure_ascii=False))


def _valor_json(valor: Any) -> Any:
    """Serializador de apoyo para tipos usados por el dominio."""
    if isinstance(valor, BaseModel):
        return valor.model_dump(mode="json")
    if isinstance(valor, UUID):
        return str(valor)
    if isinstance(valor, datetime):
        return normalizar_fecha_utc(valor).isoformat()
    if isinstance(valor, Enum):
        return valor.value
    raise TypeError(f"El valor de tipo {type(valor).__name__} no es serializable en auditoria")


def _serializar_canonico(valor: Any) -> str:
    """Serializa sin ambiguedades para persistencia y calculo de hashes."""
    return json.dumps(valor, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _material_hash(
    *,
    evento_id: UUID,
    datos_evento: EventoAuditoriaCrear | EventoAuditoria,
    ocurrido_en: datetime,
    datos: dict[str, Any],
    bases_aplicadas: dict[str, Any],
    informacion_utilizada: dict[str, Any],
    hash_anterior: str | None,
) -> dict[str, Any]:
    """Construye el contenido exacto protegido por el hash del evento."""
    return {
        "id": str(evento_id),
        "transporte_id": str(datos_evento.transporte_id),
        "entidad": datos_evento.entidad.value,
        "entidad_id": str(datos_evento.entidad_id),
        "accion": datos_evento.accion.value,
        "actor_id": str(datos_evento.actor_id),
        "ocurrido_en": normalizar_fecha_utc(ocurrido_en).isoformat(),
        "datos": datos,
        "bases_aplicadas": bases_aplicadas,
        "informacion_utilizada": informacion_utilizada,
        "evento_corregido_id": str(datos_evento.evento_corregido_id) if datos_evento.evento_corregido_id else None,
        "motivo_correccion": datos_evento.motivo_correccion,
        "hash_anterior": hash_anterior,
    }
