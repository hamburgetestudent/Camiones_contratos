// =================================
// CONFIGURACIÓN DE API Y SESIÓN
// =================================

const API_BASE_URL = window.API_BASE_URL || "http://127.0.0.1:8000";

const ESTADOS_ACTIVOS = ["ACEPTADO", "EN_PROCESO", "ATRASADO"];
const ESTADOS_HISTORIAL = ["FINALIZADO", "CANCELADO"];

// Datos demostrativos solo para desarrollo visual.
// Sustituir por respuestas reales del backend cuando esté disponible.
let contratosGeneralesDemo = [
    {
        id: 301,
        titulo: "Transporte de materiales de construcción",
        estado: "DISPONIBLE",
        esPropio: true,
        dadorNombre: "Tú (Dador actual)",
        origen: "Puerto de Valparaíso, Valparaíso",
        destino: "Obra, Viña del Mar",
        precio: 185000,
        fechaPublicacion: "Hoy",
        transportistaAsignado: null,
        descripcion: "Traslado de materiales de construcción a obra."
    },
    {
        id: 302,
        titulo: "Traslado de carga industrial",
        estado: "ACEPTADO",
        esPropio: true,
        dadorNombre: "Tú (Dador actual)",
        origen: "Quilpué, Valparaíso",
        destino: "Centro logístico, Santiago",
        precio: 320000,
        fechaPublicacion: "Hace 1 día",
        transportistaAsignado: "Transportes Andes SpA",
        fechaAceptacion: "2026-11-21 17:10",
        descripcion: "Carga industrial paletizada lista para retiro."
    },
    {
        id: 303,
        titulo: "Distribución de insumos de bodega",
        estado: "EN_PROCESO",
        esPropio: false,
        dadorNombre: "Suministros Costa",
        origen: "Concón, Valparaíso",
        destino: "Bodega, San Antonio",
        precio: 210000,
        fechaPublicacion: "Hace 2 días",
        transportistaAsignado: "Camiones Costa Sur",
        fechaAceptacion: "2026-11-20 09:40",
        descripcion: "Distribución de insumos en ruta."
    },
    {
        id: 304,
        titulo: "Flete de muebles y equipamiento",
        estado: "FINALIZADO",
        esPropio: true,
        dadorNombre: "Tú (Dador actual)",
        origen: "Villa Alemana, Valparaíso",
        destino: "Limache, Valparaíso",
        precio: 95000,
        fechaPublicacion: "Hace 10 días",
        transportistaAsignado: "Fletes Valpo Ltda.",
        fechaAceptacion: "2026-11-11 11:00",
        descripcion: "Entrega confirmada en destino."
    },
    {
        id: 305,
        titulo: "Traslado de maquinaria agrícola",
        estado: "DISPONIBLE",
        esPropio: false,
        dadorNombre: "Agroservicios El Valle",
        origen: "San Felipe, Valparaíso",
        destino: "Predio agrícola, Ovalle",
        precio: 420000,
        fechaPublicacion: "Hoy",
        transportistaAsignado: null,
        descripcion: "Traslado de maquinaria de otro dador de carga."
    }
];

let contratoPendienteCancelar = null;

const seccionPublicaciones = document.getElementById("seccion-mis-publicaciones");
const seccionMisContratos = document.getElementById("seccion-mis-contratos");
const botonSeccionPublicaciones = document.getElementById("boton-seccion-publicaciones");
const botonSeccionMisContratos = document.getElementById("boton-seccion-mis-contratos");

const listaPublicaciones = document.getElementById("lista-publicaciones");
const listaActivos = document.getElementById("lista-contratos-activos");
const listaHistorial = document.getElementById("lista-contratos-historial");
const contadorPublicaciones = document.getElementById("contador-publicaciones");
const contadorMisContratos = document.getElementById("contador-mis-contratos");
const mensajeSinPublicaciones = document.getElementById("mensaje-sin-publicaciones");
const sinActivos = document.getElementById("sin-contratos-activos");
const sinHistorial = document.getElementById("sin-contratos-historial");
const filtroPropiedadPublicacion = document.getElementById("filtro-propiedad-publicacion");
const filtroEstadoPublicacion = document.getElementById("filtro-estado-publicacion");
const estadoPublicaciones = document.getElementById("estado-publicaciones");
const estadoMisContratos = document.getElementById("estado-mis-contratos");

