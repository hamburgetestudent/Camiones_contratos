/* Catálogo principal conectado a la API real de FastAPI — MansoViaje */
const API_BASE_URL =
  window.API_BASE_URL ||
  (window.location.protocol.startsWith("http")
    ? window.location.origin
    : "http://127.0.0.1:8000");

let usuarioActual = null;
let contratosCargados = [];
let modoMisContratos = false;

const listaContratos = document.getElementById("lista-contratos");
const filtroRegion = document.getElementById("filtro-region");
const precioMinimo = document.getElementById("precio-minimo");
const precioMaximo = document.getElementById("precio-maximo");
const filtroTipo = document.getElementById("filtro-empresa");
const botonLimpiarFiltros = document.getElementById("limpiar-filtros");
const contadorContratos = document.getElementById("contador-contratos");
const mensajeSinResultados = document.getElementById("mensaje-sin-resultados");
const textoSinResultados = document.getElementById("texto-sin-resultados");
const avisoPrincipal = document.getElementById("aviso-principal");
const botonPerfil = document.getElementById("boton-perfil");
const menuPerfil = document.getElementById("menu-perfil");
const inicialesPerfil = document.getElementById("iniciales-perfil");
const botonCrear = document.getElementById("boton-crear-contrato");
const botonMisContratos = document.getElementById("boton-mis-contratos");
const tituloListado = document.getElementById("titulo-listado");
const subtituloListado = document.getElementById("subtitulo-listado");
const modalDetalle = document.getElementById("modal-detalle");

function inicializarIconosPrincipal() {
  if (!window.MVIconos) return;
  const logo = document.getElementById("logo-principal");
  if (logo) logo.replaceChildren(window.MVIconos.crear("isotipo", { size: 20 }));

  const tituloFiltros = document.getElementById("titulo-filtros-principal");
  if (tituloFiltros) {
    tituloFiltros.prepend(window.MVIconos.crear("filtro", { size: 14 }));
  }

  const icoVacio = document.getElementById("icono-sin-resultados");
  if (icoVacio) icoVacio.replaceChildren(window.MVIconos.crear("bandejaVacia", { size: 22 }));
}

function mostrarAvisoPrincipal(texto, tipo = "error") {
  if (!avisoPrincipal) return;
  avisoPrincipal.replaceChildren();
  if (!texto) {
    avisoPrincipal.className = "oculto";
    return;
  }
  avisoPrincipal.className = "aviso-banner aviso-" + tipo;
  const cuerpo = document.createElement("div");
  cuerpo.className = "aviso-banner-contenido";
  if (window.MVIconos) {
    cuerpo.append(window.MVIconos.crear(tipo === "exito" ? "exito" : "error", { size: 17 }));
  }
  const span = document.createElement("span");
  span.textContent = texto;
  cuerpo.append(span);

  const cerrar = document.createElement("button");
  cerrar.type = "button";
  cerrar.className = "aviso-cerrar";
  cerrar.setAttribute("aria-label", "Cerrar aviso");
  if (window.MVIconos) cerrar.append(window.MVIconos.crear("cerrar", { size: 15 }));
  cerrar.addEventListener("click", () => mostrarAvisoPrincipal(""));

  avisoPrincipal.append(cuerpo, cerrar);
}

function mostrarSkeletonCatalogo() {
  listaContratos.replaceChildren();
  mensajeSinResultados.classList.add("oculto");
  for (let i = 0; i < 6; i++) {
    const card = document.createElement("div");
    card.className = "skeleton-card";
    card.innerHTML = `
      <div class="skeleton skeleton-linea skeleton-linea--corta"></div>
      <div class="skeleton skeleton-linea skeleton-linea--grande"></div>
      <div class="skeleton skeleton-linea skeleton-linea--llena"></div>
      <div class="skeleton skeleton-linea"></div>
    `;
    listaContratos.appendChild(card);
  }
}

function volverLogin() {
  for (const clave of ["usuario_actual", "access_token", "usuario_rol", "sesion_usuario"]) {
    localStorage.removeItem(clave);
  }
  window.location.replace("../login/login.html");
}

