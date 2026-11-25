/* Enrutador de vistas del rol transportista — MansoViaje */
import { inicioTransportista } from "./inicio.js";
import { onboardingTransportista } from "./onboarding.js";
import { seguimientoTransportista } from "./seguimiento.js";
import { subastasTransportista } from "./subastas.js";

export async function vistaTransportista(ruta, params) {
  if (ruta === "inicio") return inicioTransportista();
  if (ruta === "subastas") return subastasTransportista(params);
  if (ruta === "onboarding") return onboardingTransportista();
  if (ruta === "seguimiento") return seguimientoTransportista();
  return inicioTransportista();
}
