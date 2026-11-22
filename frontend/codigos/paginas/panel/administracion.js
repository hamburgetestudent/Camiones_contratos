/* Las fechas y los filtros usan UTC, igual que los indicadores calculados por FastAPI. */
const etiquetasAccion = {
  eliminar_contrato: "Eliminar contrato",
  eliminar_cuenta: "Eliminar cuenta",
};
const fechaUTC = (valor) =>
  new Intl.DateTimeFormat("es-CL", {
    dateStyle: "short",
    timeStyle: "medium",
    timeZone: "UTC",
  }).format(new Date(valor));
function tabla(columnas, filas, vacio) {
  if (!filas.length) return nodo("p", vacio);
  const caja = nodo("div", null, "tabla"),
    tabla = nodo("table"),
    cabecera = tabla.createTHead().insertRow();
  for (const nombre of columnas) {
    const th = nodo("th", nombre);
    th.scope = "col";
    cabecera.append(th);
  }
  const cuerpo = tabla.createTBody();
  for (const fila of filas) {
    const tr = cuerpo.insertRow();
    for (const valor of fila) {
      const td = tr.insertCell();
      if (valor instanceof Node) td.append(valor);
      else td.textContent = valor ?? "—";
    }
  }
  caja.append(tabla);
  return caja;
}
function ficha(campos) {
  const dl = nodo("dl");
  for (const [etiqueta, valor] of campos) dl.append(nodo("dt", etiqueta), nodo("dd", valor ?? "—"));
  return dl;
}
function eventos(filas, filtros = {}) {
  return tabla(
    ["Fecha y hora (UTC)", "Administrador", "Acción", "Elemento", "Resultado", "Detalle"],
    filas.map((e) => [
      fechaUTC(e.fecha),
      e.administrador,
      etiquetasAccion[e.accion],
      e.tipo + " · " + e.elemento_id,
      e.resultado,
      enlace("Ver detalle", "historial", { ...filtros, detalle: e.id }),
    ]),
    "No hay acciones registradas para esta consulta."
  );
}
async function inicioAdmin() {
  const r = await api("/admin/resumen"),
    bloque = document.createDocumentFragment(),
    grid = nodo("div", null, "rejilla");
  bloque.append(
    nodo(
      "p",
      "Gestiona los contratos, las cuentas y las acciones administrativas de la plataforma."
    )
  );
  for (const [titulo, valor, modulo, filtros] of [
    ["Contratos publicados", r.publicados, "contratos", { estado: "PUBLICADO" }],
    ["Cuentas activas", r.activas, "cuentas", { activas: "1" }],
    [
      "Acciones administrativas de hoy (UTC)",
      r.acciones,
      "historial",
      { desde: r.hoy, hasta: r.hoy, resultado: "Completado" },
    ],
  ]) {
    const link = enlace("", modulo, filtros);
    link.className = "tarjeta";
    link.append(nodo("span", titulo), nodo("strong", valor, "indicador"));
    grid.append(link);
  }
  bloque.append(
    grid,
    nodo("h2", "Accesos"),
    tarjetas(FUNCIONALIDADES_POR_ROL.ADMIN_BACKOFFICE),
    nodo("h2", "Actividad reciente"),
    eventos(r.recientes),
    enlace("Ver todo el historial", "historial")
  );
  return bloque;
}
function filtrosListado(ruta, campos, params) {
  const form = nodo("form"),
    grupo = nodo("fieldset");
  grupo.append(nodo("legend", "Filtros"));
  for (const [clave, titulo, tipo, opciones] of campos) {
    const label = nodo("label", titulo);
    let control;
    if (opciones) {
      control = nodo("select");
      for (const [v, t] of opciones) {
        const o = nodo("option", t);
        o.value = v;
        control.append(o);
      }
    } else {
      control = nodo("input");
      control.type = tipo;
    }
    control.name = clave;
    if (tipo === "checkbox") {
      control.value = "1";
      control.checked = params.get(clave) === "1";
    } else control.value = params.get(clave) || "";
    label.append(control);
    grupo.append(label);
  }
  grupo.append(nodo("button", "Aplicar filtros"), enlace("Limpiar", ruta));
  form.append(grupo);
  form.onsubmit = (e) => {
    e.preventDefault();
    const consulta = new URLSearchParams();
    for (const [k, v] of new FormData(form)) {
      if (v.trim()) consulta.set(k, v.trim());
    }
    location.hash = ruta + "?" + consulta.toString();
  };
  return form;
}
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
function opciones(valores) {
  return [["", "Todos"], ...valores.map((v) => [v, v])];
}
let bajaPendiente;
function confirmarBaja(tipo, fila) {
  bajaPendiente = { tipo, id: fila.id };
  $("titulo-confirmacion").textContent = "Eliminar " + tipo;
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
    const { tipo, id } = bajaPendiente;
    await api("/admin/elementos/" + tipo + "/" + id + "/eliminar", { motivo, confirmado: true });
    $("confirmacion").close();
    // Retener el acceso al detalle y al historial tras retirar el elemento del listado habitual.
    const modulo = tipo === "cuenta" ? "cuentas" : "contratos";
    const destino = modulo + "?incluir_eliminados=1&detalle=" + id;
    if (location.hash.slice(1) === destino) await navegar();
    else {
      location.hash = destino;
      await new Promise((resolve) =>
        window.addEventListener("hashchange", resolve, { once: true })
      );
    }
    $("aviso").textContent = "Eliminación registrada correctamente.";
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
  const campos = [
    ["Identificador", fila.id],
    ["Estado", fila.estado],
    ["Eliminación", fila.eliminado ? "Eliminado" : "Vigente"],
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
      ["Dador de carga", fila.id_empresa_generadora],
      ["Transportista", fila.id_transportista],
      ["Carga", fila.tipo_carga],
      ["Monto total", fila.monto_total + " " + fila.moneda]
    );
  f.append(
    enlace("Volver al listado", ruta, Object.fromEntries(anterior)),
    ficha(campos),
    enlace("Consultar historial del elemento", "historial", { tipo, elemento_id: fila.id })
  );
  let razon = "";
  if (fila.eliminado) razon = "Este elemento ya fue eliminado.";
  else if (tipo === "contrato" && fila.estado !== "PUBLICADO")
    razon = "Solo se pueden eliminar contratos actualmente en PUBLICADO.";
  else if (tipo === "cuenta" && fila.rol === "ADMIN_BACKOFFICE")
    razon =
      "Las cuentas administrativas están protegidas. El panel solo permite eliminar cuentas de transportistas y dadores de carga.";
  if (razon) f.append(nodo("p", razon));
  else {
    const b = boton("Eliminar " + tipo, () => confirmarBaja(tipo, fila));
    b.classList.add("peligro");
    f.append(b);
  }
  return f;
}
async function elementosAdmin(ruta, params) {
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
      : nodo("p", "El elemento ya no aparece en esta consulta.");
  }
  const campos = [
    ["incluir_eliminados", contrato ? "Incluir eliminados" : "Incluir eliminadas", "checkbox"],
  ];
  if (contrato) campos.push(["estado", "Estado", null, opciones(estadosContrato)]);
  const f = document.createDocumentFragment();
  f.append(filtrosListado(ruta, campos, params));
  if (!contrato && !incluir) f.append(nodo("p", "Cuentas activas"));
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
        contrato ? fila.estado : nombresRol[fila.rol],
        fila.id,
        fila.eliminado ? "Eliminado" : "Vigente",
        enlace("Ver detalle", ruta, { ...Object.fromEntries(params), detalle: fila.id }),
      ]),
      "No hay elementos que coincidan con los filtros."
    )
  );
  return f;
}
function valoresEvento(valor) {
  return valor
    ? valor.estado + " · " + (valor.eliminado ? "Eliminado" : "Vigente")
    : "Sin registro";
}
async function historialAdmin(params) {
  const consulta = new URLSearchParams(params);
  consulta.delete("detalle");
  const filas = await api("/admin/historial?" + consulta);
  const f = document.createDocumentFragment(),
    detalle = params.get("detalle");
  if (detalle) {
    const e = filas.find((fila) => fila.id === detalle);
    f.append(enlace("Volver al historial", "historial", Object.fromEntries(consulta)));
    if (e)
      f.append(
        ficha([
          ["Operación", e.id],
          ["Fecha y hora (UTC)", fechaUTC(e.fecha)],
          ["Administrador", e.administrador],
          ["ID administrador", e.administrador_id],
          ["Acción", etiquetasAccion[e.accion]],
          ["Elemento", e.tipo + " · " + e.elemento_id],
          ["Motivo", e.motivo || "Sin motivo informado"],
          ["Antes", valoresEvento(e.anterior)],
          ["Después", valoresEvento(e.posterior)],
          ["Resultado", e.resultado],
          ["Causa", e.causa],
        ])
      );
    else f.append(nodo("p", "No se encontró la operación."));
    return f;
  }
  f.append(
    filtrosListado(
      "historial",
      [
        ["desde", "Desde (UTC)", "date"],
        ["hasta", "Hasta (UTC)", "date"],
        ["administrador", "Nombre o ID de administrador", "text"],
        ["accion", "Acción", null, [["", "Todas"], ...Object.entries(etiquetasAccion)]],
        ["resultado", "Resultado", null, opciones(["Completado", "Rechazado"])],
        ["tipo", "Tipo de elemento", null, opciones(["contrato", "cuenta"])],
        ["elemento_id", "ID del elemento", "text"],
      ],
      params
    ),
    eventos(filas, Object.fromEntries(consulta))
  );
  return f;
}
async function vistaAdmin(ruta, params) {
  if (ruta === "inicio") return inicioAdmin();
  if (ruta === "historial") return historialAdmin(params);
  return elementosAdmin(ruta, params);
}