const botonPerfil = document.getElementById("boton-perfil");
const menuPerfil = document.getElementById("menu-perfil");
const inicialesPerfil = document.getElementById("iniciales-perfil");

const modalDetalle = document.getElementById("modal-detalle");
const modalDetalleTitulo = document.getElementById("modal-detalle-titulo");
const modalDetalleCuerpo = document.getElementById("modal-detalle-cuerpo");
const modalDetalleAcciones = document.getElementById("modal-detalle-acciones");

const modalCancelar = document.getElementById("modal-cancelar");
const formularioCancelar = document.getElementById("formulario-cancelar");
const motivoCancelacion = document.getElementById("motivo-cancelacion");
const contenedorOtroMotivo = document.getElementById("contenedor-otro-motivo");
const textoOtroMotivo = document.getElementById("texto-otro-motivo");

function escaparTexto(valor) {
    return String(valor ?? "").replace(/[&<>"']/g, (caracter) => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#039;"
    })[caracter]);
}

function formatearPrecio(precio) {
    return new Intl.NumberFormat("es-CL", {
        style: "currency",
        currency: "CLP",
        maximumFractionDigits: 0
    }).format(Number(precio) || 0);
}

function obtenerIniciales(nombre) {
    const limpio = String(nombre || "DC").trim();
    if (!limpio) return "DC";
    return limpio
        .split(/\s+/)
        .slice(0, 2)
        .map((palabra) => palabra.charAt(0).toLocaleUpperCase("es-CL"))
        .join("");
}

function mostrarEstado(elemento, texto, tipo = "") {
    if (!texto) {
        elemento.textContent = "";
        elemento.className = "mensaje-estado oculto";
        return;
    }
    elemento.textContent = texto;
    elemento.className = tipo ? `mensaje-estado ${tipo}` : "mensaje-estado";
}

function claseEstado(estado) {
    if (estado === "ACEPTADO") return "etiqueta-estado aceptado";
    if (estado === "ATRASADO") return "etiqueta-estado atrasado";
    if (ESTADOS_HISTORIAL.includes(estado)) return "etiqueta-estado cerrado";
    return "etiqueta-estado";
}

function obtenerUsuarioSesion() {
    // La autorización real del rol DADOR_CARGA y la sesión deben validarse en el backend.
    try {
        const raw = localStorage.getItem("usuario_actual");
        return raw ? JSON.parse(raw) : null;
    } catch {
        return null;
    }
}

function cambiarSeccion(seccion) {
    const esPublicaciones = seccion === "publicaciones";
    seccionPublicaciones.classList.toggle("oculto", !esPublicaciones);
    seccionMisContratos.classList.toggle("oculto", esPublicaciones);
    botonSeccionPublicaciones.classList.toggle("activo", esPublicaciones);
    botonSeccionMisContratos.classList.toggle("activo", !esPublicaciones);

    if (esPublicaciones) {
        obtenerMisPublicaciones();
    } else {
        obtenerMisContratos();
    }
}

