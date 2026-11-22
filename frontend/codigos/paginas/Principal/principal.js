// =================================
// CONFIGURACIÓN DE API BACKEND
// =================================

const API_BASE_URL = window.API_BASE_URL || "http://127.0.0.1:8000";

// =================================
// CONFIGURACIÓN DE HOME
// =================================

const usuarioGuardado = localStorage.getItem("usuario_actual");

const usuarioActual = JSON.parse(usuarioGuardado);

// Datos demostrativos. Sustituir por los objetos recibidos desde la base de datos.
const contratos = [
    {
        id: 101,
        titulo: "Transporte de materiales de construcción",
        puntoInicio: "Puerto de Valparaíso, Valparaíso",
        puntoFinal: "Obra, Viña del Mar",
        precio: 185000,
        cliente: "Constructora Horizonte",
        tipoCliente: "Empresa",
        fechaPublicacion: "Hoy",
        descripcion: "Traslado de materiales de construcción. Coordinar horario de carga con el cliente."
    },
    {
        id: 102,
        titulo: "Traslado de carga industrial",
        puntoInicio: "Quilpué, Valparaíso",
        puntoFinal: "Centro logístico, Santiago",
        precio: 320000,
        cliente: "Logística del Pacífico",
        tipoCliente: "Empresa",
        fechaPublicacion: "Hace 1 día",
        descripcion: "Transporte de carga industrial embalada. Confirmar dimensiones y peso antes del retiro."
    },
    {
        id: 103,
        titulo: "Entrega de productos agrícolas",
        puntoInicio: "La Calera, Valparaíso",
        puntoFinal: "Mercado mayorista, Santiago",
        precio: 145000,
        cliente: "María González",
        tipoCliente: "Persona",
        fechaPublicacion: "Hace 2 días",
        descripcion: "Entrega de productos agrícolas. Coordinar la recepción con la persona responsable."
    },
    {
        id: 104,
        titulo: "Distribución de insumos",
        puntoInicio: "Concón, Valparaíso",
        puntoFinal: "Bodega, San Antonio",
        precio: 210000,
        cliente: "Suministros Costa",
        tipoCliente: "Empresa",
        fechaPublicacion: "Hoy",
        descripcion: "Distribución de insumos en pallets. Descarga en la zona de recepción de la bodega."
    },
    {
        id: 105,
        titulo: "Retiro de maquinaria",
        puntoInicio: "Los Andes, Valparaíso",
        puntoFinal: "Taller industrial, Quilicura",
        precio: 395000,
        cliente: "Maquinarias del Sur",
        tipoCliente: "Empresa",
        fechaPublicacion: "Hace 3 días",
        descripcion: "Retiro y traslado de maquinaria. Confirmar equipo de carga y condiciones de acceso."
    },
    {
        id: 106,
        titulo: "Flete de muebles y equipamiento",
        puntoInicio: "Villa Alemana, Valparaíso",
        puntoFinal: "Limache, Valparaíso",
        precio: 95000,
        cliente: "Carlos Pérez",
        tipoCliente: "Persona",
        fechaPublicacion: "Hace 4 días",
        descripcion: "Flete de muebles y equipamiento. Coordinar con el cliente la carga y descarga."
    },
    {
        id: 107,
        titulo: "Traslado de pallets de alimentos",
        puntoInicio: "Bodega, Casablanca",
        puntoFinal: "Centro de distribución, Rancagua",
        precio: 275000,
        cliente: "Alimentos Buen Campo",
        tipoCliente: "Empresa",
        fechaPublicacion: "Hoy",
        descripcion: "Traslado de pallets de alimentos en vehículo limpio y adecuado para la carga."
    },
    {
        id: 108,
        titulo: "Despacho de materiales eléctricos",
        puntoInicio: "Placilla, Valparaíso",
        puntoFinal: "Local comercial, Talca",
        precio: 240000,
        cliente: "ElectroRed Comercial",
        tipoCliente: "Empresa",
        fechaPublicacion: "Hace 1 día",
        descripcion: "Despacho de materiales eléctricos embalados. Entrega contra confirmación de recepción."
    },
    {
        id: 109,
        titulo: "Mudanza de oficina pequeña",
        puntoInicio: "Recreo, Viña del Mar",
        puntoFinal: "Centro de Viña del Mar",
        precio: 125000,
        cliente: "Andrés Muñoz",
        tipoCliente: "Persona",
        fechaPublicacion: "Hace 2 días",
        descripcion: "Traslado de escritorios, sillas, cajas y equipos de oficina. Coordinar horario con el cliente."
    },
    {
        id: 110,
        titulo: "Transporte de perfiles metálicos",
        puntoInicio: "Parque industrial, Quilicura",
        puntoFinal: "Obra, San Felipe",
        precio: 360000,
        cliente: "Aceros Cordillera",
        tipoCliente: "Empresa",
        fechaPublicacion: "Hoy",
        descripcion: "Transporte de perfiles metálicos. Verificar longitud de la carga y sujeción segura."
    },
    {
        id: 111,
        titulo: "Retiro de residuos no peligrosos",
        puntoInicio: "Obra, Concón",
        puntoFinal: "Centro autorizado, Valparaíso",
        precio: 155000,
        cliente: "Gestión Ambiental Verde",
        tipoCliente: "Empresa",
        fechaPublicacion: "Hace 3 días",
        descripcion: "Retiro de residuos no peligrosos y traslado a un centro autorizado, según coordinación."
    },
    {
        id: 112,
        titulo: "Entrega de muebles de madera",
        puntoInicio: "Taller, Limache",
        puntoFinal: "Local comercial, La Serena",
        precio: 330000,
        cliente: "Muebles Roble",
        tipoCliente: "Empresa",
        fechaPublicacion: "Hace 1 día",
        descripcion: "Entrega de muebles embalados. Proteger la carga y solicitar firma de recepción."
    },
    {
        id: 113,
        titulo: "Transporte de herramientas",
        puntoInicio: "Bodega, San Antonio",
        puntoFinal: "Faena, Melipilla",
        precio: 175000,
        cliente: "Herramientas del Puerto",
        tipoCliente: "Empresa",
        fechaPublicacion: "Hace 2 días",
        descripcion: "Traslado de herramientas y equipos menores. Revisar el inventario al retirar y entregar."
    },
    {
        id: 114,
        titulo: "Flete de electrodomésticos",
        puntoInicio: "Quilpué, Valparaíso",
        puntoFinal: "Puchuncaví, Valparaíso",
        precio: 110000,
        cliente: "Daniela Rojas",
        tipoCliente: "Persona",
        fechaPublicacion: "Hoy",
        descripcion: "Traslado de electrodomésticos protegidos para evitar golpes durante el viaje."
    },
    {
        id: 115,
        titulo: "Distribución de productos de limpieza",
        puntoInicio: "Centro de distribución, Santiago",
        puntoFinal: "Locales comerciales, Valparaíso",
        precio: 295000,
        cliente: "Higiene Total",
        tipoCliente: "Empresa",
        fechaPublicacion: "Hace 4 días",
        descripcion: "Distribución de productos de limpieza en varios puntos. Confirmar orden de entrega."
    },
    {
        id: 116,
        titulo: "Traslado de equipos agrícolas",
        puntoInicio: "San Felipe, Valparaíso",
        puntoFinal: "Predio agrícola, Ovalle",
        precio: 420000,
        cliente: "Agroservicios El Valle",
        tipoCliente: "Empresa",
        fechaPublicacion: "Hace 1 día",
        descripcion: "Traslado de equipos agrícolas. Revisar dimensiones, peso y método de carga."
    },
    {
        id: 117,
        titulo: "Entrega de materiales de ferretería",
        puntoInicio: "Bodega, Villa Alemana",
        puntoFinal: "Ferretería, Quillota",
        precio: 88000,
        cliente: "Ferretería Central",
        tipoCliente: "Empresa",
        fechaPublicacion: "Hoy",
        descripcion: "Entrega de cajas de herramientas y materiales de ferretería durante el horario comercial."
    },
    {
        id: 118,
        titulo: "Traslado de cajas para evento",
        puntoInicio: "Bodega, Viña del Mar",
        puntoFinal: "Centro de eventos, Casablanca",
        precio: 135000,
        cliente: "Eventos Brisa",
        tipoCliente: "Empresa",
        fechaPublicacion: "Hace 3 días",
        descripcion: "Traslado de cajas y equipamiento para evento. Cumplir el horario de montaje acordado."
    },
    {
        id: 119,
        titulo: "Transporte de fruta fresca",
        puntoInicio: "Productora, Quillota",
        puntoFinal: "Centro de distribución, Santiago",
        precio: 265000,
        cliente: "Frutas Santa Clara",
        tipoCliente: "Empresa",
        fechaPublicacion: "Hace 1 día",
        descripcion: "Transporte de fruta fresca. Confirmar condiciones de conservación y horario de recepción."
    },
    {
        id: 120,
        titulo: "Flete de artículos para el hogar",
        puntoInicio: "Curauma, Valparaíso",
        puntoFinal: "La Ligua, Valparaíso",
        precio: 160000,
        cliente: "Patricia Silva",
        tipoCliente: "Persona",
        fechaPublicacion: "Hace 2 días",
        descripcion: "Traslado de artículos para el hogar. El cliente coordinará el acceso al punto de entrega."
    }
];

