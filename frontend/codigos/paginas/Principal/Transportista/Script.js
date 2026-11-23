// =================================
// CONFIGURACIÓN DE API Y SESIÓN
// =================================

const API_BASE_URL = window.API_BASE_URL || "http://127.0.0.1:8000";

const ESTADOS_ACTIVOS = ["ACEPTADO", "EN_PROCESO", "ATRASADO"];
const ESTADOS_HISTORIAL = ["FINALIZADO", "CANCELADO"];

// Datos demostrativos solo para desarrollo visual.
// Sustituir por respuestas reales del backend cuando esté disponible.
let contratosDisponiblesDemo = [
    {
        id: 201,
        titulo: "Transporte de materiales de construcción",
        estado: "DISPONIBLE",
        origen: "Puerto de Valparaíso, Valparaíso",
        destino: "Obra, Viña del Mar",
        precio: 185000,
        tipoCamion: "Camión plano",
        capacidadKg: 12000,
        fechaInicio: "2026-11-25",
        fechaEntrega: "2026-11-26",
        tipoCarga: "Construcción",
        clientePublico: "Constructora Horizonte",
        tipoCliente: "Empresa",
        fechaPublicacion: "Hoy",
        descripcion: "Traslado de materiales de construcción. Coordinación de retiro en acceso autorizado."
    },
    {
        id: 202,
        titulo: "Traslado de carga industrial embalada",
        estado: "DISPONIBLE",
        origen: "Quilpué, Valparaíso",
        destino: "Centro logístico, Santiago",
        precio: 320000,
        tipoCamion: "Camión cerrado / furgón",
        capacidadKg: 18000,
        fechaInicio: "2026-11-24",
        fechaEntrega: "2026-11-25",
        tipoCarga: "Carga industrial",
        clientePublico: "Logística del Pacífico",
        tipoCliente: "Empresa",
        fechaPublicacion: "Hace 1 día",
        descripcion: "Transporte de carga industrial paletizada. Confirmar horario de carga con anticipación."
    },
    {
        id: 203,
        titulo: "Entrega de productos agrícolas",
        estado: "DISPONIBLE",
        origen: "La Calera, Valparaíso",
        destino: "Mercado mayorista, Santiago",
        precio: 145000,
        tipoCamion: "Camión refrigerado",
        capacidadKg: 8000,
        fechaInicio: "2026-11-23",
        fechaEntrega: "2026-11-23",
        tipoCarga: "Agrícola",
        clientePublico: "María González",
        tipoCliente: "Persona",
        fechaPublicacion: "Hace 2 días",
        descripcion: "Entrega de productos agrícolas. Recepción en horario de mañana."
    }
];

let misContratosDemo = [
    {
        id: 190,
        titulo: "Distribución de insumos de bodega",
        estado: "EN_PROCESO",
        origen: "Concón, Valparaíso",
        destino: "Bodega, San Antonio",
        precio: 210000,
        tipoCamion: "Camión cerrado / furgón",
        capacidadKg: 10000,
        fechaInicio: "2026-11-22",
        fechaEntrega: "2026-11-23",
        tipoCarga: "Insumos",
        clientePublico: "Suministros Costa",
        contactoAutorizado: "contacto@suministroscosta.cl · +56 9 5555 1122",
        fechaAceptacion: "2026-11-21 15:30",
        fechaPublicacion: "Hace 2 días",
        descripcion: "Distribución de insumos en pallets en zona de descarga."
    },
    {
        id: 181,
        titulo: "Flete de muebles y equipamiento",
        estado: "FINALIZADO",
        origen: "Villa Alemana, Valparaíso",
        destino: "Limache, Valparaíso",
        precio: 95000,
        tipoCamion: "Camión cerrado / furgón",
        capacidadKg: 5000,
        fechaInicio: "2026-11-10",
        fechaEntrega: "2026-11-10",
        tipoCarga: "Equipamiento",
        clientePublico: "Carlos Pérez",
        contactoAutorizado: "carlos.perez@ejemplo.cl",
        fechaAceptacion: "2026-11-09 10:15",
        fechaPublicacion: "Hace 12 días",
        descripcion: "Flete completado sin novedades."
    }
];

let contratoPendienteAceptar = null;
let contratoPendienteCancelar = null;

const seccionBuscar = document.getElementById("seccion-buscar-contratos");
const seccionMisContratos = document.getElementById("seccion-mis-contratos");
const botonSeccionBuscar = document.getElementById("boton-seccion-buscar");
const botonSeccionMisContratos = document.getElementById("boton-seccion-mis-contratos");

