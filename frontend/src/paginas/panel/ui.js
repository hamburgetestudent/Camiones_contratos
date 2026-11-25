/* Utilidades de interfaz compartidas por las vistas del panel — MansoViaje */
import { MVApi } from "../../compartido/js/api.js";
import { MVIconos } from "../../compartido/js/iconos.js";

export const $ = (id) => document.getElementById(id);
export const contenido = $("contenido");

export function icono(nombre, size = 17) {
  return MVIconos ? MVIconos.crear(nombre, { size }) : nodo("span", "");
}

export function nodo(tag, texto, clase) {
  const el = document.createElement(tag);
  if (texto != null) el.textContent = texto;
  if (clase) el.className = clase;
  return el;
}

export function enlace(texto, modulo, filtros = {}) {
  const a = nodo("a", texto, "boton");
  const query = new URLSearchParams(filtros).toString();
  a.href = "#" + modulo + (query ? "?" + query : "");
  return a;
}

export function boton(texto, accion, clase = "") {
  const b = nodo("button", texto, clase);
  b.type = "button";
  b.addEventListener("click", accion);
  return b;
}

export function mostrarAviso(texto, tipo = "info") {
  const el = $("aviso");
  el.replaceChildren();
  if (!texto) {
    el.className = "";
    return;
  }
  const mapaIcono = { exito: "exito", error: "error", info: "info" };
  el.className = "aviso-banner aviso-" + tipo;

  const cuerpo = nodo("div", null, "aviso-banner-contenido");
  cuerpo.append(icono(mapaIcono[tipo] || "info", 17), nodo("span", texto));

  const btnCerrar = nodo("button", null, "aviso-cerrar");
  btnCerrar.type = "button";
  btnCerrar.setAttribute("aria-label", "Cerrar aviso");
  btnCerrar.append(icono("cerrar", 15));
  btnCerrar.addEventListener("click", () => mostrarAviso(""));

  el.append(cuerpo, btnCerrar);
}

export function badgeEstado(estado, textoPersonalizado) {
  if (MVIconos) return MVIconos.badgeEstado(estado, textoPersonalizado);
  return nodo("span", textoPersonalizado ?? String(estado || "—"), "badge badge-neutro");
}

export function celdaId(id) {
  const valor = String(id || "—");
  if (!id) return nodo("span", "—", "texto-suave");
  const wrap = nodo("span", null, "celda-id");
  const code = nodo("code", valor, "id-corto");
  code.title = valor;

  const btn = nodo("button", null, "btn-copiar");
  btn.type = "button";
  btn.title = "Copiar identificador";
  btn.setAttribute("aria-label", "Copiar identificador");
  btn.append(icono("copiar", 14));
  btn.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(valor);
      btn.classList.add("copiado");
      btn.replaceChildren(icono("check", 14));
      setTimeout(() => {
        btn.classList.remove("copiado");
        btn.replaceChildren(icono("copiar", 14));
      }, 1400);
    } catch {
      mostrarAviso("Identificador: " + valor, "info");
    }
  });

  wrap.append(code, btn);
  return wrap;
}

export function formatearMoneda(valor, moneda = "CLP") {
  const num = Number(valor);
  if (!Number.isFinite(num)) return "—";
  if (moneda === "CLP") {
    return new Intl.NumberFormat("es-CL", {
      style: "currency",
      currency: "CLP",
      maximumFractionDigits: 0,
    }).format(num);
  }
  return num.toLocaleString("es-CL") + " " + moneda;
}

export function fechaLocal(valor) {
  if (!valor) return "—";
  return new Intl.DateTimeFormat("es-CL", {
    dateStyle: "short",
    timeStyle: "short",
  }).format(new Date(valor));
}

export function estadoVacio(mensaje, accionEl = null) {
  const caja = nodo("div", null, "estado-vacio");
  const ico = nodo("div", null, "estado-vacio-icono");
  ico.append(icono("bandejaVacia", 22));
  caja.append(ico, nodo("p", mensaje));
  if (accionEl) caja.append(accionEl);
  return caja;
}

export function tabla(columnas, filas, vacio, accionVacio = null) {
  if (!filas.length) return estadoVacio(vacio, accionVacio);
  const caja = nodo("div", null, "tabla"),
    tbl = nodo("table"),
    cabecera = tbl.createTHead().insertRow();
  for (const nombre of columnas) {
    const th = nodo("th", nombre);
    th.scope = "col";
    cabecera.append(th);
  }
  const cuerpo = tbl.createTBody();
  for (const fila of filas) {
    const tr = cuerpo.insertRow();
    for (const valor of fila) {
      const td = tr.insertCell();
      if (valor instanceof Node) td.append(valor);
      else td.textContent = valor ?? "—";
    }
  }
  caja.append(tbl);
  return caja;
}

