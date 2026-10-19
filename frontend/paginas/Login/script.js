// =================================
// CONFIGURACIÓN DE API BACKEND
// =================================

const API_BASE_URL = window.API_BASE_URL || "http://127.0.0.1:8000";

// =================================
// ELEMENTOS DEL DOM
// =================================

const btnLogin = document.getElementById("btnLogin");
const emailInput = document.getElementById("email");
const passwordInput = document.getElementById("password");
const mensajeLogin = document.getElementById("mensajeLogin");

const seccionLogin = document.getElementById("seccionLogin");
const seccionFuncionalidades = document.getElementById("seccionFuncionalidades");
const usuarioSaludo = document.getElementById("usuarioSaludo");
const usuarioRol = document.getElementById("usuarioRol");
const usuarioEmailInfo = document.getElementById("usuarioEmailInfo");
const contenedorFuncionalidades = document.getElementById("contenedorFuncionalidades");
const btnCerrarSesion = document.getElementById("btnCerrarSesion");

// =================================
// DEFINICIÓN DE FUNCIONALIDADES POR ROL (CA4)
// =================================

const FUNCIONALIDADES_POR_ROL = {
    TRANSPORTISTA: [
        {
            icono: "🚛",
            titulo: "Subastas y Cargas Disponibles",
            descripcion: "Explora las cargas publicadas en la plataforma y envía tus postulaciones con ofertas de flete.",
            accionTexto: "Ver Subastas",
            modulo: "subastas",
        },
        {
            icono: "📄",
            titulo: "Documentación y Compliance",
            descripcion: "Revisa el estado de verificación de tu licencia, padrón vehicular, revisión técnica y seguros.",
            accionTexto: "Mis Documentos",
            modulo: "onboarding",
        },
        {
            icono: "🛣️",
            titulo: "Despacho y Seguimiento",
            descripcion: "Reporta el inicio de tránsito de la carga y confirma la entrega definitiva en destino.",
            accionTexto: "Mis Despachos",
            modulo: "seguimiento",
        },
    ],
    DADOR_CARGA: [
        {
            icono: "📦",
            titulo: "Registrar Contrato de Carga",
            descripcion: "Crea borradores de contratos especificando origen, destino, tipo de carga y tarifas máximas.",
            accionTexto: "Nuevo Contrato",
            modulo: "contratos",
        },
        {
            icono: "⚖️",
            titulo: "Gestión de Subastas y Adjudicación",
            descripcion: "Supervisa las postulaciones recibidas de los transportistas y adjudica la carga al mejor postor.",
            accionTexto: "Mis Subastas",
            modulo: "subastas",
        },
        {
            icono: "💼",
            titulo: "Perfil Tributario y Facturación",
            descripcion: "Administra el RUT empresarial, razón social y datos fiscales para la emisión de contratos.",
            accionTexto: "Datos Fiscales",
            modulo: "tributario",
        },
    ],
    ADMIN_BACKOFFICE: [
        {
            icono: "🛡️",
            titulo: "Aprobación y Compliance",
            descripcion: "Verifica antecedentes y aprueba o rechaza transportistas que se encuentran en estado En Revisión.",
            accionTexto: "Auditar Usuarios",
            modulo: "administracion_usuarios",
        },
        {
            icono: "⚙️",
            titulo: "Configuración Global del Motor",
            descripcion: "Ajusta las políticas operativas, límites de tarifas, márgenes de subasta y reglas de negocio.",
            accionTexto: "Configuraciones",
            modulo: "configuracion",
        },
        {
            icono: "📊",
            titulo: "Monitoreo y Trazabilidad",
            descripcion: "Supervisa el flujo completo de contratos, cambios de estado operativo y resolución de disputas.",
            accionTexto: "Ver Reportes",
            modulo: "auditoria",
        },
    ],
};

// =================================
// MENSAJES Y NOTIFICACIONES
// =================================

