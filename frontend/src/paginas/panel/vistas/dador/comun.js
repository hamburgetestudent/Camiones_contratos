/* Utilidades compartidas — dador — MansoViaje */
import { api } from "../../ui.js";
import { estadoPanel } from "../../estado.js";

export async function obtenerPerfilDadorOpcional() {
  try {
    return await api("/onboarding/dador/perfil", undefined, {
      headers: { "X-User-Id": estadoPanel.usuario.id },
    });
  } catch {
    return null;
  }
}