const listaContratos = document.getElementById("lista-contratos");
const listaActivos = document.getElementById("lista-contratos-activos");
const listaHistorial = document.getElementById("lista-contratos-historial");
const contadorContratos = document.getElementById("contador-contratos");
const contadorMisContratos = document.getElementById("contador-mis-contratos");
const mensajeSinResultados = document.getElementById("mensaje-sin-resultados");
const sinActivos = document.getElementById("sin-contratos-activos");
const sinHistorial = document.getElementById("sin-contratos-historial");
const estadoBusqueda = document.getElementById("estado-busqueda");
const estadoMisContratos = document.getElementById("estado-mis-contratos");

const filtroOrigen = document.getElementById("filtro-origen");
const filtroDestino = document.getElementById("filtro-destino");
const precioMinimo = document.getElementById("precio-minimo");
const precioMaximo = document.getElementById("precio-maximo");
const filtroTipoCamion = document.getElementById("filtro-tipo-camion");
const filtroCapacidad = document.getElementById("filtro-capacidad");
const filtroFechaInicio = document.getElementById("filtro-fecha-inicio");
const filtroFechaEntrega = document.getElementById("filtro-fecha-entrega");
const filtroTipoCarga = document.getElementById("filtro-tipo-carga");
const ordenContratos = document.getElementById("orden-contratos");
const botonLimpiarFiltros = document.getElementById("limpiar-filtros");

const botonPerfil = document.getElementById("boton-perfil");
const menuPerfil = document.getElementById("menu-perfil");
const inicialesPerfil = document.getElementById("iniciales-perfil");

const modalDetalle = document.getElementById("modal-detalle");
const modalTitulo = document.getElementById("modal-titulo");
const modalCuerpo = document.getElementById("modal-cuerpo");
const modalAcciones = document.getElementById("modal-acciones");

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
    const limpio = String(nombre || "TR").trim();
    if (!limpio) return "TR";
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
    if (estado === "ATRASADO") return "etiqueta-estado atrasado";
    if (ESTADOS_ACTIVOS.includes(estado)) return "etiqueta-estado activo";
    if (ESTADOS_HISTORIAL.includes(estado)) return "etiqueta-estado cerrado";
    return "etiqueta-estado";
}

function obtenerUsuarioSesion() {
    // La autorización real del rol TRANSPORTISTA y la sesión deben validarse en el backend.
    try {
        const raw = localStorage.getItem("usuario_actual");
        return raw ? JSON.parse(raw) : null;
    } catch {
        return null;
    }
}

function cambiarSeccion(seccion) {
    const esBuscar = seccion === "buscar";
    seccionBuscar.classList.toggle("oculto", !esBuscar);
    seccionMisContratos.classList.toggle("oculto", esBuscar);
    botonSeccionBuscar.classList.toggle("activo", esBuscar);
    botonSeccionMisContratos.classList.toggle("activo", !esBuscar);

    if (!esBuscar) {
        obtenerMisContratos();
    } else {
        obtenerContratosDisponibles();
    }
}

function aplicarFiltros(lista) {
    const origen = filtroOrigen.value.trim().toLowerCase();
    const destino = filtroDestino.value.trim().toLowerCase();
    const minimo = precioMinimo.value === "" ? 0 : Number(precioMinimo.value);
    const maximo = precioMaximo.value === "" ? Infinity : Number(precioMaximo.value);
    const tipoCamion = filtroTipoCamion.value;
    const capacidadMin = filtroCapacidad.value === "" ? 0 : Number(filtroCapacidad.value);
    const fechaInicio = filtroFechaInicio.value;
    const fechaEntrega = filtroFechaEntrega.value;
    const tipoCarga = filtroTipoCarga.value.trim().toLowerCase();

    // El filtrado principal debe realizarse en el backend cuando exista el endpoint correspondiente.
    return lista.filter((contrato) => {
        if (contrato.estado !== "DISPONIBLE") return false;
        const cumpleOrigen = !origen || String(contrato.origen || "").toLowerCase().includes(origen);
        const cumpleDestino = !destino || String(contrato.destino || "").toLowerCase().includes(destino);
        const cumplePrecio = Number(contrato.precio) >= minimo && Number(contrato.precio) <= maximo;
        const cumpleCamion = !tipoCamion || contrato.tipoCamion === tipoCamion;
        const cumpleCapacidad = Number(contrato.capacidadKg || 0) >= capacidadMin;
        const cumpleFechaInicio = !fechaInicio || String(contrato.fechaInicio || "") >= fechaInicio;
        const cumpleFechaEntrega = !fechaEntrega || String(contrato.fechaEntrega || "") <= fechaEntrega;
        const cumpleCarga = !tipoCarga || String(contrato.tipoCarga || "").toLowerCase().includes(tipoCarga);

        return cumpleOrigen && cumpleDestino && cumplePrecio && cumpleCamion &&
            cumpleCapacidad && cumpleFechaInicio && cumpleFechaEntrega && cumpleCarga;
    });
}

