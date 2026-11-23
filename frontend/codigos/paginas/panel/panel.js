/* Estructura, sesión y utilidades compartidas por los tres roles. */
const API = window.API_BASE_URL || "http://127.0.0.1:8000";
const $ = (id) => document.getElementById(id);
const contenido = $("contenido");
const nombresRol = {
  ADMIN_BACKOFFICE: "Administrador",
  TRANSPORTISTA: "Transportista",
  DADOR_CARGA: "Dador de carga",
};
let usuario;
let versionVista = 0;

function nodo(tag, texto, clase) {
  const el = document.createElement(tag);
  if (texto != null) el.textContent = texto;
  if (clase) el.className = clase;
  return el;
}
function enlace(texto, modulo, filtros = {}) {
  const a = nodo("a", texto, "boton");
  const query = new URLSearchParams(filtros).toString();
  a.href = "#" + modulo + (query ? "?" + query : "");
  return a;
}
function boton(texto, accion, clase = "") {
  const b = nodo("button", texto, clase);
  b.type = "button";
  b.addEventListener("click", accion);
  return b;
}
function mostrarAviso(texto, tipo = "info") {
  const el = $("aviso");
  el.textContent = texto || "";
  el.className = texto ? "aviso-" + tipo : "";
}
function badgeEstado(estado) {
  const valor = String(estado || "—").toUpperCase();
  let clase = "badge-neutro";
  if (["APROBADO", "SELECCIONADA", "FINALIZADO", "ENTREGADO", "COMPLETADO"].includes(valor)) {
    clase = "badge-aprobado";
  } else if (
    ["PENDIENTE", "EN_REVISION", "EN_SUBASTA", "EN_POSTULACION", "EN_DISPUTA"].includes(valor)
  ) {
    clase = "badge-pendiente";
  } else if (["RECHAZADO", "RECHAZADA", "CANCELADO"].includes(valor)) {
    clase = "badge-rechazado";
  } else if (["PUBLICADO", "ADJUDICADO", "EN_TRANSITO", "POSTULADA"].includes(valor)) {
    clase = "badge-info";
  }
  return nodo("span", valor, "badge " + clase);
}
function formatearMoneda(valor, moneda = "CLP") {
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
function fechaLocal(valor) {
  if (!valor) return "—";
  return new Intl.DateTimeFormat("es-CL", {
    dateStyle: "short",
    timeStyle: "short",
  }).format(new Date(valor));
}
function tabla(columnas, filas, vacio) {
  if (!filas.length) return nodo("p", vacio, "texto-suave");
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
function ficha(campos) {
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
function volverLogin() {
  for (const clave of ["usuario_actual", "usuario_rol", "access_token"])
    localStorage.removeItem(clave);
  location.replace("../Login/index.html");
}
function extraerDetalleError(cuerpo) {
  if (!cuerpo || typeof cuerpo !== "object") return "No se pudo completar la solicitud.";
  if (typeof cuerpo.detail === "string") return cuerpo.detail;
  if (Array.isArray(cuerpo.detail) && cuerpo.detail.length > 0) {
    return cuerpo.detail.map((item) => item.msg || JSON.stringify(item)).join(" | ");
  }
  return "No se pudo completar la solicitud.";
}
async function api(ruta, datos, opcionesExtra = {}) {
  const token = localStorage.getItem("access_token");
  if (!token) {
    volverLogin();
    throw Error("Inicia sesión.");
  }
  const method = opcionesExtra.method || (datos !== undefined ? "POST" : "GET");
  const headers = {
    Authorization: "Bearer " + token,
    ...(opcionesExtra.headers || {}),
  };
  const opciones = { method, headers, cache: "no-store" };
  if (datos !== undefined) {
    opciones.headers["Content-Type"] = "application/json";
    opciones.body = JSON.stringify(datos);
  }
  const r = await fetch(API + ruta, opciones);
  if (r.status === 401) {
    volverLogin();
    throw Error("La sesión terminó.");
  }
  if (!r.ok) {
    const cuerpo = await r.json().catch(() => ({}));
    throw Error(extraerDetalleError(cuerpo));
  }
  return r.status === 204 ? null : r.json();
}
function mostrarError(error, reintentar) {
  contenido.replaceChildren(
    nodo("p", error.message || "No se pudo cargar la información."),
    boton("Reintentar", reintentar)
  );
}
function armarMenu() {
  const nav = $("navegacion");
  nav.replaceChildren();
  const inicio = { modulo: "inicio", titulo: "Inicio", icono: "⌂" };
  for (const item of [inicio, ...FUNCIONALIDADES_POR_ROL[usuario.rol]]) {
    const a = enlace(item.titulo, item.modulo);
    a.className = "";
    const icono = nodo("span", item.icono);
    icono.setAttribute("aria-hidden", "true");
    a.prepend(icono);
    nav.append(a);
  }
  $("nombre").textContent = usuario.nombre;
  $("etiqueta").textContent = $("rol").textContent = nombresRol[usuario.rol];
}
function tarjetas(items) {
  const grid = nodo("div", null, "rejilla");
  for (const item of items) {
    const tarjeta = nodo("article", null, "tarjeta");
    tarjeta.append(
      nodo("h3", item.titulo),
      nodo("p", item.descripcion),
      enlace(item.accionTexto, item.modulo)
    );
    grid.append(tarjeta);
  }
  return grid;
}
async function navegar() {
  if (!usuario) return;
  const actual = ++versionVista;
  const [ruta = "inicio", query = ""] = (location.hash.slice(1) || "inicio").split("?");
  const opciones = FUNCIONALIDADES_POR_ROL[usuario.rol];
  const item = opciones.find((opcion) => opcion.modulo === ruta);
  if (ruta !== "inicio" && !item) {
    location.replace("#inicio");
    return;
  }
  for (const a of $("navegacion").children) {
    if (a.hash === "#" + ruta) a.setAttribute("aria-current", "page");
    else a.removeAttribute("aria-current");
  }
  $("menu").setAttribute("aria-expanded", "false");
  $("lateral").classList.remove("abierto");
  $("titulo").textContent =
    item?.titulo ||
    (usuario.rol === "ADMIN_BACKOFFICE" ? "Panel de administración" : "Bienvenido a la Plataforma");
  document.title = $("titulo").textContent + " | Camiones Contratos";
  $("saludo").textContent = "Hola, " + usuario.nombre;
  mostrarAviso("");
  $("titulo").focus();
  contenido.replaceChildren(nodo("p", "Cargando…"));
  try {
    const params = new URLSearchParams(query);
    let vista;
    if (usuario.rol === "ADMIN_BACKOFFICE") vista = await vistaAdmin(ruta, params);
    else if (usuario.rol === "DADOR_CARGA") vista = await vistaDador(ruta, params);
    else if (usuario.rol === "TRANSPORTISTA") vista = await vistaTransportista(ruta, params);
    else vista = tarjetas(opciones);
    // Una respuesta anterior no debe sobrescribir la pestaña recién seleccionada.
    if (actual === versionVista) contenido.replaceChildren(vista);
  } catch (error) {
    if (actual === versionVista) mostrarError(error, navegar);
  }
}
async function iniciarPanel() {
  try {
    usuario = await api("/auth/sesion");
    if (!Object.hasOwn(FUNCIONALIDADES_POR_ROL, usuario.rol))
      throw Error("Rol sin opciones disponibles.");
    armarMenu();
    await navegar();
  } catch (error) {
    mostrarError(error, iniciarPanel);
  }
}
$("menu").onclick = () => {
  const abierto = $("lateral").classList.toggle("abierto");
  $("menu").setAttribute("aria-expanded", String(abierto));
};
$("salir").onclick = async () => {
  try {
    await api("/auth/logout", {});
    volverLogin();
  } catch (error) {
    mostrarAviso("No se pudo cerrar la sesión. Vuelve a intentarlo.", "error");
  }
};
window.addEventListener("hashchange", navegar);
window.addEventListener("focus", () => {
  if (usuario) api("/auth/sesion").catch(() => {});
});
document.addEventListener("DOMContentLoaded", iniciarPanel);
