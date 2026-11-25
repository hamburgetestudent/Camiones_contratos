/* Vista de inicio — admin — MansoViaje */
import { api, enlace, icono, nodo, tarjetaKpi, tarjetas } from "../../ui.js";
import { FUNCIONALIDADES_POR_ROL } from "../../roles.js";
import { eventos } from "./eventos.js";

export async function inicioAdmin() {
  const r = await api("/admin/resumen"),
    bloque = document.createDocumentFragment(),
    grid = nodo("div", null, "rejilla-kpi");

  bloque.append(
    nodo(
      "p",
      "Gestiona los contratos, las cuentas y las acciones administrativas de la plataforma.",
      "subtitulo-seccion"
    )
  );

  for (const kpi of [
    {
      titulo: "Contratos publicados",
      valor: r.publicados,
      modulo: "contratos",
      filtros: { estado: "PUBLICADO" },
      iconoNombre: "contratos",
    },
    {
      titulo: "Cuentas activas",
      valor: r.activas,
      modulo: "cuentas",
      filtros: { activas: "1" },
      iconoNombre: "cuentas",
    },
    {
      titulo: "Acciones administrativas de hoy (UTC)",
      valor: r.acciones,
      modulo: "historial",
      filtros: { desde: r.hoy, hasta: r.hoy, resultado: "Completado" },
      iconoNombre: "historial",
    },
  ]) {
    grid.append(tarjetaKpi(kpi));
  }

  const pieHistorial = nodo("div", null, "acciones-barra");
  pieHistorial.style.marginTop = "14px";
  const linkHistorial = enlace("Ver todo el historial", "historial");
  linkHistorial.append(icono("flechaDer", 14));
  pieHistorial.append(linkHistorial);

  bloque.append(
    grid,
    nodo("h2", "Accesos"),
    tarjetas(FUNCIONALIDADES_POR_ROL.ADMIN_BACKOFFICE),
    nodo("h2", "Actividad reciente"),
    eventos(r.recientes),
    pieHistorial
  );
  return bloque;
}