const listaContratos = document.getElementById("lista-contratos");
const precioMinimo = document.getElementById("precio-minimo");
const precioMaximo = document.getElementById("precio-maximo");
const filtroEmpresa = document.getElementById("filtro-empresa");
const botonLimpiarFiltros = document.getElementById("limpiar-filtros");
const contadorContratos = document.getElementById("contador-contratos");
const mensajeSinResultados = document.getElementById("mensaje-sin-resultados");
const botonPerfil = document.getElementById("boton-perfil");
const menuPerfil = document.getElementById("menu-perfil");
const inicialesPerfil = document.getElementById("iniciales-perfil");

function formatearPrecio(precio) {
    return new Intl.NumberFormat("es-CL", {
        style: "currency",
        currency: "CLP",
        maximumFractionDigits: 0
    }).format(precio);
}

function obtenerIniciales(nombre) {
    return nombre
        .trim()
        .split(/\s+/)
        .slice(0, 2)
        .map((palabra) => palabra.charAt(0).toLocaleUpperCase("es-CL"))
        .join("");
}

function crearTarjetaContrato(contrato) {
    const tarjeta = document.createElement("button");
    tarjeta.type = "button";
    tarjeta.className = "tarjeta-contrato";
    tarjeta.setAttribute("aria-label", `Ver detalles del contrato: ${contrato.titulo}`);

    const inicialesCliente = obtenerIniciales(contrato.cliente);

    tarjeta.innerHTML = `
        <div class="tarjeta-superior">
            <span class="precio-contrato">${formatearPrecio(contrato.precio)}</span>
        </div>
        <h3 class="titulo-contrato">${escaparTexto(contrato.titulo)}</h3>
        <div class="ruta-contrato">
            <div class="punto-ruta">
                <span class="icono-punto"></span>
                <span><strong>Inicio:</strong> ${escaparTexto(contrato.puntoInicio)}</span>
            </div>
            <div class="punto-ruta destino">
                <span class="icono-punto"></span>
                <span><strong>Destino:</strong> ${escaparTexto(contrato.puntoFinal)}</span>
            </div>
        </div>
        <div class="cliente-contrato">
            <span class="avatar-cliente">${escaparTexto(inicialesCliente)}</span>
            <span><strong>${escaparTexto(contrato.cliente)}</strong><br>${escaparTexto(contrato.tipoCliente)}</span>
        </div>
        <div class="pie-tarjeta">
            <span>${escaparTexto(contrato.fechaPublicacion || "Fecha no disponible")}</span>
            <span class="ver-detalle">Ver detalles →</span>
        </div>
    `;

    tarjeta.addEventListener("click", () => abrirDetalleContrato(contrato));
    return tarjeta;
}