function ordenarContratos(lista) {
    const criterio = ordenContratos.value;
    const copia = [...lista];

    if (criterio === "precio-alto") {
        copia.sort((a, b) => Number(b.precio) - Number(a.precio));
    } else if (criterio === "precio-bajo") {
        copia.sort((a, b) => Number(a.precio) - Number(b.precio));
    } else if (criterio === "fecha-proxima") {
        copia.sort((a, b) => String(a.fechaInicio || "").localeCompare(String(b.fechaInicio || "")));
    } else {
        copia.sort((a, b) => Number(b.id) - Number(a.id));
    }

    return copia;
}

function crearTarjetaContrato(contrato, modo) {
    const tarjeta = document.createElement("article");
    tarjeta.className = "tarjeta-contrato";

    const iniciales = obtenerIniciales(contrato.clientePublico || contrato.cliente || "CL");
    const estadoActual = contrato.estado || "DISPONIBLE";
    const esDisponible = modo === "disponible" && estadoActual === "DISPONIBLE";
    const puedeCancelar = modo === "mis-contratos" && ESTADOS_ACTIVOS.includes(estadoActual);

    tarjeta.innerHTML = `
        <div class="tarjeta-superior">
            <span class="${claseEstado(estadoActual)}">${escaparTexto(estadoActual)}</span>
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
        <div class="especificaciones-contrato">
            <span>${escaparTexto(contrato.tipoCamion || "Camión por definir")}</span>
            <span>${escaparTexto(contrato.capacidadKg ? `${contrato.capacidadKg} kg` : "Capacidad s/d")}</span>
            <span>${escaparTexto(contrato.tipoCarga || "Carga general")}</span>
        </div>
        <div class="cliente-contrato">
            <span class="avatar-cliente">${escaparTexto(iniciales)}</span>
            <span><strong>${escaparTexto(contrato.clientePublico || "Dador de carga")}</strong><br>${escaparTexto(contrato.tipoCliente || "Cliente")}</span>
        </div>
        <div class="pie-tarjeta">
            <span>Publicado: ${escaparTexto(contrato.fechaPublicacion || "No disponible")}</span>
            <span>Inicio: ${escaparTexto(contrato.fechaInicio || "Por coordinar")}</span>
        </div>
        <div class="acciones-tarjeta">
            <button type="button" class="boton-secundario boton-detalle">Ver detalle</button>
            ${esDisponible ? `<button type="button" class="boton-principal boton-aceptar">Aceptar contrato</button>` : ""}
            ${puedeCancelar ? `<button type="button" class="boton-peligro boton-cancelar">Cancelar contrato</button>` : ""}
        </div>
    `;

    tarjeta.querySelector(".boton-detalle").addEventListener("click", () => mostrarDetalleContrato(contrato, modo));

    const botonAceptar = tarjeta.querySelector(".boton-aceptar");
    if (botonAceptar) {
        botonAceptar.addEventListener("click", () => confirmarAceptacion(contrato));
    }

    const botonCancelar = tarjeta.querySelector(".boton-cancelar");
    if (botonCancelar) {
        botonCancelar.addEventListener("click", () => abrirModalCancelar(contrato));
    }

    return tarjeta;
}

function mostrarContratos(lista) {
    listaContratos.replaceChildren();
    lista.forEach((contrato) => {
        listaContratos.appendChild(crearTarjetaContrato(contrato, "disponible"));
    });
    contadorContratos.textContent = `${lista.length} ${lista.length === 1 ? "contrato" : "contratos"}`;
    mensajeSinResultados.classList.toggle("oculto", lista.length !== 0);
}

function renderizarMisContratos(contratosAsignados) {
    const activos = contratosAsignados.filter((c) => ESTADOS_ACTIVOS.includes(c.estado));
    const historial = contratosAsignados.filter((c) => ESTADOS_HISTORIAL.includes(c.estado));

    listaActivos.replaceChildren();
    activos.forEach((c) => listaActivos.appendChild(crearTarjetaContrato(c, "mis-contratos")));
    sinActivos.classList.toggle("oculto", activos.length !== 0);

    listaHistorial.replaceChildren();
    historial.forEach((c) => listaHistorial.appendChild(crearTarjetaContrato(c, "mis-contratos")));
    sinHistorial.classList.toggle("oculto", historial.length !== 0);

    contadorMisContratos.textContent = `${activos.length} activos · ${historial.length} historial`;
}

