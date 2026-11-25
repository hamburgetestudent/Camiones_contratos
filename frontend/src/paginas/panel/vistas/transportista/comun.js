/* Utilidades compartidas — transportista — MansoViaje */
import { api } from "../../ui.js";
import { estadoPanel } from "../../estado.js";

export async function obtenerEstadoCompliance() {
  return api("/onboarding/transportista/estado", undefined, {
    headers: { "X-User-Id": estadoPanel.usuario.id },
  });
}
