const $ = (id) => document.getElementById(id);

let usuarioSesion = null;
let reglasNegocio = {
  iva_porcentaje: 0.19,
  tolerancia_max: 0.01,
  anticipacion_min_h: 2,
};
let modoEnvio = "PUBLICADO";

function resolverUrlRetorno() {
  const params = new URLSearchParams(window.location.search);
  const desde = params.get("desde");
  if (desde === "catalogo") {
    return { href: "../Principal/principal.html", texto: "← Volver al catálogo" };
  }
  if (desde === "panel" || document.referrer.includes("/panel/")) {
    return { href: "../panel/index.html#contratos", texto: "← Volver a mis contratos" };
  }
  return { href: "../Principal/principal.html", texto: "← Volver al catálogo" };
}

function inicializarIconosCrear() {
  if (!window.MVIconos) return;
  const logo = $("logo-crear");
  if (logo) logo.replaceChildren(window.MVIconos.crear("isotipo", { size: 20 }));
}

function volverALogin() {
  window.MVApi.volverALogin();
}

async function solicitarApi(ruta, opciones = {}) {
  return window.MVApi.solicitar(ruta, {
    ...opciones,
    mensajeSinSesion: "Debes iniciar sesión para continuar.",
    mensajeExpirada: "Tu sesión ha expirado.",
    mensajeError: "No se pudo completar la operación.",
  });
}

function extraerMensajeError(cuerpo) {
  return window.MVApi.extraerMensajeError(cuerpo, "No se pudo completar la operación.");
}