export function ficha(campos) {
  const dl = nodo("dl");
  for (const [etiqueta, valor] of campos) {
    dl.append(nodo("dt", etiqueta));
    const dd = nodo("dd");
    if (valor instanceof Node) dd.append(valor);
    else dd.textContent = valor ?? "—";
    dl.append(dd);
  }
  return dl;
}

export function tarjetaKpi({
  titulo,
  valor,
  modulo,
  filtros = {},
  iconoNombre = "info",
  esEstado = false,
}) {
  const link = enlace("", modulo, filtros);
  link.className = "tarjeta";

  const top = nodo("div", null, "tarjeta-cabecera");
  top.append(nodo("span", titulo, "tarjeta-kpi-titulo"));
  const ico = nodo("span", null, "tarjeta-icono");
  ico.append(icono(iconoNombre, 17));
  top.append(ico);

  link.append(top);
  if (esEstado) {
    const estadoWrap = nodo("div", null, "kpi-estado");
    estadoWrap.append(badgeEstado(valor));
    link.append(estadoWrap);
  } else {
    link.append(nodo("strong", String(valor), "indicador num-tabular"));
  }
  return link;
}

export function mostrarSkeleton() {
  const bloque = nodo("div", null, "skeleton-bloque");
  bloque.setAttribute("aria-busy", "true");
  bloque.setAttribute("aria-label", "Cargando contenido");

  const grid = nodo("div", null, "skeleton-grid");
  for (let i = 0; i < 3; i++) {
    const card = nodo("div", null, "skeleton-card");
    card.append(
      nodo("div", null, "skeleton skeleton-linea skeleton-linea--corta"),
      nodo("div", null, "skeleton skeleton-linea skeleton-linea--grande")
    );
    grid.append(card);
  }

  const tablaSk = nodo("div", null, "skeleton-card");
  for (let i = 0; i < 4; i++) {
    tablaSk.append(nodo("div", null, "skeleton skeleton-linea skeleton-linea--llena"));
  }
  bloque.append(grid, tablaSk);
  contenido.replaceChildren(bloque);
}

export function confirmarAccion({
  titulo = "Confirmar acción",
  descripcion = "",
  textoConfirmar = "Confirmar",
  variante = "btn-primario",
}) {
  const dialogo = $("confirmacion-accion");
  if (!dialogo) return Promise.resolve(true);

  $("accion-titulo").textContent = titulo;
  $("accion-descripcion").textContent = descripcion;
  const btnAceptar = $("accion-aceptar");
  const btnCancelar = $("accion-cancelar");
  btnAceptar.textContent = textoConfirmar;
  btnAceptar.className = variante;

  return new Promise((resolve) => {
    const finalizar = (resultado) => {
      btnAceptar.removeEventListener("click", onAceptar);
      btnCancelar.removeEventListener("click", onCancelar);
      dialogo.removeEventListener("cancel", onCancelar);
      if (dialogo.open) dialogo.close();
      resolve(resultado);
    };
    const onAceptar = () => finalizar(true);
    const onCancelar = () => finalizar(false);

    btnAceptar.addEventListener("click", onAceptar);
    btnCancelar.addEventListener("click", onCancelar);
    dialogo.addEventListener("cancel", onCancelar);
    dialogo.showModal();
    btnAceptar.focus();
  });
}

export async function api(ruta, datos, opcionesExtra = {}) {
  const method = opcionesExtra.method || (datos !== undefined ? "POST" : "GET");
  const opciones = { method, headers: opcionesExtra.headers };
  if (datos !== undefined) opciones.body = JSON.stringify(datos);
  return MVApi.solicitar(ruta, opciones, {
    sinSesion: "Inicia sesión.",
    expirada: "La sesión terminó.",
    error: "No se pudo completar la solicitud.",
  });
}

export function mostrarError(error, reintentar) {
  contenido.replaceChildren(
    estadoVacio(
      error.message || "No se pudo cargar la información.",
      boton("Reintentar", reintentar, "btn-primario")
    )
  );
}

export function tarjetas(items) {
  const grid = nodo("div", null, "rejilla");
  for (const item of items) {
    const tarjeta = nodo("article", null, "tarjeta");
    const top = nodo("div", null, "tarjeta-cabecera");
    const ico = nodo("span", null, "tarjeta-icono");
    ico.append(icono(item.icono, 17));
    top.append(nodo("h3", item.titulo), ico);

    const accion = enlace(item.accionTexto, item.modulo);
    accion.append(icono("flechaDer", 14));
    tarjeta.append(top, nodo("p", item.descripcion), accion);
    grid.append(tarjeta);
  }
  return grid;
}
