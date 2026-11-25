/* Historial de operaciones — admin — MansoViaje */
import { api, badgeEstado, celdaId, enlace, estadoVacio, ficha, icono, nodo } from "../../ui.js";
import {
  elementoEventoNodo,
  etiquetasAccion,
  eventos,
  fechaUTC,
  valoresEvento,
} from "./eventos.js";
import { filtrosListado, opciones } from "./filtros.js";

export async function historialAdmin(params) {
  const consulta = new URLSearchParams(params);
  consulta.delete("detalle");
  const filas = await api("/admin/historial?" + consulta);
  const f = document.createDocumentFragment(),
    detalle = params.get("detalle");
  if (detalle) {
    const e = filas.find((fila) => fila.id === detalle);
    const barra = nodo("div", null, "acciones-barra");
    const btnVolver = enlace("Volver al historial", "historial", Object.fromEntries(consulta));
    btnVolver.prepend(icono("flechaIzq", 15));
    barra.append(btnVolver);
    f.append(barra);

    if (e)
      f.append(
        ficha([
          ["Operación", celdaId(e.id)],
          ["Fecha y hora (UTC)", nodo("span", fechaUTC(e.fecha), "num-tabular")],
          ["Administrador", e.administrador],
          ["ID administrador", celdaId(e.administrador_id)],
          ["Acción", etiquetasAccion[e.accion] || e.accion],
          ["Elemento", elementoEventoNodo(e)],
          ["Motivo", e.motivo || "Sin motivo informado"],
          ["Antes", valoresEvento(e.anterior)],
          ["Después", valoresEvento(e.posterior)],
          ["Resultado", badgeEstado(e.resultado)],
          ["Causa", e.causa || "—"],
        ])
      );
    else f.append(estadoVacio("No se encontró la operación."));
    return f;
  }
  f.append(
    filtrosListado(
      "historial",
      [
        ["desde", "Desde (UTC)", "date"],
        ["hasta", "Hasta (UTC)", "date"],
        ["administrador", "Nombre o ID de administrador", "text"],
        ["accion", "Acción", null, [["", "Todas"], ...Object.entries(etiquetasAccion)]],
        ["resultado", "Resultado", null, opciones(["Completado", "Rechazado"])],
        ["tipo", "Tipo de elemento", null, opciones(["contrato", "cuenta"])],
        ["elemento_id", "ID del elemento", "text"],
      ],
      params
    ),
    eventos(filas, Object.fromEntries(consulta))
  );
  return f;
}