function mostrarAlerta(mensaje, tipo = "error") {
  const alerta = $("alerta-general");
  if (!mensaje) {
    alerta.textContent = "";
    alerta.className = "alerta oculto";
    return;
  }
  alerta.textContent = mensaje;
  alerta.className = `alerta ${tipo}`;
  alerta.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

function establecerErrorCampo(id, msg) {
  const input = $(id);
  const errorEl = $("error-" + id);
  if (input && input.tagName !== "P") {
    input.classList.toggle("invalido", Boolean(msg));
  }
  if (errorEl) {
    errorEl.textContent = msg || "";
    errorEl.classList.toggle("oculto", !msg);
  }
}

function limpiarMarcasInvalidas() {
  for (const el of $("form-contrato").querySelectorAll(".invalido")) {
    el.classList.remove("invalido");
  }
  for (const err of $("form-contrato").querySelectorAll(".error-inline")) {
    err.textContent = "";
    err.classList.add("oculto");
  }
}

function formatoLocalDatetime(fecha) {
  const pad = (n) => String(n).padStart(2, "0");
  return (
    fecha.getFullYear() +
    "-" +
    pad(fecha.getMonth() + 1) +
    "-" +
    pad(fecha.getDate()) +
    "T" +
    pad(fecha.getHours()) +
    ":" +
    pad(fecha.getMinutes())
  );
}

function inicializarFechasPorDefecto() {
  const ahora = Date.now();
  const minHoras = Math.max(2, Number(reglasNegocio.anticipacion_min_h) || 2);
  const cierre = new Date(ahora + (minHoras + 1) * 3600000);
  const salida = new Date(ahora + (minHoras + 4) * 3600000);
  const llegada = new Date(ahora + (minHoras + 12) * 3600000);

  if (!$("f_cierre_postulaciones").value) {
    $("f_cierre_postulaciones").value = formatoLocalDatetime(cierre);
  }
  if (!$("f_estimada_salida").value) {
    $("f_estimada_salida").value = formatoLocalDatetime(salida);
  }
  if (!$("f_estimada_llegada").value) {
    $("f_estimada_llegada").value = formatoLocalDatetime(llegada);
  }
}

function actualizarReglasVisualesCarga() {
  const tipo = $("tipo_carga").value;
  const requiereTermo = tipo === "REFRIGERADA" || tipo === "PERECEDERA";
  const requiereOnu = tipo === "PELIGROSA";
  const requiereEmbalaje = tipo === "FRAGIL";
  const requiereBlindaje = tipo === "VALORES";

  $("wrap-termo").classList.toggle("requerido", requiereTermo);
  $("wrap-blindaje").classList.toggle("requerido", requiereBlindaje);
  $("wrap-onu").classList.toggle("campo-requerido", requiereOnu);
  $("wrap-embalaje").classList.toggle("campo-requerido", requiereEmbalaje);

  if (requiereTermo) $("requiere_termo").checked = true;
  if (requiereBlindaje) $("req_blindaje").checked = true;

  $("numero_onu").required = requiereOnu;
  $("req_embalaje").required = requiereEmbalaje;

  actualizarResumen();
}

function recalcularMontos(desdeIvaManual = false) {
  const moneda = $("moneda").value;
  const neto = Number($("monto_neto").value);
  const tasa = Number(reglasNegocio.iva_porcentaje ?? 0.19);

  $("etiqueta-iva").innerHTML =
    `IVA (${Math.round(tasa * 100)}%) <abbr title="Obligatorio">*</abbr>`;
  $("ayuda-iva").textContent =
    moneda === "CLP"
      ? `En CLP debe corresponder al ${Math.round(tasa * 100)}% del neto.`
      : "Ingresa el IVA aplicable (0 si está exento).";

  if (!Number.isFinite(neto) || neto <= 0) {
    if (!desdeIvaManual) $("monto_iva").value = "";
    $("monto_total").value = "";
    actualizarResumen();
    return;
  }

  let iva;
  if (desdeIvaManual && moneda !== "CLP") {
    iva = Number($("monto_iva").value) || 0;
  } else {
    iva = moneda === "CLP" ? Math.round(neto * tasa) : Number((neto * tasa).toFixed(2));
    $("monto_iva").value = String(iva);
  }

  const total = moneda === "CLP" ? Math.round(neto + iva) : Number((neto + iva).toFixed(2));
  $("monto_total").value = String(total);
  actualizarResumen();
}

function formatearMoneda(valor, moneda) {
  if (!Number.isFinite(valor) || valor <= 0) return "$0";
  if (moneda === "CLP") {
    return new Intl.NumberFormat("es-CL", {
      style: "currency",
      currency: "CLP",
      maximumFractionDigits: 0,
    }).format(valor);
  }
  return `${valor.toLocaleString("es-CL")} ${moneda}`;
}

function actualizarIndicadorCapacidad(peso, cap) {
  const wrap = $("ocupacion-wrap");
  const barra = $("barra-capacidad");
  const texto = $("texto-capacidad");
  if (!wrap || !barra || !texto) return;

  if (!Number.isFinite(peso) || !Number.isFinite(cap) || peso <= 0 || cap <= 0) {
    wrap.classList.add("oculto");
    return;
  }

  const porcentaje = Math.round((peso / cap) * 100);
  const excedido = peso > cap;
  wrap.classList.remove("oculto");
  wrap.classList.toggle("excedido", excedido);
  barra.style.width = Math.min(100, porcentaje) + "%";
  texto.textContent = excedido ? `${porcentaje}% (excede capacidad)` : `${porcentaje}%`;
}

function actualizarResumen() {
  const origen = $("origen").value.trim().toUpperCase();
  const destino = $("destino").value.trim().toUpperCase();
  $("resumen-origen").textContent = origen || "Origen sin definir";
  $("resumen-destino").textContent = destino || "Destino sin definir";

  const salidaVal = $("f_estimada_salida").value;
  $("resumen-salida").textContent = salidaVal
    ? new Date(salidaVal).toLocaleString("es-CL", { dateStyle: "short", timeStyle: "short" })
    : "—";

  $("resumen-carga").textContent = $("tipo_carga").value;

  const peso = Number($("peso_total").value);
  const cap = Number($("input_camionKG").value);
  $("resumen-capacidad").textContent =
    peso > 0 || cap > 0 ? `${peso > 0 ? peso : "—"} KG / ${cap > 0 ? cap : "—"} KG` : "—";
  actualizarIndicadorCapacidad(peso, cap);

  const reqs = [];
  if ($("requiere_termo").checked) reqs.push("Equipo termo");
  if ($("req_blindaje").checked) reqs.push("Blindado");
  if ($("numero_onu").value.trim()) reqs.push("ONU " + $("numero_onu").value.trim().toUpperCase());
  if ($("req_embalaje").value.trim()) reqs.push("Embalaje");

  const reqWrap = $("resumen-requisitos");
  reqWrap.replaceChildren();
  if (!reqs.length) {
    reqWrap.textContent = "Ninguno";
  } else {
    for (const r of reqs) {
      const chip = document.createElement("span");
      chip.className = "chip-mini";
      chip.textContent = r;
      reqWrap.append(chip);
    }
  }

  const total = Number($("monto_total").value);
  $("resumen-total").textContent = formatearMoneda(total, $("moneda").value);
}

function validarFormulario() {
  limpiarMarcasInvalidas();
  const errores = [];
  let primerInvalido = null;

  const marcar = (id, msg) => {
    establecerErrorCampo(id, msg);
    errores.push(msg);
    if (!primerInvalido && $(id)) primerInvalido = $(id);
  };

  const origen = $("origen").value.trim().toUpperCase();
  const destino = $("destino").value.trim().toUpperCase();
  if (origen.length < 3) marcar("origen", "El origen debe tener al menos 3 caracteres.");
  if (destino.length < 3) marcar("destino", "El destino debe tener al menos 3 caracteres.");
  if (origen.length >= 3 && origen === destino) {
    marcar("destino", "El origen y el destino no pueden ser idénticos.");
  }

  const cierre = new Date($("f_cierre_postulaciones").value);
  const salida = new Date($("f_estimada_salida").value);
  const llegada = new Date($("f_estimada_llegada").value);
  const minHoras = Number(reglasNegocio.anticipacion_min_h ?? 2);
  const limiteSalida = new Date(Date.now() + minHoras * 3600000);

  if (Number.isNaN(cierre.getTime())) {
    marcar("f_cierre_postulaciones", "Ingresa una fecha de cierre de postulaciones válida.");
  }
  if (Number.isNaN(salida.getTime())) {
    marcar("f_estimada_salida", "Ingresa una fecha estimada de salida válida.");
  } else if (salida <= limiteSalida) {
    marcar(
      "f_estimada_salida",
      `La salida debe programarse con al menos ${minHoras} horas de anticipación.`
    );
  }
  if (Number.isNaN(llegada.getTime())) {
    marcar("f_estimada_llegada", "Ingresa una fecha estimada de llegada válida.");
  } else if (!Number.isNaN(salida.getTime()) && llegada <= salida) {
    marcar("f_estimada_llegada", "La fecha de llegada debe ser posterior a la salida.");
  }
  if (!Number.isNaN(cierre.getTime()) && !Number.isNaN(salida.getTime()) && cierre > salida) {
    marcar(
      "f_cierre_postulaciones",
      "El cierre de postulaciones no puede ser posterior a la salida."
    );
  }

  const cap = Number($("input_camionKG").value);
  const peso = Number($("peso_total").value);
  if (!Number.isFinite(cap) || cap <= 0) {
    marcar("input_camionKG", "La capacidad del camión debe ser mayor a 0 KG.");
  }
  if (!Number.isFinite(peso) || peso <= 0) {
    marcar("peso_total", "El peso total de la carga debe ser mayor a 0 KG.");
  } else if (Number.isFinite(cap) && cap > 0 && peso > cap) {
    marcar("peso_total", "El peso total supera la capacidad máxima del camión.");
  }

  const tipo = $("tipo_carga").value;
  if ((tipo === "REFRIGERADA" || tipo === "PERECEDERA") && !$("requiere_termo").checked) {
    const msg = `La carga ${tipo} requiere activar el equipo termo/refrigeración.`;
    establecerErrorCampo("checks", msg);
    errores.push(msg);
  }
  if (tipo === "VALORES" && !$("req_blindaje").checked) {
    const msg = "La carga de VALORES requiere obligatoriamente camión blindado.";
    establecerErrorCampo("checks", msg);
    errores.push(msg);
  }

  const onu = $("numero_onu").value.trim();
  if (tipo === "PELIGROSA") {
    if (!/^(UN)?\d{4}$/i.test(onu)) {
      marcar("numero_onu", "La carga PELIGROSA requiere un código ONU de 4 dígitos (ej: UN1203).");
    }
  }
  const embalaje = $("req_embalaje").value.trim();
  if (tipo === "FRAGIL" && embalaje.length < 10) {
    marcar(
      "req_embalaje",
      "La carga FRÁGIL requiere especificación de embalaje de al menos 10 caracteres."
    );
  } else if (embalaje.length > 0 && embalaje.length < 10) {
    marcar("req_embalaje", "Si indicas embalaje, debe tener al menos 10 caracteres.");
  }

  const neto = Number($("monto_neto").value);
  const iva = Number($("monto_iva").value);
  const total = Number($("monto_total").value);
  if (!Number.isFinite(neto) || neto <= 0) {
    marcar("monto_neto", "El monto neto debe ser mayor a 0.");
  }
  if (!Number.isFinite(iva) || iva < 0) {
    marcar("monto_iva", "El monto del IVA no puede ser negativo.");
  }
  if (!Number.isFinite(total) || total <= 0) {
    marcar("monto_total", "El monto total debe ser mayor a 0.");
  }

  return { errores, primerInvalido };
}

function construirPayload() {
  const volumenRaw = $("volumen_m3").value.trim();
  const distanciaRaw = $("distancia_km").value.trim();
  const onuRaw = $("numero_onu").value.trim();
  const embalajeRaw = $("req_embalaje").value.trim();

  return {
    id_empresa_generadora: usuarioSesion.id,
    origen: $("origen").value.trim(),
    destino: $("destino").value.trim(),
    f_cierre_postulaciones: new Date($("f_cierre_postulaciones").value).toISOString(),
    f_estimada_salida: new Date($("f_estimada_salida").value).toISOString(),
    f_estimada_llegada: new Date($("f_estimada_llegada").value).toISOString(),
    input_camionKG: Number($("input_camionKG").value),
    tipo_carga: $("tipo_carga").value,
    peso_total: Number($("peso_total").value),
    volumen_m3: volumenRaw === "" ? null : Number(volumenRaw),
    distancia_km: distanciaRaw === "" ? null : Number(distanciaRaw),
    requiere_termo: $("requiere_termo").checked,
    numero_onu: onuRaw === "" ? null : onuRaw.toUpperCase(),
    req_embalaje: embalajeRaw === "" ? null : embalajeRaw,
    req_blindaje: $("req_blindaje").checked,
    moneda: $("moneda").value,
    monto_neto: Number($("monto_neto").value),
    monto_iva: Number($("monto_iva").value),
    monto_total: Number($("monto_total").value),
  };
}

async function enviarContrato(evento) {
  evento.preventDefault();
  mostrarAlerta("");
  $("resultado-creacion").classList.add("oculto");

  const { errores, primerInvalido } = validarFormulario();
  if (errores.length > 0) {
    const sufijo = errores.length > 1 ? ` (+${errores.length - 1} campos más por revisar)` : "";
    mostrarAlerta(errores[0] + sufijo, "error");
    if (primerInvalido) primerInvalido.focus();
    return;
  }

  const btnBorrador = $("btn-guardar-borrador");
  const btnPublicar = $("btn-crear-publicar");
  btnBorrador.disabled = true;
  btnPublicar.disabled = true;

  try {
    const payload = construirPayload();
    let contrato = await solicitarApi("/contratos", {
      method: "POST",
      body: JSON.stringify(payload),
    });

    if (modoEnvio === "PUBLICADO") {
      contrato = await solicitarApi(`/contratos/${contrato.id}/estado`, {
        method: "PATCH",
        body: JSON.stringify({ nuevo_estado: "PUBLICADO" }),
      });
    }

    const estadoTexto = contrato.estado === "PUBLICADO" ? "publicado" : "guardado como borrador";
    mostrarAlerta(
      `Contrato ${estadoTexto} correctamente (${contrato.origen} → ${contrato.destino}).`,
      "exito"
    );
    $("resultado-titulo").textContent =
      contrato.estado === "PUBLICADO" ? "Contrato publicado" : "Borrador guardado";
    $("resultado-detalle").textContent = `ID: ${contrato.id} · Estado: ${contrato.estado}`;
    $("resultado-creacion").classList.remove("oculto");
  } catch (error) {
    mostrarAlerta(error.message || "Error al crear el contrato.", "error");
  } finally {
    btnBorrador.disabled = false;
    btnPublicar.disabled = false;
  }
}

async function cargarEstadoKyc() {
  try {
    const perfil = await solicitarApi("/onboarding/dador/perfil", {
      headers: { "X-User-Id": usuarioSesion.id },
    });
    const badge = $("etiqueta-kyc");
    badge.classList.remove("oculto");
    const clase = window.MVIconos
      ? window.MVIconos.claseBadgeEstado(perfil.estado_validacion)
      : "badge-info";
    badge.className = "badge " + clase;
    badge.textContent =
      perfil.estado_validacion === "APROBADO" ? "KYC Aprobado" : `KYC: ${perfil.estado_validacion}`;
  } catch {
    // Si no tiene perfil o no aplica, no bloqueamos la carga de la pantalla.
  }
}

async function inicializar() {
  inicializarIconosCrear();

  const retorno = resolverUrlRetorno();
  const btnVolver = $("boton-volver");
  if (btnVolver) {
    btnVolver.textContent = retorno.texto;
    btnVolver.addEventListener("click", () => {
      window.location.href = retorno.href;
    });
  }
  const enlaceResultado = $("enlace-resultado-volver");
  if (enlaceResultado) {
    enlaceResultado.href = retorno.href;
  }

  try {
    usuarioSesion = await solicitarApi("/auth/sesion");
    $("resumen-empresa").textContent = `${usuarioSesion.nombre} (${usuarioSesion.email})`;
    $("subtitulo-usuario").textContent =
      `Sesión activa: ${usuarioSesion.nombre}. Completa los datos para emitir tu contrato.`;

    if (usuarioSesion.rol === "TRANSPORTISTA") {
      mostrarAlerta(
        "Tu cuenta tiene rol Transportista. Solo los Dadores de carga con verificación KYC aprobada pueden emitir contratos.",
        "error"
      );
    }

    try {
      const cfg = await solicitarApi("/configuracion");
      if (cfg && typeof cfg === "object") {
        reglasNegocio = { ...reglasNegocio, ...cfg };
      }
    } catch {
      // Mantiene valores por defecto si no se puede leer /configuracion.
    }

    $("ayuda-anticipacion").textContent =
      `Mínimo ${reglasNegocio.anticipacion_min_h} horas de anticipación.`;

    inicializarFechasPorDefecto();
    actualizarReglasVisualesCarga();
    cargarEstadoKyc();
  } catch (error) {
    mostrarAlerta(error.message || "No se pudo verificar tu sesión.", "error");
  }

  $("btn-guardar-borrador").addEventListener("click", () => {
    modoEnvio = "BORRADOR";
  });

  $("btn-crear-publicar").addEventListener("click", () => {
    modoEnvio = "PUBLICADO";
  });

  $("btn-nuevo-contrato").addEventListener("click", () => {
    $("form-contrato").reset();
    $("resultado-creacion").classList.add("oculto");
    mostrarAlerta("");
    limpiarMarcasInvalidas();
    inicializarFechasPorDefecto();
    actualizarReglasVisualesCarga();
    recalcularMontos();
  });

  $("tipo_carga").addEventListener("change", actualizarReglasVisualesCarga);
  $("moneda").addEventListener("change", () => recalcularMontos(false));
  $("monto_neto").addEventListener("input", () => recalcularMontos(false));
  $("monto_iva").addEventListener("input", () => recalcularMontos(true));

  for (const id of [
    "origen",
    "destino",
    "f_estimada_salida",
    "peso_total",
    "input_camionKG",
    "numero_onu",
    "req_embalaje",
  ]) {
    $(id).addEventListener("input", actualizarResumen);
  }
  for (const id of ["requiere_termo", "req_blindaje"]) {
    $(id).addEventListener("change", () => {
      establecerErrorCampo("checks", "");
      actualizarResumen();
    });
  }

  $("form-contrato")
    .querySelectorAll("input, select, textarea")
    .forEach((campo) => {
      campo.addEventListener("input", () => establecerErrorCampo(campo.id, ""));
      campo.addEventListener("change", () => establecerErrorCampo(campo.id, ""));
    });

  $("form-contrato").addEventListener("submit", enviarContrato);
}

document.addEventListener("DOMContentLoaded", inicializar);
