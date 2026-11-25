/* Enrutador de vistas del rol dador — MansoViaje */
import { contratosDador } from "./contratos.js";
import { inicioDador } from "./inicio.js";
import { subastasDador } from "./subastas.js";
import { tributarioDador } from "./tributario.js";

export async function vistaDador(ruta, params) {
  if (ruta === "inicio") return inicioDador();
  if (ruta === "contratos") return contratosDador(params);
  if (ruta === "subastas") return subastasDador(params);
  if (ruta === "tributario") return tributarioDador();
  return inicioDador();
}
