/* Listados, detalle y bajas — admin — MansoViaje */
import {
  $,
  api,
  badgeEstado,
  boton,
  celdaId,
  enlace,
  estadoVacio,
  ficha,
  formatearMoneda,
  icono,
  mostrarAviso,
  nodo,
  tabla,
} from "../../ui.js";
import { estadoPanel, nombresRol } from "../../estado.js";
import { filtrosListado, opciones } from "./filtros.js";

const estadosContrato = [
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

let operacionPendiente;

function confirmarOperacion(accion, tipo, fila) {
  operacionPendiente = { accion, tipo, id: fila.id };
  const cancelar = accion === "cancelar";
  $("titulo-confirmacion").textContent = cancelar ? "Cancelar contrato" : "Eliminar " + tipo;
  $("etiqueta-motivo").textContent = cancelar
    ? "Motivo de la cancelación"
    : "Motivo de la eliminación";
  $("confirmar-operacion").textContent = cancelar
    ? "Confirmar cancelación"
    : "Confirmar eliminación";
  $("efecto-operacion").textContent = cancelar
    ? "La convocatoria terminará. El contrato y sus ofertas seguirán disponibles para consulta."
    : "El elemento dejará de aparecer en los listados habituales.";
  $("objetivo").textContent =
    (tipo === "cuenta" ? fila.nombre : fila.origen + " → " + fila.destino) + " · " + fila.id;
  $("motivo").value = "";
  $("error-baja").textContent = "";
  $("confirmacion").showModal();
  $("motivo").focus();
}

$("volver").onclick = () => $("confirmacion").close();

let enviandoBaja = false;
$("confirmacion").addEventListener("cancel", (e) => {
  if (enviandoBaja) e.preventDefault();
});

$("form-baja").onsubmit = async (e) => {
  e.preventDefault();
  if (enviandoBaja) return;
  const motivo = $("motivo").value.trim();
  if (!motivo) {
    $("error-baja").textContent = "Ingresa un motivo.";
    return;
  }
  enviandoBaja = true;
  const botones = $("form-baja").querySelectorAll("button");
  botones.forEach((b) => (b.disabled = true));
  try {
    const { accion, tipo, id } = operacionPendiente;
    await api("/admin/elementos/" + tipo + "/" + id + "/" + accion, { motivo, confirmado: true });
    $("confirmacion").close();
    // Retener el acceso al detalle y al historial tras retirar el elemento del listado habitual.
    const modulo = tipo === "cuenta" ? "cuentas" : "contratos";
    const destino =
      modulo + (accion === "eliminar" ? "?incluir_eliminados=1&detalle=" : "?detalle=") + id;
    if (location.hash.slice(1) === destino) await estadoPanel.navegar();
    else {
      location.hash = destino;
      await new Promise((resolve) =>
        window.addEventListener("hashchange", resolve, { once: true })
      );
    }
    mostrarAviso(
      accion === "cancelar"
        ? "Cancelación registrada correctamente."
        : "Eliminación registrada correctamente.",
      "exito"
    );
  } catch (error) {
    $("error-baja").textContent = error.message;
  } finally {
    enviandoBaja = false;
    botones.forEach((b) => (b.disabled = false));
  }
};

function detalleElemento(tipo, fila, ruta, params) {
  const f = document.createDocumentFragment(),
    anterior = new URLSearchParams(params);
  anterior.delete("detalle");

  const barraTop = nodo("div", null, "acciones-barra");
  const btnVolver = enlace("Volver al listado", ruta, Object.fromEntries(anterior));
  btnVolver.prepend(icono("flechaIzq", 15));
  barraTop.append(btnVolver);

  const situacion = fila.eliminado
    ? badgeEstado("ELIMINADO", "Eliminado")
    : badgeEstado("VIGENTE", "Vigente");

  const campos = [
    ["Identificador", celdaId(fila.id)],
    ["Estado", badgeEstado(fila.estado)],
    ["Eliminación", situacion],
  ];
  if (tipo === "cuenta")
    campos.push(
      ["Nombre", fila.nombre],
      ["Correo", fila.email],
      ["Rol", nombresRol[fila.rol] || fila.rol]
    );
  else
    campos.push(
      ["Origen", fila.origen],
      ["Destino", fila.destino],
      ["Dador de carga", celdaId(fila.id_empresa_generadora)],
      ["Transportista", fila.id_transportista ? celdaId(fila.id_transportista) : "Sin asignar"],
      ["Carga", fila.tipo_carga],
      ["Monto total", nodo("span", formatearMoneda(fila.monto_total, fila.moneda), "num-tabular")]
    );

  const acciones = nodo("div", null, "acciones-grupo");
  acciones.append(
    enlace("Consultar historial del elemento", "historial", { tipo, elemento_id: fila.id })
  );
  if (tipo === "contrato" && fila.cancelable) {
    acciones.append(boton("Cancelar contrato", () => confirmarOperacion("cancelar", tipo, fila)));
  }

  let razon = "";
  if (fila.eliminado) razon = "Este elemento ya fue eliminado.";
  else if (tipo === "contrato" && fila.estado !== "PUBLICADO")
    razon = "Solo se pueden eliminar contratos actualmente en PUBLICADO.";
  else if (tipo === "cuenta" && fila.rol === "ADMIN_BACKOFFICE")
    razon =
      "Las cuentas administrativas están protegidas. El panel solo permite eliminar cuentas de transportistas y dadores de carga.";

  if (!razon) {
    const b = boton("Eliminar " + tipo, () => confirmarOperacion("eliminar", tipo, fila));
    b.classList.add("peligro");
    acciones.append(b);
  }

  f.append(barraTop, ficha(campos), acciones);
  if (razon) {
    const nota = nodo("p", razon, "nota-protegida");
    nota.style.marginTop = "14px";
    f.append(nota);
  }
  return f;
}

export async function elementosAdmin(ruta, params) {
  const contrato = ruta === "contratos",
    tipo = contrato ? "contrato" : "cuenta",
    consulta = new URLSearchParams();
  const incluir = params.get("incluir_eliminados") === "1";
  if (incluir) consulta.set("incluir_eliminados", "true");
  if (contrato && params.get("estado")) consulta.set("estado", params.get("estado"));
  const filas = await api("/admin/elementos/" + tipo + "?" + consulta),
    detalle = params.get("detalle");
  if (detalle) {
    const fila = filas.find((f) => f.id === detalle);
    return fila
      ? detalleElemento(tipo, fila, ruta, params)
      : estadoVacio(
          "El elemento ya no aparece en esta consulta.",
          enlace("Volver al listado", ruta)
        );
  }
  const campos = [
    ["incluir_eliminados", contrato ? "Incluir eliminados" : "Incluir eliminadas", "checkbox"],
  ];
  if (contrato) campos.push(["estado", "Estado", null, opciones(estadosContrato)]);
  const f = document.createDocumentFragment();
  f.append(filtrosListado(ruta, campos, params));
  if (!contrato && !incluir) {
    f.append(nodo("p", "Cuentas activas (" + filas.length + ")", "subtitulo-seccion"));
  }
  f.append(
    tabla(
      [
        contrato ? "Ruta" : "Nombre",
        contrato ? "Estado" : "Rol",
        "Identificador",
        "Situación",
        "Detalle",
      ],
      filas.map((fila) => [
        contrato ? fila.origen + " → " + fila.destino : fila.nombre,
        contrato ? badgeEstado(fila.estado) : nombresRol[fila.rol] || fila.rol,
        celdaId(fila.id),
        fila.eliminado ? badgeEstado("ELIMINADO", "Eliminado") : badgeEstado("VIGENTE", "Vigente"),
        enlace("Ver detalle", ruta, { ...Object.fromEntries(params), detalle: fila.id }),
      ]),
      "No hay elementos que coincidan con los filtros."
    )
  );
  return f;
}
