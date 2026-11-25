/* Estructura, sesión y utilidades compartidas por los tres roles — MansoViaje */
const API =
  window.API_BASE_URL ||
  (window.location.protocol.startsWith("http")
    ? window.location.origin
    : "http://127.0.0.1:8000");
const $ = (id) => document.getElementById(id);
const contenido = $("contenido");
const nombresRol = {
  ADMIN_BACKOFFICE: "Administrador",
  TRANSPORTISTA: "Transportista",
  DADOR_CARGA: "Dador de carga",
};
let usuario;
let versionVista = 0;

function icono(nombre, size = 17) {
  return window.MVIconos ? window.MVIconos.crear(nombre, { size }) : nodo("span", "");
}

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

function badgeEstado(estado, textoPersonalizado) {
  if (window.MVIconos) return window.MVIconos.badgeEstado(estado, textoPersonalizado);
  return nodo("span", textoPersonalizado ?? String(estado || "—"), "badge badge-neutro");
}

function celdaId(id) {
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

function estadoVacio(mensaje, accionEl = null) {
  const caja = nodo("div", null, "estado-vacio");
  const ico = nodo("div", null, "estado-vacio-icono");
  ico.append(icono("bandejaVacia", 22));
  caja.append(ico, nodo("p", mensaje));
  if (accionEl) caja.append(accionEl);
  return caja;
}

function tabla(columnas, filas, vacio, accionVacio = null) {
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

function tarjetaKpi({
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

function mostrarSkeleton() {
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

function confirmarAccion({
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
    estadoVacio(
      error.message || "No se pudo cargar la información.",
      boton("Reintentar", reintentar, "btn-primario")
    )
  );
}

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
  for (const item of [inicio, ...FUNCIONALIDADES_POR_ROL[usuario.rol]]) {
    const a = enlace(item.titulo, item.modulo);
    a.className = "";
    a.prepend(icono(item.icono, 17));
    nav.append(a);
  }
  $("nombre").textContent = usuario.nombre;
  $("etiqueta").textContent = $("rol").textContent = nombresRol[usuario.rol];
  const avatar = $("avatar-usuario");
  if (avatar && window.MVIconos) {
    avatar.textContent = window.MVIconos.iniciales(usuario.nombre);
  }
}

function tarjetas(items) {
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
    (usuario.rol === "ADMIN_BACKOFFICE" ? "Panel de administración" : "Bienvenido a MansoViaje");
  document.title = $("titulo").textContent + " | MansoViaje";
  $("saludo").textContent = "Hola, " + usuario.nombre;
  mostrarAviso("");
  $("titulo").focus();
  mostrarSkeleton();
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
  inicializarIconosShell();
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
