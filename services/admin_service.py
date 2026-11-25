"""Reglas administrativas, bajas lógicas y auditoría delegadas a la capa DAO."""

from __future__ import annotations

from datetime import UTC, date, datetime
from uuid import UUID, uuid4

from dao.admin_dao import AdminDAO, AdminDAOSQLite, TipoElemento
from dao.contrato_dao import ContratoDAO, ContratoDAOSQLite
from domain.maquina_estados import EstadoContrato, MaquinaEstadosContrato
from domain.modelos_usuario import UsuarioModelo

# Misma base por defecto que el resto de servicios (inyectables desde dependencies.py).
admin_dao: AdminDAO = AdminDAOSQLite()
_contratos: ContratoDAO = ContratoDAOSQLite()

ESTADOS_CANCELACION_ADMIN = frozenset(
    {
        EstadoContrato.PUBLICADO,
        EstadoContrato.EN_SUBASTA,
        EstadoContrato.EN_POSTULACION,
    }
)


def listar_elementos(tipo: TipoElemento, incluir_eliminados=False, estado=None):
    with admin_dao.conexion() as conn:
        elementos = admin_dao.listar_elementos(
            conn, tipo, incluir_eliminados=incluir_eliminados, estado=estado
        )
    if tipo == "contrato":
        for elemento in elementos:
            elemento["cancelable"] = (
                not elemento["eliminado"]
                and elemento["estado"] in ESTADOS_CANCELACION_ADMIN
            )
    return elementos


def _causa_rechazo(tipo, fila, motivo, confirmado, accion):
    if not fila:
        return "El elemento no existe."
    if not motivo:
        return "Ingresa el motivo de la operación."
    if not confirmado:
        return "Confirma la operación."
    if fila["eliminado"]:
        return "El elemento ya fue eliminado."
    if accion == "cancelar_contrato":
        if fila["estado"] not in ESTADOS_CANCELACION_ADMIN:
            return "Solo se pueden cancelar contratos publicados, en subasta o en postulación."
        return None
    if tipo == "contrato" and fila["estado"] != "PUBLICADO":
        return "Solo se pueden eliminar contratos actualmente en PUBLICADO."
    if tipo == "cuenta" and fila["rol"] == "ADMIN_BACKOFFICE":
        return "Las cuentas administrativas están protegidas. El panel solo permite eliminar cuentas de transportistas y dadores de carga."
    return None


def eliminar(
    tipo: TipoElemento,
    elemento_id: UUID,
    actor: UsuarioModelo,
    motivo: str,
    confirmado: bool,
):
    return _operar(tipo, elemento_id, actor, motivo, confirmado, "eliminar_" + tipo)


def cancelar_contrato(
    contrato_id: UUID, actor: UsuarioModelo, motivo: str, confirmado: bool
):
    return _operar(
        "contrato", contrato_id, actor, motivo, confirmado, "cancelar_contrato"
    )


def _operar(tipo, elemento_id, actor, motivo, confirmado, accion):
    """Reserva la escritura antes de releer el estado y registrar el resultado."""
    with admin_dao.transaccion() as conn:
        # Si la baja del actor ganó la carrera, su sesión ya no autoriza cambios.
        vigente = admin_dao.obtener_actor_vigente(conn, str(actor.id))
        if not vigente:
            raise PermissionError("La cuenta administradora ya no tiene acceso.")
        identificador = str(elemento_id)
        motivo = motivo.strip()
        autorizado = vigente["rol"] == "ADMIN_BACKOFFICE"
        fila = None
        if autorizado:
            fila = admin_dao.obtener_elemento_por_id(conn, tipo, identificador)
            causa = _causa_rechazo(tipo, fila, motivo, confirmado, accion)
        else:
            # Se audita el intento sin consultar ni revelar el recurso solicitado.
            causa = "Se requiere una cuenta administradora."
        anterior = (
            {"estado": fila["estado"], "eliminado": bool(fila["eliminado"])}
            if fila
            else None
        )
        posterior = anterior
        if not causa and accion == "cancelar_contrato":
            # El permiso es más estrecho que la máquina de estados. Se comprueban ambos
            # bajo el mismo bloqueo que usa la adjudicación, conservando todas las ofertas.
            contrato = _contratos.obtener_por_id(conn, elemento_id)
            actualizado = MaquinaEstadosContrato.cambiar_estado(
                contrato, EstadoContrato.CANCELADO
            )
            _contratos.actualizar(conn, elemento_id, actualizado)
            posterior = dict(anterior, estado=actualizado.estado.value)
        elif not causa:
            admin_dao.marcar_eliminado(conn, tipo, identificador)
            posterior = dict(anterior, eliminado=True)
        operacion = str(uuid4())
        admin_dao.registrar_accion(
            conn,
            operacion_id=operacion,
            fecha_iso=datetime.now(UTC).isoformat(),
            administrador_id=str(actor.id),
            administrador=vigente["nombre"],
            accion=accion,
            tipo=tipo,
            elemento_id=identificador,
            motivo=motivo,
            anterior=anterior,
            posterior=posterior,
            resultado="Rechazado" if causa else "Completado",
            causa=causa,
        )
    # El router comunica el rechazo después del commit para conservar su historial.
    if not autorizado:
        raise PermissionError(causa)
    return operacion, causa


def historial(
    desde: date | None = None,
    hasta: date | None = None,
    administrador=None,
    accion=None,
    resultado=None,
    tipo=None,
    elemento_id=None,
):
    with admin_dao.conexion() as conn:
        return admin_dao.listar_historial(
            conn,
            desde=desde,
            hasta=hasta,
            administrador=administrador,
            accion=accion,
            resultado=resultado,
            tipo=tipo,
            elemento_id=elemento_id,
        )


def resumen():
    """Una sola instantánea mantiene coherentes los indicadores y los últimos eventos."""
    hoy = datetime.now(UTC).date()
    with admin_dao.conexion() as conn:
        return admin_dao.obtener_resumen(conn, hoy)
