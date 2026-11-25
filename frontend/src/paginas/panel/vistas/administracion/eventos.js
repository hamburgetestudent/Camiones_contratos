/* Formato y lectura de eventos del historial — admin — MansoViaje */
import { badgeEstado, celdaId, enlace, nodo, tabla } from "../../ui.js";

/* Las fechas y los filtros usan UTC, igual que los indicadores calculados por FastAPI. */
export const etiquetasAccion = {
  cancelar_contrato: "Cancelar contrato",
  eliminar_contrato: "Eliminar contrato",
  eliminar_cuenta: "Eliminar cuenta",
};

export const fechaUTC = (valor) =>
  new Intl.DateTimeFormat("es-CL", {
    dateStyle: "short",
    timeStyle: "medium",
    timeZone: "UTC",
  }).format(new Date(valor));

export function elementoEventoNodo(e) {
  const wrap = nodo("div", null, "acciones-grupo");
  wrap.append(nodo("span", e.tipo, "badge badge-neutro"), celdaId(e.elemento_id));
  return wrap;
}

export function eventos(filas, filtros = {}) {
  return tabla(
    ["Fecha y hora (UTC)", "Administrador", "Acción", "Elemento", "Resultado", "Detalle"],
    filas.map((e) => [
      nodo("span", fechaUTC(e.fecha), "num-tabular"),
      e.administrador,
      etiquetasAccion[e.accion] || e.accion,
      elementoEventoNodo(e),
      badgeEstado(e.resultado),
      enlace("Ver detalle", "historial", { ...filtros, detalle: e.id }),
    ]),
    "No hay acciones registradas para esta consulta."
  );
}

export function valoresEvento(valor) {
  return valor
    ? valor.estado + " · " + (valor.eliminado ? "Eliminado" : "Vigente")
    : "Sin registro";
}
