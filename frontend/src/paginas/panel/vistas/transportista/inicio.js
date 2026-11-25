/* Vista de inicio — transportista — MansoViaje */
import { api, nodo, tarjetaKpi, tarjetas } from "../../ui.js";
import { estadoPanel } from "../../estado.js";
import { FUNCIONALIDADES_POR_ROL } from "../../roles.js";
import { obtenerEstadoCompliance } from "./comun.js";

export async function inicioTransportista() {
  const [estadoKyc, cargas, contratos] = await Promise.all([
    obtenerEstadoCompliance(),
    api("/subastas/cargas"),
    api("/contratos"),
  ]);
  const asignados = contratos.filter((c) => c.id_transportista === estadoPanel.usuario.id);

  const f = document.createDocumentFragment();
  f.append(
    nodo(
      "p",
      "Explora cargas disponibles para postular, gestiona tu documentación de cumplimiento y reporta el avance de tus viajes.",
      "subtitulo-seccion"
    )
  );

  const grid = nodo("div", null, "rejilla-kpi");
  for (const kpi of [
    {
      titulo: "Estado Compliance",
      valor: estadoKyc.estado_global,
      modulo: "onboarding",
      iconoNombre: "validaciones",
      esEstado: true,
    },
    {
      titulo: "Cargas disponibles",
      valor: cargas.length,
      modulo: "subastas",
      iconoNombre: "subastas",
    },
    {
      titulo: "Despachos asignados",
      valor: asignados.length,
      modulo: "seguimiento",
      iconoNombre: "seguimiento",
    },
  ]) {
    grid.append(tarjetaKpi(kpi));
  }

  f.append(grid, nodo("h2", "Accesos rápidos"), tarjetas(FUNCIONALIDADES_POR_ROL.TRANSPORTISTA));
  return f;
}