function mostrarDetalleContrato(contrato, modo) {
    modalTitulo.textContent = contrato.titulo || "Detalle del contrato";

    // No se muestran datos privados del dador antes de aceptar el contrato.
    const bloqueContacto = modo === "mis-contratos" && contrato.contactoAutorizado
        ? `<p><strong>Contacto autorizado:</strong> ${escaparTexto(contrato.contactoAutorizado)}</p>`
        : `<p><strong>Contacto privado:</strong> Disponible una vez aceptado el contrato.</p>`;

    modalCuerpo.innerHTML = `
        <p><strong>Estado:</strong> ${escaparTexto(contrato.estado)}</p>
        <p><strong>Monto:</strong> ${formatearPrecio(contrato.precio)}</p>
        <p><strong>Origen:</strong> ${escaparTexto(contrato.origen)}</p>
        <p><strong>Destino:</strong> ${escaparTexto(contrato.destino)}</p>
        <p><strong>Tipo de camión:</strong> ${escaparTexto(contrato.tipoCamion || "No especificado")}</p>
        <p><strong>Capacidad / peso:</strong> ${escaparTexto(contrato.capacidadKg ? `${contrato.capacidadKg} kg` : "No especificado")}</p>
        <p><strong>Tipo de carga:</strong> ${escaparTexto(contrato.tipoCarga || "No especificado")}</p>
        <p><strong>Fecha de inicio:</strong> ${escaparTexto(contrato.fechaInicio || "Por coordinar")}</p>
        <p><strong>Fecha límite de entrega:</strong> ${escaparTexto(contrato.fechaEntrega || "Por coordinar")}</p>
        <p><strong>Dador de carga:</strong> ${escaparTexto(contrato.clientePublico || "No disponible")}</p>
        ${bloqueContacto}
        <p><strong>Descripción:</strong> ${escaparTexto(contrato.descripcion || "Sin descripción adicional.")}</p>
    `;

    modalAcciones.replaceChildren();

    const btnCerrar = document.createElement("button");
    btnCerrar.type = "button";
    btnCerrar.className = "boton-secundario";
    btnCerrar.textContent = "Cerrar";
    btnCerrar.addEventListener("click", cerrarModalDetalle);
    modalAcciones.appendChild(btnCerrar);

    if (modo === "disponible" && contrato.estado === "DISPONIBLE") {
        const btnAceptar = document.createElement("button");
        btnAceptar.type = "button";
        btnAceptar.className = "boton-principal";
        btnAceptar.textContent = "Aceptar contrato";
        btnAceptar.addEventListener("click", () => {
            cerrarModalDetalle();
            confirmarAceptacion(contrato);
        });
        modalAcciones.appendChild(btnAceptar);
    }

    modalDetalle.classList.remove("oculto");
}

function cerrarModalDetalle() {
    modalDetalle.classList.add("oculto");
}

function confirmarAceptacion(contrato) {
    contratoPendienteAceptar = contrato;
    modalTitulo.textContent = "Confirmar aceptación de contrato";
    modalCuerpo.innerHTML = `
        <p>¿Realmente deseas aceptar el contrato <strong>${escaparTexto(contrato.titulo)}</strong> por <strong>${formatearPrecio(contrato.precio)}</strong>?</p>
        <p><strong>Ruta:</strong> ${escaparTexto(contrato.origen)} → ${escaparTexto(contrato.destino)}</p>
    `;
    modalAcciones.replaceChildren();

    const btnCancelar = document.createElement("button");
    btnCancelar.type = "button";
    btnCancelar.className = "boton-secundario";
    btnCancelar.textContent = "No, volver";
    btnCancelar.addEventListener("click", () => {
        contratoPendienteAceptar = null;
        cerrarModalDetalle();
    });

    const btnConfirmar = document.createElement("button");
    btnConfirmar.type = "button";
    btnConfirmar.className = "boton-principal";
    btnConfirmar.textContent = "Sí, aceptar contrato";
    btnConfirmar.addEventListener("click", () => {
        const seleccionado = contratoPendienteAceptar;
        contratoPendienteAceptar = null;
        cerrarModalDetalle();
        if (seleccionado) {
            aceptarContrato(seleccionado);
        }
    });

    modalAcciones.appendChild(btnCancelar);
    modalAcciones.appendChild(btnConfirmar);
    modalDetalle.classList.remove("oculto");
}

