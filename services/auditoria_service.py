"""Casos de uso para trazabilidad y reconstruccion de transportes."""

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from dao.auditoria_dao import AuditoriaDAO
from domain.auditoria import (
    AccionAuditoria,
    EntidadAuditable,
    EstadoTransporteHistorico,
    EventoAuditoria,
    EventoAuditoriaCrear,
    ResultadoIntegridadAuditoria,
    SolicitudCorreccionAuditoria,
    normalizar_fecha_utc,
)


class ServicioAuditoria:
    """Registra hechos inmutables y produce vistas historicas por fecha."""

    def __init__(self, dao: AuditoriaDAO) -> None:
        self.dao = dao

    def registrar_evento(
        self,
        *,
        transporte_id: UUID,
        entidad: EntidadAuditable,
        entidad_id: UUID,
        accion: AccionAuditoria,
        actor_id: UUID,
        datos: dict[str, Any],
        bases_aplicadas: dict[str, Any] | None = None,
        informacion_utilizada: dict[str, Any] | None = None,
        ocurrido_en: datetime | None = None,
    ) -> EventoAuditoria:
        """Registra un hecho con actor, fecha UTC e instantaneas de contexto.

        Args:
            transporte_id: Contrato o transporte afectado.
            entidad: Tipo de entidad que cambio.
            entidad_id: Identificador de la entidad afectada.
            accion: Hecho de negocio ejecutado.
            actor_id: Usuario responsable de la actuacion.
            datos: Estado completo de la entidad despues de la actuacion.
            bases_aplicadas: Reglas vigentes utilizadas.
            informacion_utilizada: Antecedentes considerados para actuar.
            ocurrido_en: Fecha consciente de zona horaria; usa UTC actual por defecto.

        Returns:
            Evento anexado al ledger.
        """
        evento = EventoAuditoriaCrear(
            transporte_id=transporte_id,
            entidad=entidad,
            entidad_id=entidad_id,
            accion=accion,
            actor_id=actor_id,
            ocurrido_en=ocurrido_en or datetime.now(UTC),
            datos=datos,
            bases_aplicadas=bases_aplicadas or {},
            informacion_utilizada=informacion_utilizada or {},
        )
        return self.dao.registrar(evento)

    def registrar_correccion(
        self,
        solicitud: SolicitudCorreccionAuditoria,
        actor_id: UUID,
        ocurrido_en: datetime | None = None,
    ) -> EventoAuditoria:
        """Anexa una correccion que conserva y referencia el evento original.

        Args:
            solicitud: Evento original, motivo y nueva instantanea corregida.
            actor_id: Usuario responsable de la rectificacion.
            ocurrido_en: Fecha consciente de zona horaria; usa UTC actual por defecto.

        Returns:
            Nuevo evento de tipo CORRECCION_REGISTRADA.

        Raises:
            ValueError: Si el evento original no existe.
        """
        original = self.dao.obtener_por_id(solicitud.evento_corregido_id)
        if original is None:
            raise ValueError(f"El evento {solicitud.evento_corregido_id} no existe")

        informacion = {
            **solicitud.informacion_utilizada,
            "datos_anteriores": original.datos,
            "accion_original": original.accion.value,
        }
        fecha_correccion = normalizar_fecha_utc(ocurrido_en or datetime.now(UTC))
        if fecha_correccion < original.ocurrido_en:
            raise ValueError("La correccion no puede tener una fecha anterior al evento original")

        correccion = EventoAuditoriaCrear(
            transporte_id=original.transporte_id,
            entidad=original.entidad,
            entidad_id=original.entidad_id,
            accion=AccionAuditoria.CORRECCION_REGISTRADA,
            actor_id=actor_id,
            ocurrido_en=fecha_correccion,
            datos=solicitud.datos_corregidos,
            bases_aplicadas=original.bases_aplicadas,
            informacion_utilizada=informacion,
            evento_corregido_id=original.id,
            motivo_correccion=solicitud.motivo,
        )
        return self.dao.registrar(correccion)

    def listar_eventos(
        self,
        transporte_id: UUID,
        hasta: datetime | None = None,
    ) -> list[EventoAuditoria]:
        """Obtiene la evidencia completa de un transporte hasta una fecha opcional."""
        return self.dao.listar_por_transporte(transporte_id, hasta)

    def reconstruir_estado(
        self,
        transporte_id: UUID,
        hasta: datetime | None = None,
    ) -> EstadoTransporteHistorico:
        """Reconstruye contrato, ofertas, revisiones y bases a una fecha exacta.

        Una correccion se vuelve efectiva solo desde su propia fecha. Por lo tanto,
        una consulta anterior a ella conserva el valor originalmente registrado.

        Args:
            transporte_id: Contrato o transporte que se desea reconstruir.
            hasta: Fecha de corte inclusiva. Usa el instante actual si se omite.

        Returns:
            Vista historica construida exclusivamente desde eventos inmutables.
        """
        fecha_corte = normalizar_fecha_utc(hasta or datetime.now(UTC))
        eventos = self.dao.listar_por_transporte(transporte_id, fecha_corte)

        contrato: dict[str, Any] | None = None
        ofertas: dict[UUID, dict[str, Any]] = {}
        revisiones: dict[UUID, dict[str, Any]] = {}
        decisiones: dict[UUID, dict[str, Any]] = {}
        bases: list[dict[str, Any]] = []
        correcciones: list[dict[str, Any]] = []

        for evento in eventos:
            if evento.entidad == EntidadAuditable.CONTRATO:
                contrato = evento.datos
            elif evento.entidad == EntidadAuditable.OFERTA:
                ofertas[evento.entidad_id] = evento.datos
            elif evento.entidad == EntidadAuditable.REVISION:
                revisiones[evento.entidad_id] = _resumen_actuacion(evento)
            elif evento.entidad == EntidadAuditable.DECISION:
                decisiones[evento.entidad_id] = _resumen_actuacion(evento)

            if evento.bases_aplicadas:
                bases.append(
                    {
                        "evento_id": str(evento.id),
                        "accion": evento.accion.value,
                        "ocurrido_en": evento.ocurrido_en.isoformat(),
                        "valores": evento.bases_aplicadas,
                    }
                )

            if evento.accion == AccionAuditoria.CORRECCION_REGISTRADA:
                correcciones.append(
                    {
                        "evento_id": str(evento.id),
                        "evento_corregido_id": str(evento.evento_corregido_id),
                        "motivo": evento.motivo_correccion,
                        "actor_id": str(evento.actor_id),
                        "ocurrido_en": evento.ocurrido_en.isoformat(),
                    }
                )

        return EstadoTransporteHistorico(
            transporte_id=transporte_id,
            hasta=fecha_corte,
            contrato=contrato,
            ofertas=list(ofertas.values()),
            revisiones=list(revisiones.values()),
            decisiones=list(decisiones.values()),
            bases_aplicadas=bases,
            correcciones=correcciones,
            eventos_considerados=len(eventos),
        )

    def verificar_integridad(self) -> ResultadoIntegridadAuditoria:
        """Verifica que ningun evento o enlace del historial haya sido alterado."""
        return self.dao.verificar_integridad()


def _resumen_actuacion(evento: EventoAuditoria) -> dict[str, Any]:
    """Expone actor, fecha, resultado y antecedentes de una actuacion."""
    return {
        "evento_id": str(evento.id),
        "entidad_id": str(evento.entidad_id),
        "accion": evento.accion.value,
        "actor_id": str(evento.actor_id),
        "ocurrido_en": evento.ocurrido_en.isoformat(),
        "datos": evento.datos,
        "informacion_utilizada": evento.informacion_utilizada,
    }