function crearTarjetaContrato(contrato) {
    const tarjeta = document.createElement("article");
    const estado = contrato.estado || "DISPONIBLE";
    const esPropio = contrato.esPropio === true;
    const tieneTransportista = Boolean(contrato.transportistaAsignado) || estado !== "DISPONIBLE";
    // Solo se puede modificar un contrato propio mientras esté DISPONIBLE.
    const esEditable = esPropio && estado === "DISPONIBLE";
    // Solo el dador propietario puede cancelar contratos de su propiedad que no estén cerrados.
    const puedeCancelar = esPropio && estado !== "FINALIZADO" && estado !== "CANCELADO";

    tarjeta.className = `tarjeta-contrato${tieneTransportista ? " aceptada-destacada" : ""}`;

    const badgeOrigen = esPropio
        ? `<span class="etiqueta-propio">Publicado por ti</span>`
        : `<span class="etiqueta-estado">Otro dador</span>`;

    const textoTransportista = tieneTransportista
        ? `<strong>Transportista asignado:</strong> ${escaparTexto(contrato.transportistaAsignado || "Asignado")}`
        : `<strong>Sin transportista asignado</strong> (Disponible para aceptar)`;

    tarjeta.innerHTML = `
        <div class="tarjeta-superior">
            <div class="badges-grupo">
                ${badgeOrigen}
                <span class="${claseEstado(estado)}">${escaparTexto(estado)}</span>
            </div>
            <span class="precio-contrato">${formatearPrecio(contrato.precio)}</span>
        </div>
        <h3 class="titulo-contrato">${escaparTexto(contrato.titulo)}</h3>
        <div class="ruta-contrato">
            <div class="punto-ruta">
                <span class="icono-punto"></span>
                <span><strong>Origen:</strong> ${escaparTexto(contrato.origen)}</span>
            </div>
            <div class="punto-ruta destino">
                <span class="icono-punto"></span>
                <span><strong>Destino:</strong> ${escaparTexto(contrato.destino)}</span>
            </div>
        </div>
        <div class="transportista-info">
            <p style="margin:0 0 6px;"><strong>Publicado por:</strong> ${escaparTexto(contrato.dadorNombre || (esPropio ? "Tú" : "Dador de carga"))}</p>
            ${textoTransportista}
        </div>
        <div class="pie-tarjeta">
            <span>Publicado: ${escaparTexto(contrato.fechaPublicacion || "No disponible")}</span>
            <span>ID #${escaparTexto(contrato.id)}</span>
        </div>
        <div class="acciones-tarjeta">
            <button type="button" class="boton-secundario boton-detalle">Ver detalle</button>
            ${esPropio ? `<button type="button" class="boton-secundario boton-editar" ${esEditable ? "" : "disabled"}>Editar</button>` : ""}
            ${puedeCancelar ? `<button type="button" class="boton-peligro boton-cancelar">Cancelar</button>` : ""}
        </div>
    `;

    tarjeta.querySelector(".boton-detalle").addEventListener("click", () => mostrarDetalleContrato(contrato));

    const btnEditar = tarjeta.querySelector(".boton-editar");
    if (btnEditar) {
        btnEditar.addEventListener("click", () => editarContrato(contrato));
    }

    const btnCancelar = tarjeta.querySelector(".boton-cancelar");
    if (btnCancelar) {
        btnCancelar.addEventListener("click", () => abrirModalCancelar(contrato));
    }

    return tarjeta;
}

function mostrarPublicaciones(lista) {
    listaPublicaciones.replaceChildren();
    lista.forEach((contrato) => {
        listaPublicaciones.appendChild(crearTarjetaContrato(contrato));
    });
    contadorPublicaciones.textContent = `${lista.length} ${lista.length === 1 ? "contrato" : "contratos"}`;
    mensajeSinPublicaciones.classList.toggle("oculto", lista.length !== 0);
}

function obtenerMisPublicaciones() {
    mostrarEstado(estadoPublicaciones, "");
    const filtroPropiedad = filtroPropiedadPublicacion.value;
    const estadoFiltro = filtroEstadoPublicacion.value;

    // Se muestran todos los contratos existentes sin restringir únicamente a esPropio,
    // permitiendo filtrar por todos, solo propios o de otros dadores, y por estado.
    const filtradas = contratosGeneralesDemo.filter((contrato) => {
        const cumplePropiedad =
            filtroPropiedad === "todos" ||
            (filtroPropiedad === "propios" && contrato.esPropio === true) ||
            (filtroPropiedad === "otros" && contrato.esPropio !== true);

        const cumpleEstado = !estadoFiltro || contrato.estado === estadoFiltro;

        return cumplePropiedad && cumpleEstado;
    });

    mostrarPublicaciones(filtradas);
}