function abrirCrearContrato() { // editar
    // window.location.href = ""; 
}

function abrirMisContratos() { // editar
    // window.location.href = ""; 
}

function escaparTexto(valor) {
    // Evita insertar texto recibido de la API como HTML ejecutable.
    return String(valor ?? "").replace(/[&<>"']/g, (caracter) => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#039;"
    })[caracter]);
}

function mostrarContratos(lista) {
    listaContratos.replaceChildren();

    lista.forEach((contrato) => {
        listaContratos.appendChild(crearTarjetaContrato(contrato));
    });

    contadorContratos.textContent = `${lista.length} ${lista.length === 1 ? "contrato" : "contratos"}`;
    mensajeSinResultados.classList.toggle("oculto", lista.length !== 0);
}

function cargarOpcionesEmpresas() {
    const empresas = [...new Set(contratos.map((contrato) => contrato.cliente))]
        .sort((empresaA, empresaB) => empresaA.localeCompare(empresaB, "es-CL"));

    empresas.forEach((empresa) => {
        const opcion = document.createElement("option");
        opcion.value = empresa;
        opcion.textContent = empresa;
        filtroEmpresa.appendChild(opcion);
    });
}

function filtrarContratos() {
    const minimo = precioMinimo.value === "" ? 0 : Number(precioMinimo.value);
    const maximo = precioMaximo.value === "" ? Infinity : Number(precioMaximo.value);
    const empresaSeleccionada = filtroEmpresa.value;

    const contratosFiltrados = contratos.filter((contrato) => {
        const cumplePrecio = contrato.precio >= minimo && contrato.precio <= maximo;
        const cumpleEmpresa = !empresaSeleccionada || contrato.cliente === empresaSeleccionada;

        
        //  AGREGAR MÁS FILTROS AQUI
         
        return cumplePrecio && cumpleEmpresa;
    });

    mostrarContratos(contratosFiltrados);
}

