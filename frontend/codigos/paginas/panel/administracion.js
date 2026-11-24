/* Las fechas y los filtros usan UTC, igual que los indicadores calculados por FastAPI. */
const etiquetasAccion = {
  cancelar_contrato: "Cancelar contrato",
  eliminar_contrato: "Eliminar contrato",
  eliminar_cuenta: "Eliminar cuenta",
};

const fechaUTC = (valor) =>
  new Intl.DateTimeFormat("es-CL", {
    dateStyle: "short",
    timeStyle: "medium",
    timeZone: "UTC",
  }).format(new Date(valor));

function elementoEventoNodo(e) {
  const wrap = nodo("div", null, "acciones-grupo");
  wrap.append(nodo("span", e.tipo, "badge badge-neutro"), celdaId(e.elemento_id));
  return wrap;
}

function eventos(filas, filtros = {}) {
  return tabla(
    ["Fecha y hora (UTC)", "Administrador", "Acción", "Elemento", "Resultado", "Detalle"],
    filas.map((e) => [
      nodo("span", fechaUTC(e.fecha), "num-tabular"),
      e.administrador,
      etiquetasAccion[e.accion] || e.accion,
      elementoEventoNodo(e),
      badgeEstado(e.resultado),
      enlace("Ver detalle", "historial", { ...filtros, detalle: e.id }),
    ]),
    "No hay acciones registradas para esta consulta."
  );
}

async function inicioAdmin() {
  const r = await api("/admin/resumen"),
    bloque = document.createDocumentFragment(),
    grid = nodo("div", null, "rejilla-kpi");

  bloque.append(
    nodo(
      "p",
      "Gestiona los contratos, las cuentas y las acciones administrativas de la plataforma.",
      "subtitulo-seccion"
    )
  );

  for (const kpi of [
    {
      titulo: "Contratos publicados",
      valor: r.publicados,
      modulo: "contratos",
      filtros: { estado: "PUBLICADO" },
      iconoNombre: "contratos",
    },
    {
      titulo: "Cuentas activas",
      valor: r.activas,
      modulo: "cuentas",
      filtros: { activas: "1" },
      iconoNombre: "cuentas",
    },
    {
      titulo: "Acciones administrativas de hoy (UTC)",
      valor: r.acciones,
      modulo: "historial",
      filtros: { desde: r.hoy, hasta: r.hoy, resultado: "Completado" },
      iconoNombre: "historial",
    },
  ]) {
    grid.append(tarjetaKpi(kpi));
  }

  const pieHistorial = nodo("div", null, "acciones-barra");
  pieHistorial.style.marginTop = "14px";
  const linkHistorial = enlace("Ver todo el historial", "historial");
  linkHistorial.append(icono("flechaDer", 14));
  pieHistorial.append(linkHistorial);

  bloque.append(
    grid,
    nodo("h2", "Accesos"),
    tarjetas(FUNCIONALIDADES_POR_ROL.ADMIN_BACKOFFICE),
    nodo("h2", "Actividad reciente"),
    eventos(r.recientes),
    pieHistorial
  );
  return bloque;
}