function obtenerMisContratos() {
    mostrarEstado(estadoMisContratos, "");
    const propiosAceptados = contratosGeneralesDemo.filter(
        (c) => c.esPropio === true && (Boolean(c.transportistaAsignado) || c.estado !== "DISPONIBLE")
    );
    const activos = propiosAceptados.filter((c) => ESTADOS_ACTIVOS.includes(c.estado));
    const historial = propiosAceptados.filter((c) => ESTADOS_HISTORIAL.includes(c.estado));

    listaActivos.replaceChildren();
    activos.forEach((c) => listaActivos.appendChild(crearTarjetaContrato(c)));
    sinActivos.classList.toggle("oculto", activos.length !== 0);

    listaHistorial.replaceChildren();
    historial.forEach((c) => listaHistorial.appendChild(crearTarjetaContrato(c)));
    sinHistorial.classList.toggle("oculto", historial.length !== 0);

    contadorMisContratos.textContent = `${activos.length} activos · ${historial.length} historial`;
}

function mostrarDetalleContrato(contrato) {
    modalDetalleTitulo.textContent = contrato.titulo || "Detalle del contrato";
    modalDetalleCuerpo.innerHTML = `
        <p><strong>Propiedad:</strong> ${contrato.esPropio ? "Publicado por ti" : "Publicado por otro dador"}</p>
        <p><strong>Estado:</strong> ${escaparTexto(contrato.estado)}</p>
        <p><strong>Monto:</strong> ${formatearPrecio(contrato.precio)}</p>
        <p><strong>Origen:</strong> ${escaparTexto(contrato.origen)}</p>
        <p><strong>Destino:</strong> ${escaparTexto(contrato.destino)}</p>
        <p><strong>Transportista asignado:</strong> ${escaparTexto(contrato.transportistaAsignado || "Aún no asignado")}</p>
        <p><strong>Descripción:</strong> ${escaparTexto(contrato.descripcion || "Sin descripción adicional.")}</p>
    `;

    modalDetalleAcciones.replaceChildren();
    const btnCerrar = document.createElement("button");
    btnCerrar.type = "button";
    btnCerrar.className = "boton-secundario";
    btnCerrar.textContent = "Cerrar";
    btnCerrar.addEventListener("click", cerrarModalDetalle);
    modalDetalleAcciones.appendChild(btnCerrar);

    modalDetalle.classList.remove("oculto");
}

function cerrarModalDetalle() {
    modalDetalle.classList.add("oculto");
}

function crearNuevoContrato() {
    ///////////////////////////////////////////////////////////////// agregar path de Crear contrato /////////////////////////////////////////////////////
    alert("Pendiente conexión: agregar path de Crear contrato");
}

function editarContrato(contrato) {
    if (!contrato.esPropio) {
        mostrarEstado(estadoPublicaciones, "No puedes modificar contratos publicados por otros usuarios.", "error");
        return;
    }
    if (contrato.estado !== "DISPONIBLE") {
        mostrarEstado(estadoPublicaciones, "Solo se pueden modificar contratos en estado DISPONIBLE.", "error");
        return;
    }
    // agregar path de Editar contrato
    alert(`Pendiente conexión: agregar path de Editar contrato (ID #${contrato.id})`);
}

function abrirModalCancelar(contrato) {
    if (!contrato.esPropio) {
        mostrarEstado(estadoPublicaciones, "Solo puedes cancelar contratos de tu propiedad.", "error");
        return;
    }
    contratoPendienteCancelar = contrato;
    formularioCancelar.reset();
    contenedorOtroMotivo.classList.add("oculto");
    textoOtroMotivo.required = false;
    modalCancelar.classList.remove("oculto");
}

function cerrarModalCancelar() {
    contratoPendienteCancelar = null;
    modalCancelar.classList.add("oculto");
}

