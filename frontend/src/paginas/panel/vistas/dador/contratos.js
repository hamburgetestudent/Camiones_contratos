/* Contratos del dador — dador — MansoViaje */
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
  icono,
  mostrarAviso,
  nodo,
  tabla,
} from "../../ui.js";
import { estadoPanel } from "../../estado.js";

/* Vistas operativas para el rol DADOR_CARGA dentro del panel unificado — MansoViaje */

const ESTADOS_CONTRATO_DADOR = [
  "BORRADOR",
  "PUBLICADO",
  "EN_SUBASTA",
  "EN_POSTULACION",
  "ADJUDICADO",
  "EN_TRANSITO",
  "ENTREGADO",
  "FINALIZADO",
  "CANCELADO",
  "EN_DISPUTA",
];

async function cambiarEstadoContratoDador(contratoId, nuevoEstado, confirmacion = null) {
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
    mostrarAviso("Estado del contrato actualizado a " + nuevoEstado + ".", "exito");
  } catch (error) {
    mostrarAviso(error.message, "error");
  }
}

function accionesEstadoDador(contrato) {
  const grupo = nodo("div", null, "acciones-grupo");
  const confirmarCancelar = {
    titulo: "Cancelar contrato",
    descripcion:
      "El contrato pasará a estado CANCELADO (terminal) y dejará de aceptar postulaciones o avanzar en el flujo.",
    textoConfirmar: "Sí, cancelar contrato",
    variante: "btn-peligro-solido",
  };
  const confirmarFinalizar = {
    titulo: "Finalizar contrato",
    descripcion:
      "Confirmas la conformidad del servicio. El contrato pasará a estado FINALIZADO y no podrá modificarse.",
    textoConfirmar: "Finalizar contrato",
    variante: "btn-exito",
  };
  const confirmarDisputa = {
    titulo: "Abrir disputa",
    descripcion: "El contrato quedará marcado EN_DISPUTA para su revisión y resolución posterior.",
    textoConfirmar: "Abrir disputa",
    variante: "btn-peligro-solido",
  };

  if (contrato.estado === "BORRADOR") {
    grupo.append(
      boton("Publicar", () => cambiarEstadoContratoDador(contrato.id, "PUBLICADO"), "btn-primario"),
      boton("Abrir subasta", () => cambiarEstadoContratoDador(contrato.id, "EN_SUBASTA")),
      boton(
        "Cancelar",
        () => cambiarEstadoContratoDador(contrato.id, "CANCELADO", confirmarCancelar),
        "peligro"
      )
    );
  } else if (["PUBLICADO", "EN_SUBASTA", "EN_POSTULACION"].includes(contrato.estado)) {
    if (contrato.estado === "PUBLICADO") {
      grupo.append(
        boton("Abrir subasta", () => cambiarEstadoContratoDador(contrato.id, "EN_SUBASTA"))
      );
    }
    grupo.append(
      enlace("Ver postulaciones", "subastas", { contrato: contrato.id }),
      boton(
        "Cancelar",
        () => cambiarEstadoContratoDador(contrato.id, "CANCELADO", confirmarCancelar),
        "peligro"
      )
    );
  } else if (contrato.estado === "ENTREGADO") {
    grupo.append(
      boton(
        "Finalizar contrato",
        () => cambiarEstadoContratoDador(contrato.id, "FINALIZADO", confirmarFinalizar),
        "btn-exito"
      ),
      boton(
        "Abrir disputa",
        () => cambiarEstadoContratoDador(contrato.id, "EN_DISPUTA", confirmarDisputa),
        "peligro"
      )
    );
  } else if (contrato.estado === "EN_DISPUTA") {
    grupo.append(
      boton(
        "Finalizar contrato",
        () => cambiarEstadoContratoDador(contrato.id, "FINALIZADO", confirmarFinalizar),
        "btn-exito"
      ),
      boton(
        "Cancelar",
        () => cambiarEstadoContratoDador(contrato.id, "CANCELADO", confirmarCancelar),
        "peligro"
      )
    );
  }
  return grupo;
}

