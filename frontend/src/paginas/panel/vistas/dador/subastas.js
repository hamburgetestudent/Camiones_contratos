/* Subastas — dador — MansoViaje */
import {
  api,
  badgeEstado,
  boton,
  celdaId,
  confirmarAccion,
  enlace,
  estadoVacio,
  fechaLocal,
  ficha,
  formatearMoneda,
  mostrarAviso,
  nodo,
  tabla,
} from "../../ui.js";
import { estadoPanel } from "../../estado.js";

export async function subastasDador(params) {
  const contratos = await api("/contratos");
  const subastables = contratos.filter(
    (c) =>
      c.id_empresa_generadora === estadoPanel.usuario.id &&
      ["PUBLICADO", "EN_SUBASTA", "EN_POSTULACION", "ADJUDICADO"].includes(c.estado)
  );
  const f = document.createDocumentFragment();
  const seleccionadoId = params.get("contrato");

  if (seleccionadoId) {
    const contrato = subastables.find((c) => c.id === seleccionadoId);
    const barra = nodo("div", null, "acciones-barra");
    barra.append(enlace("← Volver a mis subastas", "subastas"));
    f.append(barra);

    if (!contrato) {
      f.append(estadoVacio("No se encontró la subasta solicitada."));
      return f;
    }

    const postulaciones = await api("/subastas/cargas/" + contrato.id + "/postulaciones");
    f.append(
      nodo("h2", contrato.origen + " → " + contrato.destino),
      ficha([
        ["Estado", badgeEstado(contrato.estado)],
        [
          "Monto referencial",
          nodo("span", formatearMoneda(contrato.monto_total, contrato.moneda), "num-tabular"),
        ],
        [
          "Cierre postulaciones",
          nodo("span", fechaLocal(contrato.f_cierre_postulaciones), "num-tabular"),
        ],
        ["Postulaciones recibidas", nodo("span", String(postulaciones.length), "num-tabular")],
      ])
    );

    async function adjudicar(postulacion) {
      const ok = await confirmarAccion({
        titulo: "Confirmar adjudicación",
        descripcion:
          "Adjudicarás esta carga por " +
          formatearMoneda(postulacion.precio_oferta, "CLP") +
          " (" +
          postulacion.tiempo_entrega_horas +
          " h). Las demás postulaciones pasarán automáticamente a RECHAZADA.",
        textoConfirmar: "Adjudicar oferta",
        variante: "btn-exito",
      });
      if (!ok) return;

      try {
        await api("/subastas/adjudicar", {
          carga_id: contrato.id,
          postulacion_id: postulacion.id,
        });
        await estadoPanel.navegar();
        mostrarAviso("Subasta adjudicada correctamente.", "exito");
      } catch (error) {
        mostrarAviso(error.message, "error");
      }
    }

    const adjudicable = ["PUBLICADO", "EN_SUBASTA", "EN_POSTULACION"].includes(contrato.estado);
    f.append(
      nodo("h2", "Ofertas recibidas"),
      tabla(
        ["Transportista ID", "Oferta", "Tiempo entrega", "Comentario", "Estado", "Acción"],
        postulaciones.map((p) => [
          celdaId(p.transportista_id),
          nodo("span", formatearMoneda(p.precio_oferta, "CLP"), "num-tabular"),
          nodo("span", p.tiempo_entrega_horas + " h", "num-tabular"),
          p.comentario || "—",
          badgeEstado(p.estado),
          adjudicable && p.estado === "POSTULADA"
            ? boton("Adjudicar oferta", () => adjudicar(p), "btn-exito btn-sm")
            : "—",
        ]),
        "Aún no se han recibido postulaciones para esta carga."
      )
    );
    return f;
  }

  f.append(
    nodo(
      "p",
      "Selecciona uno de tus contratos publicados o en subasta para revisar ofertas y adjudicar al transportista ganador.",
      "subtitulo-seccion"
    ),
    tabla(
      ["Ruta", "Tipo carga", "Monto total", "Cierre postulaciones", "Estado", "Ofertas"],
      subastables.map((c) => [
        c.origen + " → " + c.destino,
        c.tipo_carga,
        nodo("span", formatearMoneda(c.monto_total, c.moneda), "num-tabular"),
        nodo("span", fechaLocal(c.f_cierre_postulaciones), "num-tabular"),
        badgeEstado(c.estado),
        enlace("Revisar ofertas", "subastas", { contrato: c.id }),
      ]),
      "No tienes cargas en subasta o publicadas actualmente. Crea o publica un contrato desde Mis Contratos.",
      enlace("Ir a Mis Contratos", "contratos")
    )
  );
  return f;
}
