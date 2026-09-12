"""Pruebas de inmutabilidad, correcciones y reconstruccion temporal."""

import sqlite3
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import uuid4

import pytest

from dao.auditoria_dao import AuditoriaDAOSQLite
from domain.auditoria import (
    AccionAuditoria,
    EntidadAuditable,
    SolicitudCorreccionAuditoria,
)
from services.auditoria_service import ServicioAuditoria


@pytest.fixture
def auditoria() -> tuple[AuditoriaDAOSQLite, ServicioAuditoria]:
    """Entrega un ledger aislado en memoria para cada prueba."""
    dao = AuditoriaDAOSQLite(":memory:")
    yield dao, ServicioAuditoria(dao)
    dao.cerrar()


def test_correccion_preserva_original_y_respeta_fecha_de_corte(
    auditoria: tuple[AuditoriaDAOSQLite, ServicioAuditoria],
) -> None:
    """La correccion solo afecta reconstrucciones posteriores a su fecha."""
    _, servicio = auditoria
    transporte_id = uuid4()
    actor_original = uuid4()
    actor_corrector = uuid4()
    fecha_original = datetime(2026, 9, 12, 10, 0, tzinfo=UTC)
    fecha_correccion = fecha_original + timedelta(hours=2)

    original = servicio.registrar_evento(
        transporte_id=transporte_id,
        entidad=EntidadAuditable.CONTRATO,
        entidad_id=transporte_id,
        accion=AccionAuditoria.CONTRATO_CREADO,
        actor_id=actor_original,
        datos={"estado": "BORRADOR", "monto_total": 100_000},
        bases_aplicadas={"iva_porcentaje": 0.19},
        ocurrido_en=fecha_original,
    )
    correccion = servicio.registrar_correccion(
        SolicitudCorreccionAuditoria(
            evento_corregido_id=original.id,
            motivo="Correccion del monto informado",
            datos_corregidos={"estado": "BORRADOR", "monto_total": 119_000},
        ),
        actor_id=actor_corrector,
        ocurrido_en=fecha_correccion,
    )

    antes = servicio.reconstruir_estado(transporte_id, fecha_original + timedelta(minutes=30))
    despues = servicio.reconstruir_estado(transporte_id, fecha_correccion + timedelta(minutes=1))
    historial = servicio.listar_eventos(transporte_id)

    assert antes.contrato == {"estado": "BORRADOR", "monto_total": 100_000}
    assert despues.contrato == {"estado": "BORRADOR", "monto_total": 119_000}
    assert len(historial) == 2
    assert historial[0].id == original.id
    assert correccion.evento_corregido_id == original.id
    assert despues.correcciones[0]["actor_id"] == str(actor_corrector)


def test_sqlite_impide_actualizar_y_eliminar_eventos(
    auditoria: tuple[AuditoriaDAOSQLite, ServicioAuditoria],
) -> None:
    """Los triggers bloquean toda mutacion destructiva sobre el ledger."""
    dao, servicio = auditoria
    transporte_id = uuid4()
    evento = servicio.registrar_evento(
        transporte_id=transporte_id,
        entidad=EntidadAuditable.CONTRATO,
        entidad_id=transporte_id,
        accion=AccionAuditoria.CONTRATO_CREADO,
        actor_id=uuid4(),
        datos={"estado": "BORRADOR"},
    )

    with pytest.raises(sqlite3.IntegrityError, match="inmutable"):
        dao._conexion.execute(
            "UPDATE eventos_auditoria SET datos_json = ? WHERE id = ?",
            ('{"estado":"ALTERADO"}', str(evento.id)),
        )
    dao._conexion.rollback()

    with pytest.raises(sqlite3.IntegrityError, match="inmutable"):
        dao._conexion.execute("DELETE FROM eventos_auditoria WHERE id = ?", (str(evento.id),))
    dao._conexion.rollback()

    assert dao.obtener_por_id(evento.id) == evento
    assert dao.verificar_integridad().integra is True


def test_verificacion_detecta_una_alteracion_forzada(
    auditoria: tuple[AuditoriaDAOSQLite, ServicioAuditoria],
) -> None:
    """La cadena SHA-256 detecta cambios incluso si se desactiva una proteccion SQL."""
    dao, servicio = auditoria
    transporte_id = uuid4()
    evento = servicio.registrar_evento(
        transporte_id=transporte_id,
        entidad=EntidadAuditable.CONTRATO,
        entidad_id=transporte_id,
        accion=AccionAuditoria.CONTRATO_CREADO,
        actor_id=uuid4(),
        datos={"estado": "BORRADOR"},
    )

    dao._conexion.execute("DROP TRIGGER auditoria_impedir_actualizacion")
    dao._conexion.execute(
        "UPDATE eventos_auditoria SET datos_json = ? WHERE id = ?",
        ('{"estado":"ALTERADO"}', str(evento.id)),
    )
    dao._conexion.commit()

    resultado = dao.verificar_integridad()
    assert resultado.integra is False
    assert resultado.primer_evento_invalido == evento.id


def test_eventos_persisten_entre_reinicios(tmp_path: Path) -> None:
    """El historial sigue disponible al cerrar y volver a abrir la aplicacion."""
    ruta = tmp_path / "auditoria.sqlite3"
    transporte_id = uuid4()
    primer_dao = AuditoriaDAOSQLite(ruta)
    evento = ServicioAuditoria(primer_dao).registrar_evento(
        transporte_id=transporte_id,
        entidad=EntidadAuditable.CONTRATO,
        entidad_id=transporte_id,
        accion=AccionAuditoria.CONTRATO_CREADO,
        actor_id=uuid4(),
        datos={"estado": "BORRADOR"},
    )
    primer_dao.cerrar()

    segundo_dao = AuditoriaDAOSQLite(ruta)
    recuperado = segundo_dao.obtener_por_id(evento.id)

    assert recuperado == evento
    assert segundo_dao.verificar_integridad().integra is True
    segundo_dao.cerrar()