function limpiarFiltros() {
    precioMinimo.value = "";
    precioMaximo.value = "";
    filtroEmpresa.value = "";
    filtrarContratos();
}

function abrirDetalleContrato(contrato) {

    /*
    window.location.href = `?id=${encodeURIComponent(contrato.id)}`;
    */
    console.log("Contrato seleccionado para ver detalle:", contrato);
    alert(`Seleccionaste "${contrato.titulo}".\n\n`);
}

function alternarMenuPerfil() {
    const estaOculto = menuPerfil.classList.toggle("oculto");
    botonPerfil.setAttribute("aria-expanded", String(!estaOculto));
}

function gestionarAccionPerfil(evento) {
    const boton = evento.target.closest("[data-accion-perfil]");
    if (!boton) return;

    const accion = boton.dataset.accionPerfil;
    menuPerfil.classList.add("oculto");
    botonPerfil.setAttribute("aria-expanded", "false");

   
    if (accion === "editar") {
        alert("conectar la pantalla para editar los datos del usuario.");
    } else if (accion === "configuracion") {
        alert("conectar la pantalla de configuración de la aplicación.");
    } else if (accion === "cerrar") {

        localStorage.removeItem("sesion_usuario");

        window.location.replace("../Login/index.html");
    }
}

function inicializarPantallaPrincipal() {
    inicialesPerfil.textContent = usuarioActual.iniciales || obtenerIniciales(usuarioActual.nombre);
    cargarOpcionesEmpresas();
    mostrarContratos(contratos);

    precioMinimo.addEventListener("input", filtrarContratos);
    precioMaximo.addEventListener("input", filtrarContratos);
    filtroEmpresa.addEventListener("change", filtrarContratos);
    botonLimpiarFiltros.addEventListener("click", limpiarFiltros);

    botonPerfil.addEventListener("click", (evento) => {
        evento.stopPropagation();
        alternarMenuPerfil();
    });

    menuPerfil.addEventListener("click", gestionarAccionPerfil);

    document.getElementById("boton-crear-contrato").addEventListener("click", abrirCrearContrato);

    document.getElementById("boton-mis-contratos").addEventListener("click", abrirMisContratos);

    document.addEventListener("click", (evento) => {
        if (!menuPerfil.contains(evento.target) && !botonPerfil.contains(evento.target)) {
            menuPerfil.classList.add("oculto");
            botonPerfil.setAttribute("aria-expanded", "false");
        }
    });

}

document.addEventListener("DOMContentLoaded", inicializarPantallaPrincipal);