function filtrosListado(ruta, campos, params) {
  const form = nodo("form", null, "barra-filtros");
  const titulo = nodo("p", null, "barra-filtros-titulo");
  titulo.append(icono("filtro", 14), nodo("span", "Filtros"));
  const grid = nodo("div", null, "barra-filtros-grid");

  for (const [clave, etiqueta, tipo, opcionesLista] of campos) {
    const label = nodo("label", tipo === "checkbox" ? null : etiqueta);
    let control;
    if (opcionesLista) {
      control = nodo("select");
      for (const [v, t] of opcionesLista) {
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
      label.className = "filtro-check";
      control.value = "1";
      control.checked = params.get(clave) === "1";
      label.append(control, nodo("span", etiqueta));
    } else {
      control.value = params.get(clave) || "";
      label.append(control);
    }
    grid.append(label);
  }

  const acciones = nodo("div", null, "barra-filtros-acciones");
  const btnAplicar = nodo("button", "Aplicar filtros", "btn-primario");
  btnAplicar.type = "submit";
  acciones.append(btnAplicar, enlace("Limpiar", ruta));

  form.append(titulo, grid, acciones);
  form.onsubmit = (e) => {
    e.preventDefault();
    const consulta = new URLSearchParams();
    for (const [k, v] of new FormData(form)) {
      if (v.trim()) consulta.set(k, v.trim());
    }
    location.hash = ruta + (consulta.toString() ? "?" + consulta.toString() : "");
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
    if (location.hash.slice(1) === destino) await navegar();
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
    const barra = nodo("div", null, "acciones-barra");
    const btnVolver = enlace("Volver al historial", "historial", Object.fromEntries(consulta));
    btnVolver.prepend(icono("flechaIzq", 15));
    barra.append(btnVolver);
    f.append(barra);

    if (e)
      f.append(
        ficha([
          ["Operación", celdaId(e.id)],
          ["Fecha y hora (UTC)", nodo("span", fechaUTC(e.fecha), "num-tabular")],
          ["Administrador", e.administrador],
          ["ID administrador", celdaId(e.administrador_id)],
          ["Acción", etiquetasAccion[e.accion] || e.accion],
          ["Elemento", elementoEventoNodo(e)],
          ["Motivo", e.motivo || "Sin motivo informado"],
          ["Antes", valoresEvento(e.anterior)],
          ["Después", valoresEvento(e.posterior)],
          ["Resultado", badgeEstado(e.resultado)],
          ["Causa", e.causa || "—"],
        ])
      );
    else f.append(estadoVacio("No se encontró la operación."));
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

async function validacionesAdmin() {
  const [documentos, dadores] = await Promise.all([
    api("/onboarding/admin/documentos"),
    api("/onboarding/admin/dadores"),
  ]);
  const f = document.createDocumentFragment();
  f.append(
    nodo(
      "p",
      "Revisa y aprueba o rechaza la documentación de transportistas y los perfiles tributarios de dadores pendientes.",
      "subtitulo-seccion"
    )
  );

  async function resolverDocumento(id, estado) {
    try {
      await api("/onboarding/admin/documentos/" + id + "/validar", { estado }, { method: "PATCH" });
      await navegar();
      mostrarAviso("Documento marcado como " + estado + ".", "exito");
    } catch (error) {
      mostrarAviso(error.message, "error");
    }
  }

  async function resolverDador(id, estado_validacion) {
    try {
      await api(
        "/onboarding/admin/dadores/" + id + "/validar",
        { estado_validacion },
        { method: "PATCH" }
      );
      await navegar();
      mostrarAviso("Perfil de dador marcado como " + estado_validacion + ".", "exito");
    } catch (error) {
      mostrarAviso(error.message, "error");
    }
  }

  f.append(
    nodo("h2", "Documentos de transportistas pendientes (" + documentos.length + ")"),
    tabla(
      ["Tipo de documento", "Archivo", "Usuario ID", "Fecha carga", "Estado", "Acciones"],
      documentos.map((doc) => {
        const acciones = nodo("div", null, "acciones-grupo");
        acciones.append(
          boton("Aprobar", () => resolverDocumento(doc.id, "APROBADO"), "btn-exito btn-sm"),
          boton("Rechazar", () => resolverDocumento(doc.id, "RECHAZADO"), "peligro btn-sm")
        );
        return [
          doc.tipo,
          doc.archivo,
          celdaId(doc.user_id),
          nodo("span", fechaLocal(doc.created_at), "num-tabular"),
          badgeEstado(doc.estado),
          acciones,
        ];
      }),
      "No hay documentos de transportistas pendientes de revisión."
    )
  );

  f.append(
    nodo("h2", "Perfiles tributarios de dadores pendientes (" + dadores.length + ")"),
    tabla(
      ["RUT empresa", "Razón social", "Dirección", "Correo facturación", "Estado", "Acciones"],
      dadores.map((dador) => {
        const acciones = nodo("div", null, "acciones-grupo");
        acciones.append(
          boton("Aprobar", () => resolverDador(dador.id, "APROBADO"), "btn-exito btn-sm"),
          boton("Rechazar", () => resolverDador(dador.id, "RECHAZADO"), "peligro btn-sm")
        );
        return [
          nodo("span", dador.rut_id_empresa, "num-tabular"),
          dador.datos_facturacion?.razon_social,
          dador.datos_facturacion?.direccion,
          dador.datos_facturacion?.correo_facturacion,
          badgeEstado(dador.estado_validacion),
          acciones,
        ];
      }),
      "No hay perfiles tributarios de dadores pendientes de validación."
    )
  );

  return f;
}

async function configuracionAdmin() {
  const cfg = await api("/configuracion");
  const f = document.createDocumentFragment();
  f.append(
    nodo(
      "p",
      "Ajusta las reglas de negocio globales vigentes para la creación y validación de contratos.",
      "subtitulo-seccion"
    )
  );

  const form = nodo("form", null, "form-panel");
  const grid = nodo("div", null, "form-grid");

  const labelIva = nodo("label", "Tasa de IVA (decimal entre 0 y 1)");
  const inputIva = nodo("input");
  inputIva.type = "number";
  inputIva.name = "iva_porcentaje";
  inputIva.min = "0";
  inputIva.max = "1";
  inputIva.step = "0.01";
  inputIva.required = true;
  inputIva.value = String(cfg.iva_porcentaje);
  labelIva.append(inputIva, nodo("small", "Ejemplo: 0.19 equivale a 19%.", "texto-suave"));

  const labelTol = nodo("label", "Tolerancia financiera máxima");
  const inputTol = nodo("input");
  inputTol.type = "number";
  inputTol.name = "tolerancia_max";
  inputTol.min = "0";
  inputTol.step = "0.01";
  inputTol.required = true;
  inputTol.value = String(cfg.tolerancia_max);
  labelTol.append(inputTol, nodo("small", "Margen máximo en cuadratura de montos.", "texto-suave"));

  const labelAnt = nodo("label", "Anticipación mínima de salida (horas)");
  const inputAnt = nodo("input");
  inputAnt.type = "number";
  inputAnt.name = "anticipacion_min_h";
  inputAnt.min = "0";
  inputAnt.step = "1";
  inputAnt.required = true;
  inputAnt.value = String(cfg.anticipacion_min_h);
  labelAnt.append(
    inputAnt,
    nodo("small", "Horas mínimas antes de la salida programada.", "texto-suave")
  );

  grid.append(labelIva, labelTol, labelAnt);

  const acciones = nodo("div", null, "acciones-grupo");
  const btnGuardar = nodo("button", "Guardar configuración", "btn-primario");
  btnGuardar.type = "submit";
  acciones.append(btnGuardar);

  form.append(grid, acciones);
  form.onsubmit = async (e) => {
    e.preventDefault();
    btnGuardar.disabled = true;
    try {
      const actualizado = await api(
        "/configuracion",
        {
          iva_porcentaje: Number(inputIva.value),
          tolerancia_max: Number(inputTol.value),
          anticipacion_min_h: Number(inputAnt.value),
        },
        { method: "PATCH" }
      );
      inputIva.value = String(actualizado.iva_porcentaje);
      inputTol.value = String(actualizado.tolerancia_max);
      inputAnt.value = String(actualizado.anticipacion_min_h);
      mostrarAviso("Configuración global actualizada correctamente.", "exito");
    } catch (error) {
      mostrarAviso(error.message, "error");
    } finally {
      btnGuardar.disabled = false;
    }
  };

  f.append(form);
  return f;
}

async function vistaAdmin(ruta, params) {
  if (ruta === "inicio") return inicioAdmin();
  if (ruta === "historial") return historialAdmin(params);
  if (ruta === "validaciones") return validacionesAdmin();
  if (ruta === "configuracion") return configuracionAdmin();
  return elementosAdmin(ruta, params);
}