function mostrarMensajeLogin(texto, tipo = "") {
    if (!mensajeLogin) return;
    mensajeLogin.textContent = texto;
    mensajeLogin.className = "mensaje-login";
    if (tipo) {
        mensajeLogin.classList.add(tipo);
    }
}

// =================================
// RENDERIZADO DE FUNCIONALIDADES SEGÚN ROL (CA4)
// =================================

function normalizarRol(rolCrudo) {
    if (!rolCrudo) return "TRANSPORTISTA";
    const normalizado = String(rolCrudo).trim().toUpperCase();
    if (normalizado === "EMPRESA") return "DADOR_CARGA";
    if (normalizado === "INDEPENDIENTE") return "TRANSPORTISTA";
    return normalizado;
}

function renderizarFuncionalidades(datosUsuario) {
    if (!contenedorFuncionalidades || !seccionLogin || !seccionFuncionalidades) return;

    const rol = normalizarRol(datosUsuario.rol);
    const listaFuncionalidades = FUNCIONALIDADES_POR_ROL[rol] || FUNCIONALIDADES_POR_ROL.TRANSPORTISTA;

    // Actualizar encabezados
    if (usuarioSaludo) {
        usuarioSaludo.textContent = `Hola, ${datosUsuario.nombre || datosUsuario.usuario || "Usuario"}`;
    }
    if (usuarioRol) {
        usuarioRol.textContent = rol;
    }
    if (usuarioEmailInfo) {
        usuarioEmailInfo.textContent = `Correo: ${datosUsuario.email || datosUsuario.usuario || ""}`;
    }

    // Renderizar tarjetas autorizadas
    contenedorFuncionalidades.innerHTML = "";
    listaFuncionalidades.forEach((item) => {
        const tarjeta = document.createElement("article");
        tarjeta.className = "tarjeta-funcionalidad";
        tarjeta.innerHTML = `
            <div>
                <div class="func-icono">${item.icono}</div>
                <h4 class="func-titulo">${item.titulo}</h4>
                <p class="func-descripcion">${item.descripcion}</p>
            </div>
            <button class="func-boton" data-modulo="${item.modulo}">
                ${item.accionTexto} →
            </button>
        `;
        const botonAccion = tarjeta.querySelector(".func-boton");
        if (botonAccion) {
            botonAccion.addEventListener("click", () => {
                alert(`Accediendo a: ${item.titulo} (${item.modulo})`);
            });
        }
        contenedorFuncionalidades.appendChild(tarjeta);
    });

    // Cambiar vista
    seccionLogin.style.display = "none";
    seccionFuncionalidades.style.display = "block";
}

function restaurarVistaLogin() {
    if (seccionLogin && seccionFuncionalidades) {
        seccionLogin.style.display = "block";
        seccionFuncionalidades.style.display = "none";
    }
    if (emailInput) emailInput.value = "";
    if (passwordInput) passwordInput.value = "";
    mostrarMensajeLogin("");
}

// =================================
// EJECUCIÓN DEL LOGIN (CA1, CA2, CA3)
// =================================

