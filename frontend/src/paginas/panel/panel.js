/* Arranque del panel: sesión, menú por rol y navegación entre vistas — MansoViaje */
import { MVApi } from "../../compartido/js/api.js";
import { MVIconos } from "../../compartido/js/iconos.js";
import { estadoPanel, nombresRol } from "./estado.js";
import { FUNCIONALIDADES_POR_ROL } from "./roles.js";
import {
  $,
  api,
  boton,
  contenido,
  enlace,
  estadoVacio,
  icono,
  mostrarAviso,
  mostrarError,
  mostrarSkeleton,
  tarjetas,
} from "./ui.js";
import { vistaAdmin } from "./vistas/administracion/index.js";
import { vistaDador } from "./vistas/dador/index.js";
import { vistaTransportista } from "./vistas/transportista/index.js";

function inicializarIconosShell() {
  const logoSidebar = $("logo-sidebar");
  const logoMovil = $("logo-movil");
  const icoMenu = $("icono-menu");
  const icoSalir = $("icono-salir");

  if (logoSidebar) logoSidebar.replaceChildren(icono("isotipo", 20));
  if (logoMovil) logoMovil.replaceChildren(icono("isotipo", 17));
  if (icoMenu) icoMenu.replaceChildren(icono("menu", 16));
  if (icoSalir) icoSalir.replaceChildren(icono("salir", 16));
}

function armarMenu() {
  const nav = $("navegacion");
  nav.replaceChildren();
  const inicio = { modulo: "inicio", titulo: "Inicio", icono: "inicio" };
  for (const item of [inicio, ...FUNCIONALIDADES_POR_ROL[estadoPanel.usuario.rol]]) {
    const a = enlace(item.titulo, item.modulo);
    a.className = "";
    a.prepend(icono(item.icono, 17));
    nav.append(a);
  }
  $("nombre").textContent = estadoPanel.usuario.nombre;
  $("etiqueta").textContent = $("rol").textContent = nombresRol[estadoPanel.usuario.rol];
  const avatar = $("avatar-usuario");
  if (avatar && MVIconos) {
    avatar.textContent = MVIconos.iniciales(estadoPanel.usuario.nombre);
  }
}

async function navegar() {
  if (!estadoPanel.usuario) return;
  const actual = ++estadoPanel.versionVista;
  const [ruta = "inicio", query = ""] = (location.hash.slice(1) || "inicio").split("?");
  const opciones = FUNCIONALIDADES_POR_ROL[estadoPanel.usuario.rol];
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
    (estadoPanel.usuario.rol === "ADMIN_BACKOFFICE"
      ? "Panel de administración"
      : "Bienvenido a MansoViaje");
  document.title = $("titulo").textContent + " | MansoViaje";
  $("saludo").textContent = "Hola, " + estadoPanel.usuario.nombre;
  mostrarAviso("");
  $("titulo").focus();
  mostrarSkeleton();
  try {
    const params = new URLSearchParams(query);
    let vista;
    if (estadoPanel.usuario.rol === "ADMIN_BACKOFFICE") vista = await vistaAdmin(ruta, params);
    else if (estadoPanel.usuario.rol === "DADOR_CARGA") vista = await vistaDador(ruta, params);
    else if (estadoPanel.usuario.rol === "TRANSPORTISTA")
      vista = await vistaTransportista(ruta, params);
    else vista = tarjetas(opciones);
    // Una respuesta anterior no debe sobrescribir la pestaña recién seleccionada.
    if (actual === estadoPanel.versionVista) contenido.replaceChildren(vista);
  } catch (error) {
    if (actual === estadoPanel.versionVista) mostrarError(error, navegar);
  }
}

async function iniciarPanel() {
  inicializarIconosShell();
  try {
    estadoPanel.usuario = await api("/auth/sesion");
    if (!Object.hasOwn(FUNCIONALIDADES_POR_ROL, estadoPanel.usuario.rol))
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
    await MVApi.cerrarSesion();
  } catch (error) {
    mostrarAviso("No se pudo cerrar la sesión. Vuelve a intentarlo.", "error");
  }
};

window.addEventListener("hashchange", navegar);
window.addEventListener("focus", () => {
  if (estadoPanel.usuario) api("/auth/sesion").catch(() => {});
});
estadoPanel.navegar = navegar;
document.addEventListener("DOMContentLoaded", iniciarPanel);
