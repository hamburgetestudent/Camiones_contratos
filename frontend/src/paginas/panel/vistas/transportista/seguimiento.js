/* Despacho y seguimiento — transportista — MansoViaje */
import {
  api,
  badgeEstado,
  boton,
  confirmarAccion,
  enlace,
  fechaLocal,
  formatearMoneda,
  mostrarAviso,
  nodo,
  tabla,
} from "../../ui.js";
import { estadoPanel } from "../../estado.js";

export async function seguimientoTransportista() {
  const contratos = await api("/contratos");
  const asignados = contratos.filter((c) => c.id_transportista === estadoPanel.usuario.id);
  const f = document.createDocumentFragment();

  f.append(
    nodo(
      "p",
      "Reporta el inicio de tránsito y la entrega de los contratos que te fueron adjudicados.",
      "subtitulo-seccion"
    )
  );

  async function avanzarEstado(contratoId, nuevoEstado, confirmacion) {
    if (confirmacion) {
      const ok = await confirmarAccion(confirmacion);
      if (!ok) return;
    }
    try {
      await api(
        "/contratos/" + contratoId + "/estado",
        { nuevo_estado: nuevoEstado },
        { method: "PATCH" }
      );
      await estadoPanel.navegar();
      mostrarAviso("Despacho actualizado a estado " + nuevoEstado + ".", "exito");
    } catch (error) {
      mostrarAviso(error.message, "error");
    }
  }

  f.append(
    tabla(
      ["Ruta", "Tipo carga", "Salida estimada", "Monto total", "Estado", "Acciones"],
      asignados.map((c) => {
        const acciones = nodo("div", null, "acciones-grupo");
        if (c.estado === "ADJUDICADO") {
          acciones.append(
            boton(
              "Iniciar tránsito",
              () =>
                avanzarEstado(c.id, "EN_TRANSITO", {
                  titulo: "Confirmar inicio de tránsito",
                  descripcion:
                    "El despacho " + c.origen + " → " + c.destino + " pasará a estado EN_TRANSITO.",
                  textoConfirmar: "Iniciar tránsito",
                  variante: "btn-primario",
                }),
              "btn-primario btn-sm"
            )
          );
        } else if (c.estado === "EN_TRANSITO") {
          acciones.append(
            boton(
              "Confirmar entrega",
              () =>
                avanzarEstado(c.id, "ENTREGADO", {
                  titulo: "Confirmar entrega en destino",
                  descripcion:
                    "Registrarás la entrega definitiva de la carga en " +
                    c.destino +
                    " para que el dador pueda finalizar el contrato.",
                  textoConfirmar: "Confirmar entrega",
                  variante: "btn-exito",
                }),
              "btn-exito btn-sm"
            ),
            boton(
              "Reportar disputa",
              () =>
                avanzarEstado(c.id, "EN_DISPUTA", {
                  titulo: "Reportar incidencia o disputa",
                  descripcion:
                    "El contrato pasará a estado EN_DISPUTA y se detendrá el cierre normal hasta su resolución.",
                  textoConfirmar: "Reportar disputa",
                  variante: "btn-peligro-solido",
                }),
              "peligro btn-sm"
            )
          );
        } else {
          acciones.append(nodo("span", "Sin acciones pendientes", "texto-suave"));
        }
        return [
          c.origen + " → " + c.destino,
          c.tipo_carga,
          nodo("span", fechaLocal(c.f_estimada_salida), "num-tabular"),
          nodo("span", formatearMoneda(c.monto_total, c.moneda), "num-tabular"),
          badgeEstado(c.estado),
          acciones,
        ];
      }),
      "Aún no tienes contratos adjudicados asignados a tu cuenta.",
      enlace("Explorar cargas disponibles", "subastas")
    )
  );
  return f;
}