async function ejecutarLogin() {
    const email = emailInput ? emailInput.value.trim() : "";
    const password = passwordInput ? passwordInput.value : "";

    mostrarMensajeLogin("");

    // CA3: Validación detallada de campos obligatorios
    if (!email && !password) {
        mostrarMensajeLogin("El correo electrónico y la contraseña son campos obligatorios.", "error");
        if (emailInput) emailInput.focus();
        return;
    }
    if (!email) {
        mostrarMensajeLogin("El correo electrónico es un campo obligatorio.", "error");
        if (emailInput) emailInput.focus();
        return;
    }
    if (!password) {
        mostrarMensajeLogin("La contraseña es un campo obligatorio.", "error");
        if (passwordInput) passwordInput.focus();
        return;
    }

    if (btnLogin) btnLogin.disabled = true;
    mostrarMensajeLogin("Verificando credenciales...");

    try {
        const respuesta = await fetch(`${API_BASE_URL}/auth/login`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                email: email,
                password: password,
            }),
        });

        const datos = await respuesta.json().catch(() => ({}));

        // CA2: Credenciales incorrectas (HTTP 401)
        if (!respuesta.ok) {
            let detalle = "Credenciales inválidas";
            if (typeof datos.detail === "string") {
                detalle = datos.detail;
            } else if (Array.isArray(datos.detail) && datos.detail.length > 0) {
                detalle = datos.detail.map((err) => err.msg || JSON.stringify(err)).join(" | ");
            }
            mostrarMensajeLogin(detalle, "error");
            return;
        }

        // CA1: Autenticación exitosa - guardar sesión con token Bearer
        localStorage.setItem("usuario_actual", JSON.stringify(datos));
        if (datos.access_token) {
            localStorage.setItem("access_token", datos.access_token);
        }
        if (datos.rol) {
            localStorage.setItem("usuario_rol", datos.rol);
        }

        mostrarMensajeLogin("Inicio de sesión exitoso. Cargando funcionalidades...", "success");

        // CA4: Mostrar únicamente las funcionalidades según el rol
        setTimeout(() => {
            renderizarFuncionalidades(datos);
        }, 350);

    } catch (error) {
        console.error("Error al conectar con el backend:", error);
        mostrarMensajeLogin(
            "No se pudo conectar con el servidor (http://127.0.0.1:8000). Verifica que el backend esté en ejecución.",
            "error"
        );
    } finally {
        if (btnLogin) btnLogin.disabled = false;
    }
}

// =================================
// EVENTOS Y NAVEGACIÓN
// =================================

if (btnLogin) {
    btnLogin.addEventListener("click", ejecutarLogin);
}

[emailInput, passwordInput].forEach((input) => {
    if (input) {
        input.addEventListener("keydown", (event) => {
            if (event.key === "Enter") {
                event.preventDefault();
                ejecutarLogin();
            }
        });
    }
});

if (btnCerrarSesion) {
    btnCerrarSesion.addEventListener("click", () => {
        localStorage.removeItem("usuario_actual");
        localStorage.removeItem("access_token");
        localStorage.removeItem("usuario_rol");
        restaurarVistaLogin();
    });
}

// Cargar sesión si ya existe en localStorage
document.addEventListener("DOMContentLoaded", () => {
    try {
        const sesionGuardada = localStorage.getItem("usuario_actual");
        if (sesionGuardada) {
            const datos = JSON.parse(sesionGuardada);
            if (datos && datos.access_token && datos.rol) {
                renderizarFuncionalidades(datos);
            }
        }
    } catch (e) {
        console.warn("No se pudo restaurar la sesión previa:", e);
    }
});

// Botones sociales
const btnGoogle = document.getElementById("btnGoogle");
if (btnGoogle) {
    btnGoogle.addEventListener("click", () => alert("Inicio de sesión con Google"));
}

const btnMicrosoft = document.getElementById("btnMicrosoft");
if (btnMicrosoft) {
    btnMicrosoft.addEventListener("click", () => alert("Inicio de sesión con Microsoft"));
}

const btnApple = document.getElementById("btnApple");
if (btnApple) {
    btnApple.addEventListener("click", () => alert("Inicio de sesión con Apple"));
}

// Recuperar contraseña
const recuperarContraseña = document.getElementById("recuperarContraseña");
if (recuperarContraseña) {
    recuperarContraseña.addEventListener("click", (event) => {
        event.preventDefault();
        alert("Aquí irá el sistema para recuperar la contraseña.");
    });
}

// Registro
const btnRegistro = document.getElementById("btnRegistro");
if (btnRegistro) {
    btnRegistro.addEventListener("click", (event) => {
        event.preventDefault();
        window.location.href = "../registrar/registro.html";
    });
}