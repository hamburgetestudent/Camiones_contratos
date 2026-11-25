"""Consultas administrativas y bajas lógicas sobre la misma base que el negocio."""

import json
from datetime import UTC, date, datetime, timedelta
from typing import Literal
from uuid import UUID, uuid4

from app.db.conexion import obtener_conexion, transaccion_exclusiva
from app.modules.contratos.dao import ContratoDAOSQLite
from app.modules.contratos.maquina_estados import EstadoContrato, MaquinaEstadosContrato
from app.modules.usuarios.models import UsuarioModelo

# Misma base por defecto que el resto de servicios; opera sobre la conexion recibida.
_contratos = ContratoDAOSQLite()

ESTADOS_CANCELACION_ADMIN = frozenset(
    {
        EstadoContrato.PUBLICADO,
        EstadoContrato.EN_SUBASTA,
        EstadoContrato.EN_POSTULACION,
    }
)

TipoElemento = Literal["contrato", "cuenta"]
# Solo consultas conocidas pueden elegir tablas y columnas. Nunca se lee el hash.
_CONSULTAS = {
    "contrato": "SELECT * FROM contratos",
    "cuenta": "SELECT id, nombre, email, rol, estado, eliminado FROM usuarios",
}


def listar_elementos(tipo: TipoElemento, incluir_eliminados=False, estado=None):
    sql = _CONSULTAS[tipo] + " WHERE (? OR eliminado = 0)"
    valores = [incluir_eliminados]
    if estado:
        sql += " AND estado = ?"
        valores.append(estado)
    with obtener_conexion() as conn:
        elementos = [
            dict(fila) for fila in conn.execute(sql + " ORDER BY rowid DESC", valores)
        ]
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
    with transaccion_exclusiva() as conn:
        # Si la baja del actor ganó la carrera, su sesión ya no autoriza cambios.
        vigente = conn.execute(
            "SELECT nombre, rol FROM usuarios WHERE id = ? AND eliminado = 0",
            (str(actor.id),),
        ).fetchone()
        if not vigente:
            raise PermissionError("La cuenta administradora ya no tiene acceso.")
        identificador = str(elemento_id)
        motivo = motivo.strip()
        autorizado = vigente["rol"] == "ADMIN_BACKOFFICE"
        fila = None
        if autorizado:
            fila = conn.execute(
                _CONSULTAS[tipo] + " WHERE id = ?", (identificador,)
            ).fetchone()
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
            tabla = "contratos" if tipo == "contrato" else "usuarios"
            conn.execute(
                f"UPDATE {tabla} SET eliminado = 1 WHERE id = ?", (identificador,)
            )
            posterior = dict(anterior, eliminado=True)
        operacion = str(uuid4())
        conn.execute(
            """INSERT INTO acciones_admin
            (id, fecha, administrador_id, administrador, accion, tipo, elemento_id,
             motivo, anterior, posterior, resultado, causa) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                operacion,
                datetime.now(UTC).isoformat(),
                str(actor.id),
                vigente["nombre"],
                accion,
                tipo,
                identificador,
                motivo,
                json.dumps(anterior),
                json.dumps(posterior),
                "Rechazado" if causa else "Completado",
                causa,
            ),
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
    condiciones = []
    valores = []
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
    with obtener_conexion() as conn:
        filas = conn.execute(
            "SELECT * FROM acciones_admin" + where + " ORDER BY fecha DESC, rowid DESC",
            valores,
        )
        return [_evento(fila) for fila in filas]


def _evento(fila):
    return dict(
        dict(fila),
        anterior=json.loads(fila["anterior"]),
        posterior=json.loads(fila["posterior"]),
    )


def resumen():
    """Una sola instantánea mantiene coherentes los indicadores y los últimos eventos."""
    hoy = datetime.now(UTC).date()
    with obtener_conexion() as conn:
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
                _evento(f)
                for f in conn.execute(
                    "SELECT * FROM acciones_admin ORDER BY fecha DESC, rowid DESC LIMIT 10"
                )
            ],
        }
