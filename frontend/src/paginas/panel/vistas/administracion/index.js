/* Enrutador de vistas del rol admin — MansoViaje */
import { configuracionAdmin } from "./configuracion.js";
import { historialAdmin } from "./historial.js";
import { inicioAdmin } from "./inicio.js";
import { elementosAdmin } from "./listados.js";
import { validacionesAdmin } from "./validaciones.js";

export async function vistaAdmin(ruta, params) {
  if (ruta === "inicio") return inicioAdmin();
  if (ruta === "historial") return historialAdmin(params);
  if (ruta === "validaciones") return validacionesAdmin();
  if (ruta === "configuracion") return configuracionAdmin();
  return elementosAdmin(ruta, params);
}