async function aceptarContrato(contrato) {
    mostrarEstado(estadoBusqueda, "Procesando aceptación del contrato...");
    // Integración pendiente con backend:
    // Se Debe validar rol TRANSPORTISTA, disponibilidad atómica del contrato, asignar transportista,
    // registrar fecha/hora de aceptación y responder si ya no está disponible.
    try {
        const indice = contratosDisponiblesDemo.findIndex((c) => c.id === contrato.id && c.estado === "DISPONIBLE");
        if (indice === -1) {
            mostrarEstado(estadoBusqueda, "Este contrato ya no está disponible.", "error");
            obtenerContratosDisponibles();
            return;
        }

        const [aceptado] = contratosDisponiblesDemo.splice(indice, 1);
        aceptado.estado = "ACEPTADO";
        aceptado.fechaAceptacion = new Date().toISOString();
        misContratosDemo.unshift(aceptado);

        mostrarEstado(estadoBusqueda, "Contrato aceptado. Ya figura en tu sección Mis contratos.", "exito");
        obtenerContratosDisponibles();
    } catch {
        mostrarEstado(estadoBusqueda, "No fue posible aceptar el contrato. Intenta nuevamente.", "error");
    }
}

function abrirModalCancelar(contrato) {
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
        mostrarEstado(estadoMisContratos, "Debes seleccionar un motivo de cancelación.", "error");
        return;
    }

    if (motivo === "Otro motivo" && (!explicacion || explicacion.length > 300)) {
        mostrarEstado(estadoMisContratos, "Debes ingresar una explicación de hasta 300 caracteres para 'Otro motivo'.", "error");
        return;
    }

    // Integración pendiente con backend:
    // Debe registrar quién canceló, fecha/hora, motivo y explicación adicional sin permitir edición posterior.
    const objetivo = misContratosDemo.find((c) => c.id === contratoPendienteCancelar.id);
    if (objetivo) {
        objetivo.estado = "CANCELADO";
        objetivo.motivoCancelacion = motivo;
        objetivo.explicacionCancelacion = motivo === "Otro motivo" ? explicacion : "";
    }

    cerrarModalCancelar();
    mostrarEstado(estadoMisContratos, "Contrato cancelado y movido al historial.", "exito");
    obtenerMisContratos();
}

function obtenerContratosDisponibles() {
    mostrarEstado(estadoBusqueda, "");
    const filtrados = aplicarFiltros(contratosDisponiblesDemo);
    const ordenados = ordenarContratos(filtrados);
    mostrarContratos(ordenados);
}

function obtenerMisContratos() {
    mostrarEstado(estadoMisContratos, "");
    renderizarMisContratos(misContratosDemo);
}

function limpiarFiltros() {
    filtroOrigen.value = "";
    filtroDestino.value = "";
    precioMinimo.value = "";
    precioMaximo.value = "";
    filtroTipoCamion.value = "";
    filtroCapacidad.value = "";
    filtroFechaInicio.value = "";
    filtroFechaEntrega.value = "";
    filtroTipoCarga.value = "";
    ordenContratos.value = "recientes";
    obtenerContratosDisponibles();
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
        ////////////////////////////////////////////////////////////////////////////////////////////////// agregar path de Editar usuario
        alert("Pendiente conexión: agregar path de Editar usuario");
    } else if (accion === "configuracion") {
        ////////////////////////////////////////////////////////////////////////////////////////////////// agregar path de Configuración de la aplicación
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
        inicialesPerfil.textContent = "TR";
    }

    botonSeccionBuscar.addEventListener("click", () => cambiarSeccion("buscar"));
    botonSeccionMisContratos.addEventListener("click", () => cambiarSeccion("mis-contratos"));

    [
        filtroOrigen, filtroDestino, precioMinimo, precioMaximo,
        filtroTipoCamion, filtroCapacidad, filtroFechaInicio,
        filtroFechaEntrega, filtroTipoCarga, ordenContratos
    ].forEach((control) => {
        control.addEventListener("input", obtenerContratosDisponibles);
        control.addEventListener("change", obtenerContratosDisponibles);
    });

    botonLimpiarFiltros.addEventListener("click", limpiarFiltros);

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

    obtenerContratosDisponibles();
}

document.addEventListener("DOMContentLoaded", inicializarPagina);