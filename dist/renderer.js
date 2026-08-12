"use strict";
// Base URL of the FastAPI backend service
const urlBase = "http://127.0.0.1:8000";
// Set minimum date input to today
const fechaLimiteInput = document.getElementById('fecha_limite');
if (fechaLimiteInput) {
    fechaLimiteInput.min = new Date().toISOString().split('T')[0];
}
// Currency formatter for Chilean Peso (CLP)
const formatearMoneda = (valor) => {
    return new Intl.NumberFormat('es-CL', {
        style: 'currency',
        currency: 'CLP',
        maximumFractionDigits: 0
    }).format(valor);
};
// Fetch all contracts and update the UI
async function obtenerContratos() {
    try {
        const respuesta = await fetch(`${urlBase}/solicitudes/`);
        if (!respuesta.ok) {
            throw new Error(`Failed to fetch contracts: ${respuesta.statusText}`);
        }
        const contratos = await respuesta.json();
        actualizarEstadisticas(contratos);
        renderizarContratos(contratos);
    }
    catch (error) {
        console.error("Error al obtener los contratos:", error);
    }
}
// Update the summary statistic cards
function actualizarEstadisticas(contratos) {
    const totalContratos = contratos.length;
    const totalTons = contratos.reduce((suma, c) => suma + c.cantidad_carga, 0);
    const totalTarifas = contratos.reduce((suma, c) => suma + c.tarifa_propuesta, 0);
    const statContratos = document.getElementById('stat-contratos');
    const statToneladas = document.getElementById('stat-toneladas');
    const statTarifas = document.getElementById('stat-tarifas');
    if (statContratos)
        statContratos.innerText = totalContratos.toString();
    if (statToneladas)
        statToneladas.innerText = totalTons.toFixed(1);
    if (statTarifas)
        statTarifas.innerText = formatearMoneda(totalTarifas);
}
// Dynamically build and render the contract cards list
function renderizarContratos(contratos) {
    const contenedor = document.getElementById('lista-contratos');
    if (!contenedor)
        return;
    contenedor.innerHTML = '';
    if (contratos.length === 0) {
        contenedor.innerHTML = `
            <div style="text-align: center; padding: 3rem; color: var(--text-muted);">
                No hay contratos registrados actualmente.
            </div>
        `;
        return;
    }
    contratos.forEach(contrato => {
        const tarjeta = document.createElement('div');
        tarjeta.className = 'tarjeta-contrato';
        // CSS class for the status badge
        let claseEstado = 'pendiente';
        if (contrato.estado === 'Asignado')
            claseEstado = 'asignado';
        if (contrato.estado === 'En Ruta')
            claseEstado = 'en-ruta';
        if (contrato.estado === 'Entregado')
            claseEstado = 'entregado';
        // Truck assignment block
        let htmlCamion = '';
        if (contrato.camion_asignado) {
            htmlCamion = `
                <div class="seccion-camion">
                    <div class="camion-info">
                        <span>🚚 Camión Asignado:</span>
                        <span class="camion-placa">${contrato.camion_asignado}</span>
                    </div>
                </div>
            `;
        }
        else if (contrato.estado === 'Pendiente') {
            htmlCamion = `
                <div class="seccion-camion" id="form-camion-${contrato.id_contrato}">
                    <div class="formulario-asignar">
                        <input type="text" id="placa-${contrato.id_contrato}" placeholder="Patente Camión" required>
                        <button onclick="asignarCamion(${contrato.id_contrato})">Asignar</button>
                    </div>
                </div>
            `;
        }
        // Action buttons based on the contract lifecycle state
        let htmlAcciones = '';
        if (contrato.estado === 'Asignado') {
            htmlAcciones = `
                <button class="btn-accion btn-primario" onclick="cambiarEstado(${contrato.id_contrato}, 'En Ruta')">
                    🛫 Iniciar Viaje (En Ruta)
                </button>
            `;
        }
        else if (contrato.estado === 'En Ruta') {
            htmlAcciones = `
                <button class="btn-accion btn-completar" onclick="cambiarEstado(${contrato.id_contrato}, 'Entregado')">
                    ✅ Completar Entrega
                </button>
            `;
        }
        // Delete button
        const htmlBotonEliminar = `
            <button class="btn-accion btn-danger" onclick="eliminarContrato(${contrato.id_contrato})">
                🗑️ Eliminar
            </button>
        `;
        tarjeta.innerHTML = `
            <div class="cabecera-contrato">
                <span class="id-flete">Contrato #${contrato.id_contrato}</span>
                <span class="badge-estado estado-${claseEstado}">${contrato.estado}</span>
            </div>
            
            <div class="cuerpo-contrato">
                <div class="detalle-item">
                    <span>Material</span>
                    <span>${contrato.tipo_material}</span>
                </div>
                <div class="detalle-item">
                    <span>Peso</span>
                    <span>${contrato.cantidad_carga} Toneladas</span>
                </div>
                <div class="detalle-item">
                    <span>Ruta</span>
                    <span>📍 ${contrato.origen} ➔ 🏁 ${contrato.destino}</span>
                </div>
                <div class="detalle-item">
                    <span>Tarifa</span>
                    <span style="color: var(--accent-success); font-weight: 700;">
                        ${formatearMoneda(contrato.tarifa_propuesta)}
                    </span>
                </div>
                <div class="detalle-item">
                    <span>Fecha Límite</span>
                    <span>📅 ${contrato.fecha_limite}</span>
                </div>
            </div>

            ${htmlCamion}

            <div class="acciones-contrato">
                ${htmlAcciones}
                ${htmlBotonEliminar}
            </div>
        `;
        contenedor.appendChild(tarjeta);
    });
}
// Create a new contract
async function crearContrato(event) {
    event.preventDefault();
    const tipoMaterialEl = document.getElementById('tipo_material');
    const cantidadCargaEl = document.getElementById('cantidad_carga');
    const tarifaPropuestaEl = document.getElementById('tarifa_propuesta');
    const origenEl = document.getElementById('origen');
    const destinoEl = document.getElementById('destino');
    const fechaLimiteEl = document.getElementById('fecha_limite');
    if (!tipoMaterialEl || !cantidadCargaEl || !tarifaPropuestaEl || !origenEl || !destinoEl || !fechaLimiteEl) {
        return;
    }
    const carga = {
        tipo_material: tipoMaterialEl.value,
        cantidad_carga: parseFloat(cantidadCargaEl.value),
        tarifa_propuesta: parseInt(tarifaPropuestaEl.value),
        origen: origenEl.value,
        destino: destinoEl.value,
        fecha_limite: fechaLimiteEl.value
    };
    try {
        const respuesta = await fetch(`${urlBase}/solicitudes/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(carga)
        });
        if (respuesta.ok) {
            const form = document.getElementById('formulario-registro');
            if (form)
                form.reset();
            if (fechaLimiteInput) {
                fechaLimiteInput.min = new Date().toISOString().split('T')[0];
            }
            obtenerContratos();
        }
        else {
            const errorRes = await respuesta.json();
            alert("Error al guardar: " + JSON.stringify(errorRes.detail));
        }
    }
    catch (error) {
        console.error("Error al registrar contrato:", error);
    }
}
// Assign a truck plate to a contract
async function asignarCamion(id) {
    const entradaPlaca = document.getElementById(`placa-${id}`);
    if (!entradaPlaca)
        return;
    const placa = entradaPlaca.value.trim();
    if (!placa) {
        alert("Por favor, ingresa una patente válida.");
        return;
    }
    try {
        const respuesta = await fetch(`${urlBase}/solicitudes/${id}/camion/`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ camion: placa })
        });
        if (respuesta.ok) {
            obtenerContratos();
        }
        else {
            alert("Error al asignar camión.");
        }
    }
    catch (error) {
        console.error("Error al conectar con el servidor:", error);
    }
}
// Update the status of a contract
async function cambiarEstado(id, nuevoEstado) {
    try {
        const respuesta = await fetch(`${urlBase}/solicitudes/${id}/estado/`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ estado: nuevoEstado })
        });
        if (respuesta.ok) {
            obtenerContratos();
        }
        else {
            alert("Error al cambiar estado.");
        }
    }
    catch (error) {
        console.error("Error al actualizar estado:", error);
    }
}
// Delete a contract
async function eliminarContrato(id) {
    if (!confirm("¿Estás seguro de que deseas eliminar este contrato?"))
        return;
    try {
        const respuesta = await fetch(`${urlBase}/solicitudes/${id}`, {
            method: 'DELETE'
        });
        if (respuesta.ok) {
            obtenerContratos();
        }
        else {
            alert("Error al eliminar el contrato.");
        }
    }
    catch (error) {
        console.error("Error al eliminar:", error);
    }
}
// Setup form submit listener
const formRegistro = document.getElementById('formulario-registro');
if (formRegistro) {
    formRegistro.addEventListener('submit', crearContrato);
}
// Expose functions globally to be called from HTML onclick attributes
window.crearContrato = crearContrato;
window.asignarCamion = asignarCamion;
window.cambiarEstado = cambiarEstado;
window.eliminarContrato = eliminarContrato;
// Handle Swagger documentation button click to open in user's browser
const btnDocs = document.getElementById('btn-docs');
if (btnDocs) {
    btnDocs.addEventListener('click', () => {
        if (window.electronAPI && typeof window.electronAPI.openExternal === 'function') {
            window.electronAPI.openExternal(`${urlBase}/docs`);
        }
        else {
            window.open(`${urlBase}/docs`, '_blank');
        }
    });
}
// Initial fetch on application load
obtenerContratos();