async function cancelarContrato(evento) {
    evento.preventDefault();
    if (!contratoPendienteCancelar) return;

    const motivo = motivoCancelacion.value;
    const explicacion = textoOtroMotivo.value.trim();

    if (!motivo) {
        mostrarEstado(estadoPublicaciones, "Debes seleccionar un motivo de cancelación.", "error");
        return;
    }

    if (motivo === "Otro motivo" && (!explicacion || explicacion.length > 300)) {
        mostrarEstado(estadoPublicaciones, "Debes ingresar una explicación de hasta 300 caracteres para 'Otro motivo'.", "error");
        return;
    }

    // Integración pendiente con backend:
    // Debe validar propiedad del dador y registrar quién canceló, fecha/hora, motivo y explicación adicional.
    const objetivo = contratosGeneralesDemo.find((c) => c.id === contratoPendienteCancelar.id);
    if (objetivo && objetivo.esPropio) {
        objetivo.estado = "CANCELADO";
        objetivo.motivoCancelacion = motivo;
        objetivo.explicacionCancelacion = motivo === "Otro motivo" ? explicacion : "";
    }

    cerrarModalCancelar();
    mostrarEstado(estadoPublicaciones, "Contrato cancelado.", "exito");
    obtenerMisPublicaciones();
    obtenerMisContratos();
}

function alternarMenuPerfil() {
    const estaOculto = menuPerfil.classList.toggle("oculto");
    botonPerfil.setAttribute("aria-expanded", String(!estaOculto));
}

function cerrarSesion() {
    localStorage.removeItem("sesion_usuario");
    localStorage.removeItem("usuario_actual");
    window.location.replace("../../Login/index.html"); 
}

function gestionarAccionPerfil(evento) {
    const boton = evento.target.closest("[data-accion-perfil]");
    if (!boton) return;

    const accion = boton.dataset.accionPerfil;
    menuPerfil.classList.add("oculto");
    botonPerfil.setAttribute("aria-expanded", "false");

    if (accion === "editar") {
        // agregar path de Editar usuario
        alert("Pendiente conexión: agregar path de Editar usuario");
    } else if (accion === "configuracion") {
        // agregar path de Configuración de la aplicación
        alert("Pendiente conexión: agregar path de Configuración de la aplicación");
    } else if (accion === "cerrar") {
        cerrarSesion();
    }
}

function inicializarPagina() {
    const usuario = obtenerUsuarioSesion();
    if (usuario && (usuario.iniciales || usuario.nombre)) {
        inicialesPerfil.textContent = usuario.iniciales || obtenerIniciales(usuario.nombre);
    } else {
        inicialesPerfil.textContent = "DC";
    }

    botonSeccionPublicaciones.addEventListener("click", () => cambiarSeccion("publicaciones"));
    botonSeccionMisContratos.addEventListener("click", () => cambiarSeccion("mis-contratos"));
    filtroPropiedadPublicacion.addEventListener("change", obtenerMisPublicaciones);
    filtroEstadoPublicacion.addEventListener("change", obtenerMisPublicaciones);

    document.getElementById("boton-crear-contrato").addEventListener("click", crearNuevoContrato);
    document.getElementById("boton-crear-contrato-secundario").addEventListener("click", crearNuevoContrato);

    motivoCancelacion.addEventListener("change", () => {
        const esOtro = motivoCancelacion.value === "Otro motivo";
        contenedorOtroMotivo.classList.toggle("oculto", !esOtro);
        textoOtroMotivo.required = esOtro;
    });

    formularioCancelar.addEventListener("submit", cancelarContrato);
    document.getElementById("cerrar-modal-detalle").addEventListener("click", cerrarModalDetalle);
    document.getElementById("cerrar-modal-cancelar").addEventListener("click", cerrarModalCancelar);
    document.getElementById("cancelar-accion-modal").addEventListener("click", cerrarModalCancelar);

    botonPerfil.addEventListener("click", (evento) => {
        evento.stopPropagation();
        alternarMenuPerfil();
    });

    menuPerfil.addEventListener("click", gestionarAccionPerfil);

    document.addEventListener("click", (evento) => {
        if (!menuPerfil.contains(evento.target) && !botonPerfil.contains(evento.target)) {
            menuPerfil.classList.add("oculto");
            botonPerfil.setAttribute("aria-expanded", "false");
        }
    });

    obtenerMisPublicaciones();
}

document.addEventListener("DOMContentLoaded", inicializarPagina);