async function solicitarApi(ruta, opciones = {}) {
  const token = localStorage.getItem("access_token");
  if (!token) {
    volverLogin();
    throw new Error("Debes iniciar sesión.");
  }
  const r = await fetch(API_BASE_URL + ruta, {
    ...opciones,
    headers: {
      Authorization: "Bearer " + token,
      ...(opciones.headers || {}),
    },
    cache: "no-store",
  });
  if (r.status === 401) {
    volverLogin();
    throw new Error("Sesión expirada.");
  }
  if (!r.ok) {
    const cuerpo = await r.json().catch(() => ({}));
    throw new Error(typeof cuerpo.detail === "string" ? cuerpo.detail : "Error al cargar datos.");
  }
  return r.status === 204 ? null : r.json();
}

function formatearPrecio(precio, moneda = "CLP") {
  const valor = Number(precio);
  if (!Number.isFinite(valor)) return "—";
  if (moneda === "CLP") {
    return new Intl.NumberFormat("es-CL", {
      style: "currency",
      currency: "CLP",
      maximumFractionDigits: 0,
    }).format(valor);
  }
  return `${valor.toLocaleString("es-CL")} ${moneda}`;
}

function formatearFecha(iso) {
  if (!iso) return "—";
  return new Intl.DateTimeFormat("es-CL", {
    dateStyle: "short",
    timeStyle: "short",
  }).format(new Date(iso));
}

function obtenerIniciales(nombre) {
  return window.MVIconos ? window.MVIconos.iniciales(nombre) : "MV";
}

function escaparTexto(valor) {
  return String(valor ?? "").replace(
    /[&<>"']/g,
    (caracter) =>
      ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#039;",
      })[caracter]
  );
}

function crearTarjetaContrato(contrato) {
  const tarjeta = document.createElement("button");
  tarjeta.type = "button";
  tarjeta.className = "tarjeta-contrato";
  tarjeta.setAttribute(
    "aria-label",
    `Ver detalles del contrato ${contrato.origen} a ${contrato.destino}`
  );

  const claseEstado = window.MVIconos
    ? window.MVIconos.claseBadgeEstado(contrato.estado)
    : "badge-info";

  tarjeta.innerHTML = `
    <div class="tarjeta-superior">
      <span class="badge ${claseEstado}">${escaparTexto(contrato.estado)}</span>
      <span class="precio-contrato num-tabular">${escaparTexto(formatearPrecio(contrato.monto_total, contrato.moneda))}</span>
    </div>
    <h3 class="titulo-contrato">${escaparTexto(contrato.origen)} → ${escaparTexto(contrato.destino)}</h3>
    <div class="ruta-contrato">
      <div class="punto-ruta">
        <span class="icono-punto"></span>
        <span><strong>Tipo de carga:</strong> ${escaparTexto(contrato.tipo_carga)}</span>
      </div>
      <div class="punto-ruta destino">
        <span class="icono-punto"></span>
        <span class="num-tabular"><strong>Peso / Capacidad:</strong> ${escaparTexto(contrato.peso_total)} KG / ${escaparTexto(contrato.input_camionKG)} KG</span>
      </div>
    </div>
    <div class="pie-tarjeta">
      <span class="num-tabular">Salida: ${escaparTexto(formatearFecha(contrato.f_estimada_salida))}</span>
      <span class="ver-detalle">Ver detalles →</span>
    </div>
  `;

  tarjeta.addEventListener("click", () => abrirDetalleContrato(contrato));
  return tarjeta;
}

function mostrarContratos(lista) {
  listaContratos.replaceChildren();
  lista.forEach((contrato) => listaContratos.appendChild(crearTarjetaContrato(contrato)));
  contadorContratos.textContent = `${lista.length} ${lista.length === 1 ? "contrato" : "contratos"}`;
  textoSinResultados.textContent = "No se encontraron contratos con esos filtros.";
  mensajeSinResultados.classList.toggle("oculto", lista.length !== 0);
}

function cargarOpcionesTipo() {
  const actual = filtroTipo.value;
  filtroTipo.replaceChildren();
  const optTodos = document.createElement("option");
  optTodos.value = "";
  optTodos.textContent = "Todos los tipos";
  filtroTipo.appendChild(optTodos);

  const tipos = [...new Set(contratosCargados.map((c) => c.tipo_carga))].sort();
  tipos.forEach((tipo) => {
    const opcion = document.createElement("option");
    opcion.value = tipo;
    opcion.textContent = tipo;
    filtroTipo.appendChild(opcion);
  });
  filtroTipo.value = actual;
}