export async function contratosDador(params) {
  const contratos = await api("/contratos");
  const propios = contratos.filter((c) => c.id_empresa_generadora === estadoPanel.usuario.id);
  const detalleId = params.get("detalle");

  const f = document.createDocumentFragment();
  const barra = nodo("div", null, "acciones-barra");
  const links = nodo("div", null, "acciones-grupo");
  const btnCrear = nodo("a", "+ Nuevo contrato", "boton btn-primario");
  btnCrear.href = "../crear-contrato/crear-contrato.html?desde=panel";
  const btnCatalogo = nodo("a", "Abrir vista catálogo", "boton");
  btnCatalogo.href = "../catalogo-contratos/catalogo-contratos.html";
  btnCatalogo.prepend(icono("catalogo", 15));
  links.append(btnCrear, btnCatalogo);
  barra.append(links);
  f.append(barra);

  if (detalleId) {
    const c = propios.find((item) => item.id === detalleId);
    const barraVolver = nodo("div", null, "acciones-barra");
    barraVolver.append(enlace("← Volver a mis contratos", "contratos"));
    f.append(barraVolver);

    if (!c) {
      f.append(estadoVacio("No se encontró el contrato solicitado."));
      return f;
    }
    f.append(
      ficha([
        ["Identificador", celdaId(c.id)],
        ["Estado", badgeEstado(c.estado)],
        ["Ruta", c.origen + " → " + c.destino],
        ["Tipo de carga", c.tipo_carga],
        [
          "Peso / Capacidad",
          nodo("span", c.peso_total + " KG / " + c.input_camionKG + " KG", "num-tabular"),
        ],
        ["Cierre postulaciones", nodo("span", fechaLocal(c.f_cierre_postulaciones), "num-tabular")],
        ["Salida estimada", nodo("span", fechaLocal(c.f_estimada_salida), "num-tabular")],
        ["Llegada estimada", nodo("span", fechaLocal(c.f_estimada_llegada), "num-tabular")],
        ["Monto neto", nodo("span", formatearMoneda(c.monto_neto, c.moneda), "num-tabular")],
        ["IVA", nodo("span", formatearMoneda(c.monto_iva, c.moneda), "num-tabular")],
        ["Monto total", nodo("span", formatearMoneda(c.monto_total, c.moneda), "num-tabular")],
        [
          "Transportista asignado",
          c.id_transportista ? celdaId(c.id_transportista) : "Sin asignar",
        ],
      ]),
      accionesEstadoDador(c)
    );
    return f;
  }

  const estadoFiltro = params.get("estado") || "";
  const formFiltro = nodo("form", null, "barra-filtros");
  const tituloFiltro = nodo("p", null, "barra-filtros-titulo");
  tituloFiltro.append(icono("filtro", 14), nodo("span", "Filtrar mis contratos"));
  const gridFiltro = nodo("div", null, "barra-filtros-grid");

  const labelEstado = nodo("label", "Estado");
  const selEstado = nodo("select");
  selEstado.name = "estado";
  const optTodos = nodo("option", "Todos");
  optTodos.value = "";
  selEstado.append(optTodos);
  for (const est of ESTADOS_CONTRATO_DADOR) {
    const opt = nodo("option", est);
    opt.value = est;
    selEstado.append(opt);
  }
  selEstado.value = estadoFiltro;
  labelEstado.append(selEstado);
  gridFiltro.append(labelEstado);

  const accionesFiltro = nodo("div", null, "barra-filtros-acciones");
  const btnFiltrar = nodo("button", "Filtrar", "btn-primario");
  btnFiltrar.type = "submit";
  accionesFiltro.append(btnFiltrar, enlace("Limpiar", "contratos"));

  formFiltro.append(tituloFiltro, gridFiltro, accionesFiltro);
  formFiltro.onsubmit = (e) => {
    e.preventDefault();
    location.hash = selEstado.value ? "contratos?estado=" + selEstado.value : "contratos";
  };

  const filtrados = estadoFiltro ? propios.filter((c) => c.estado === estadoFiltro) : propios;
  const ctaNuevo = nodo("a", "+ Crear primer contrato", "boton btn-primario");
  ctaNuevo.href = "../crear-contrato/crear-contrato.html?desde=panel";

  f.append(
    formFiltro,
    tabla(
      ["Ruta", "Tipo carga", "Monto total", "Salida", "Estado", "Acciones"],
      filtrados.map((c) => [
        c.origen + " → " + c.destino,
        c.tipo_carga,
        nodo("span", formatearMoneda(c.monto_total, c.moneda), "num-tabular"),
        nodo("span", fechaLocal(c.f_estimada_salida), "num-tabular"),
        badgeEstado(c.estado),
        enlace("Gestionar", "contratos", { detalle: c.id }),
      ]),
      "Aún no tienes contratos registrados con este filtro.",
      estadoFiltro ? enlace("Ver todos mis contratos", "contratos") : ctaNuevo
    )
  );
  return f;
}
