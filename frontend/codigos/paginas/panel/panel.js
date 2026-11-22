/* Estructura y sesión compartidas por los tres roles. Los módulos solo dibujan el contenido. */
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
function boton(texto, accion) {
  const b = nodo("button", texto);
  b.type = "button";
  b.addEventListener("click", accion);
  return b;
}
function volverLogin() {
  for (const clave of ["usuario_actual", "usuario_rol", "access_token"])
    localStorage.removeItem(clave);
  location.replace("../Login/index.html");
}
async function api(ruta, datos) {
  const token = localStorage.getItem("access_token");
  if (!token) {
    volverLogin();
    throw Error("Inicia sesión.");
  }
  const opciones = { headers: { Authorization: "Bearer " + token }, cache: "no-store" };
  if (datos !== undefined) {
    opciones.method = "POST";
    opciones.headers["Content-Type"] = "application/json";
    opciones.body = JSON.stringify(datos);
  }
  const r = await fetch(API + ruta, opciones);
  if (r.status === 401) {
    volverLogin();
    throw Error("La sesión terminó.");
  }
  if (!r.ok) {
    const detalle = (await r.json().catch(() => ({}))).detail;
    throw Error(typeof detalle === "string" ? detalle : "No se pudo completar la solicitud.");
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
  $("aviso").textContent = "";
  $("titulo").focus();
  contenido.replaceChildren(nodo("p", "Cargando…"));
  try {
    let vista;
    if (usuario.rol === "ADMIN_BACKOFFICE")
      vista = await vistaAdmin(ruta, new URLSearchParams(query));
    else vista = item ? moduloOperativo(item) : tarjetas(opciones);
    // Una respuesta anterior no debe sobrescribir la pestaña recién seleccionada.
    if (actual === versionVista) contenido.replaceChildren(vista);
  } catch (error) {
    if (actual === versionVista) mostrarError(error, navegar);
  }
}
function moduloOperativo(item) {
  if (item.destino) {
    const acceso = nodo("a", item.accionTexto, "boton");
    acceso.href = item.destino;
    return acceso;
  }
  const bloque = nodo("article", null, "tarjeta");
  bloque.append(
    nodo("p", item.descripcion),
    boton(item.accionTexto, () => alert("Accediendo a: " + item.titulo + " (" + item.modulo + ")"))
  );
  return bloque;
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
    $("aviso").textContent = "No se pudo cerrar la sesión. Vuelve a intentarlo.";
  }
};
window.addEventListener("hashchange", navegar);
window.addEventListener("focus", () => {
  if (usuario) api("/auth/sesion").catch(() => {});
});
document.addEventListener("DOMContentLoaded", iniciarPanel);