function filtrarContratos() {
  const region = filtroRegion.value.trim().toLowerCase();
  const minimo = precioMinimo.value === "" ? 0 : Number(precioMinimo.value);
  const maximo = precioMaximo.value === "" ? Infinity : Number(precioMaximo.value);
  const tipoSeleccionado = filtroTipo.value;

  const filtrados = contratosCargados.filter((c) => {
    const cumpleRegion =
      !region ||
      c.origen.toLowerCase().includes(region) ||
      c.destino.toLowerCase().includes(region);
    const cumplePrecio = Number(c.monto_total) >= minimo && Number(c.monto_total) <= maximo;
    const cumpleTipo = !tipoSeleccionado || c.tipo_carga === tipoSeleccionado;
    return cumpleRegion && cumplePrecio && cumpleTipo;
  });

  mostrarContratos(filtrados);
}

function limpiarFiltros() {
  filtroRegion.value = "";
  precioMinimo.value = "";
  precioMaximo.value = "";
  filtroTipo.value = "";
  filtrarContratos();
}

function abrirDetalleContrato(contrato) {
  document.getElementById("modal-titulo").textContent = `${contrato.origen} → ${contrato.destino}`;
  const badgeWrap = document.getElementById("modal-badge-wrap");
  if (badgeWrap) {
    badgeWrap.replaceChildren(
      window.MVIconos
        ? window.MVIconos.badgeEstado(contrato.estado)
        : document.createTextNode(contrato.estado)
    );
  }

  const requisitos = [];
  if (contrato.requiere_termo) requisitos.push("Equipo termo/refrigeración");
  if (contrato.req_blindaje) requisitos.push("Camión blindado");
  if (contrato.numero_onu) requisitos.push("ONU " + contrato.numero_onu);
  if (contrato.req_embalaje) requisitos.push("Embalaje: " + contrato.req_embalaje);

  const dl = document.getElementById("modal-datos");
  dl.replaceChildren();
  const campos = [
    ["Identificador", contrato.id],
    ["Tipo de carga", contrato.tipo_carga],
    ["Peso / Capacidad", `${contrato.peso_total} KG / ${contrato.input_camionKG} KG`],
    ["Cierre postulaciones", formatearFecha(contrato.f_cierre_postulaciones)],
    ["Salida estimada", formatearFecha(contrato.f_estimada_salida)],
    ["Llegada estimada", formatearFecha(contrato.f_estimada_llegada)],
    ["Requisitos especiales", requisitos.length ? requisitos.join(" · ") : "Ninguno"],
    ["Monto total", formatearPrecio(contrato.monto_total, contrato.moneda)],
  ];
  for (const [k, v] of campos) {
    const dt = document.createElement("dt");
    dt.textContent = k;
    const dd = document.createElement("dd");
    dd.textContent = v;
    dl.append(dt, dd);
  }
  const link = document.getElementById("modal-ir-panel");
  if (usuarioActual?.rol === "TRANSPORTISTA") {
    link.href = `../panel/panel.html#subastas?carga=${encodeURIComponent(contrato.id)}`;
    link.textContent = "Postular en el panel";
  } else {
    link.href = `../panel/panel.html#contratos?detalle=${encodeURIComponent(contrato.id)}`;
    link.textContent = "Gestionar en el panel";
  }
  modalDetalle.showModal();
}

