/* Vista de inicio — dador — MansoViaje */
import { api, nodo, tarjetaKpi, tarjetas } from "../../ui.js";
import { estadoPanel } from "../../estado.js";
import { FUNCIONALIDADES_POR_ROL } from "../../roles.js";
import { obtenerPerfilDadorOpcional } from "./comun.js";

export async function inicioDador() {
  const [contratos, perfil] = await Promise.all([api("/contratos"), obtenerPerfilDadorOpcional()]);
  const propios = contratos.filter((c) => c.id_empresa_generadora === estadoPanel.usuario.id);
  const enSubasta = propios.filter((c) =>
    ["PUBLICADO", "EN_SUBASTA", "EN_POSTULACION"].includes(c.estado)
  ).length;
  const activos = propios.filter((c) =>
    ["ADJUDICADO", "EN_TRANSITO", "ENTREGADO"].includes(c.estado)
  ).length;

  const f = document.createDocumentFragment();
  f.append(
    nodo(
      "p",
      "Administra tus contratos de transporte, supervisa postulaciones y mantén al día tu perfil tributario.",
      "subtitulo-seccion"
    )
  );

  const grid = nodo("div", null, "rejilla-kpi");
  for (const kpi of [
    {
      titulo: "Estado KYC tributario",
      valor: perfil ? perfil.estado_validacion : "SIN REGISTRAR",
      modulo: "tributario",
      iconoNombre: "validaciones",
      esEstado: true,
    },
    {
      titulo: "Mis contratos",
      valor: propios.length,
      modulo: "contratos",
      iconoNombre: "contratos",
    },
    {
      titulo: "En subasta / postulación",
      valor: enSubasta,
      modulo: "subastas",
      iconoNombre: "subastas",
    },
    {
      titulo: "Adjudicados / en curso",
      valor: activos,
      modulo: "contratos",
      iconoNombre: "seguimiento",
    },
  ]) {
    grid.append(tarjetaKpi(kpi));
  }

  f.append(grid, nodo("h2", "Accesos rápidos"), tarjetas(FUNCIONALIDADES_POR_ROL.DADOR_CARGA));
  return f;
}