async function cargarContratosDesdeApi() {
  mostrarAvisoPrincipal("");
  mostrarSkeletonCatalogo();
  try {
    if (modoMisContratos) {
      const todos = await solicitarApi("/contratos");
      if (usuarioActual.rol === "DADOR_CARGA") {
        contratosCargados = todos.filter((c) => c.id_empresa_generadora === usuarioActual.id);
      } else if (usuarioActual.rol === "TRANSPORTISTA") {
        contratosCargados = todos.filter((c) => c.id_transportista === usuarioActual.id);
      } else {
        contratosCargados = todos;
      }
      tituloListado.textContent = "Mis contratos";
      subtituloListado.textContent = "Contratos asociados directamente a tu cuenta.";
      botonMisContratos.textContent = "Ver cargas disponibles";
    } else {
      contratosCargados = await solicitarApi("/subastas/cargas");
      tituloListado.textContent = "Cargas disponibles en subasta";
      subtituloListado.textContent = "Explora los contratos activos publicados en la plataforma.";
      botonMisContratos.textContent = "Mis contratos";
    }
    cargarOpcionesTipo();
    filtrarContratos();
  } catch (error) {
    listaContratos.replaceChildren();
    textoSinResultados.textContent = error.message || "No se pudieron cargar los contratos.";
    mensajeSinResultados.classList.remove("oculto");
  }
}

function alternarMenuPerfil() {
  const estaOculto = menuPerfil.classList.toggle("oculto");
  botonPerfil.setAttribute("aria-expanded", String(!estaOculto));
}

async function gestionarAccionPerfil(evento) {
  const boton = evento.target.closest("[data-accion-perfil]");
  if (!boton) return;

  const accion = boton.dataset.accionPerfil;
  menuPerfil.classList.add("oculto");
  botonPerfil.setAttribute("aria-expanded", "false");

  if (accion === "editar") {
    const destino =
      usuarioActual?.rol === "TRANSPORTISTA"
        ? "../panel/panel.html#onboarding"
        : usuarioActual?.rol === "DADOR_CARGA"
          ? "../panel/panel.html#tributario"
          : "../panel/panel.html#cuentas";
    window.location.href = destino;
  } else if (accion === "configuracion") {
    window.location.href =
      usuarioActual?.rol === "ADMIN_BACKOFFICE"
        ? "../panel/panel.html#configuracion"
        : "../panel/panel.html";
  } else if (accion === "cerrar") {
    try {
      const respuesta = await fetch(API_BASE_URL + "/auth/logout", {
        method: "POST",
        headers: { Authorization: "Bearer " + localStorage.getItem("access_token") },
      });
      if (!respuesta.ok && respuesta.status !== 401) throw Error();
    } catch {
      mostrarAvisoPrincipal("No se pudo cerrar la sesión. Vuelve a intentarlo.", "error");
      return;
    }
    volverLogin();
  }
}

async function inicializarPantallaPrincipal() {
  inicializarIconosPrincipal();
  try {
    usuarioActual = await solicitarApi("/auth/sesion");
    inicialesPerfil.textContent = obtenerIniciales(usuarioActual.nombre);
    if (usuarioActual.rol === "TRANSPORTISTA") {
      botonCrear.classList.add("oculto");
    }
    await cargarContratosDesdeApi();
  } catch {
    return;
  }

  filtroRegion.addEventListener("input", filtrarContratos);
  precioMinimo.addEventListener("input", filtrarContratos);
  precioMaximo.addEventListener("input", filtrarContratos);
  filtroTipo.addEventListener("change", filtrarContratos);
  botonLimpiarFiltros.addEventListener("click", limpiarFiltros);
  const btnResetVacio = document.getElementById("btn-reset-vacio");
  if (btnResetVacio) btnResetVacio.addEventListener("click", limpiarFiltros);

  botonPerfil.addEventListener("click", (evento) => {
    evento.stopPropagation();
    alternarMenuPerfil();
  });

  menuPerfil.addEventListener("click", gestionarAccionPerfil);

  botonCrear.addEventListener("click", () => {
    window.location.href = "../crear-contrato/crear-contrato.html?desde=catalogo";
  });

  botonMisContratos.addEventListener("click", () => {
    modoMisContratos = !modoMisContratos;
    cargarContratosDesdeApi();
  });

  document.getElementById("cerrar-modal").addEventListener("click", () => modalDetalle.close());

  document.addEventListener("click", (evento) => {
    if (!menuPerfil.contains(evento.target) && !botonPerfil.contains(evento.target)) {
      menuPerfil.classList.add("oculto");
      botonPerfil.setAttribute("aria-expanded", "false");
    }
  });
}

document.addEventListener("DOMContentLoaded", inicializarPantallaPrincipal);
