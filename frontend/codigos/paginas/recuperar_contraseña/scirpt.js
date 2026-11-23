// ==========================================
// CONFIGURACIÓN DE EMAILJS (Reemplaza con tus datos)
// ==========================================
const EMAILJS_PUBLIC_KEY = "TU_PUBLIC_KEY";
const EMAILJS_SERVICE_ID = "TU_SERVICE_ID";
const EMAILJS_TEMPLATE_ID = "TU_TEMPLATE_ID";

// Inicializar EmailJS
(function () {
    emailjs.init({ publicKey: EMAILJS_PUBLIC_KEY });
})();

// Referencias del DOM
const formCorreo = document.getElementById("form-correo");
const formCodigo = document.getElementById("form-codigo");
const formNuevaClave = document.getElementById("form-nueva-clave");
const mensajeEstado = document.getElementById("mensaje-estado");
const btnEnviarCodigo = document.getElementById("btn-enviar-codigo");
const btnReenviar = document.getElementById("btn-reenviar");
const correoMostrado = document.getElementById("correo-mostrado");

let correoActual = "";

// Función auxiliar para alertas visuales
function mostrarMensaje(texto, tipo) {
    mensajeEstado.textContent = texto;
    mensajeEstado.className = `mensaje ${tipo}`;
}

function ocultarMensaje() {
    mensajeEstado.className = "mensaje oculto";
}

// Generar código aleatorio de 6 dígitos
function generarCodigoOTP() {
    return Math.floor(100000 + Math.random() * 900000).toString();
}

// PASO 1: Verificar usuario y enviar correo
formCorreo.addEventListener("submit", async (e) => {
    e.preventDefault();
    ocultarMensaje();

    const correoInput = document.getElementById("correo").value.trim().toLowerCase();

    // Buscar usuarios almacenados en localStorage (ajustar la clave)
    const usuarios = JSON.parse(localStorage.getItem("usuarios")) || [];
    const usuarioExiste = usuarios.find(u => (u.correo || u.email)?.toLowerCase() === correoInput);

    if (!usuarioExiste) {
        mostrarMensaje("No existe ninguna cuenta asociada a este correo electrónico.", "error");
        return;
    }

    const codigoGenerado = generarCodigoOTP();
    const expiracion = Date.now() + 10 * 60 * 1000; // Válido por 10 minutos

    // Guardar token temporal en sessionStorage
    sessionStorage.setItem("recuperacion_data", JSON.stringify({
        correo: correoInput,
        codigo: codigoGenerado,
        expiracion: expiracion
    }));

    btnEnviarCodigo.disabled = true;
    btnEnviarCodigo.textContent = "Enviando correo...";

    try {
        await emailjs.send(EMAILJS_SERVICE_ID, EMAILJS_TEMPLATE_ID, {
            to_email: correoInput,
            codigo: codigoGenerado
        });

        correoActual = correoInput;
        correoMostrado.textContent = correoActual;

        formCorreo.classList.add("oculto");
        formCodigo.classList.remove("oculto");
        mostrarMensaje("Código enviado con éxito. Revisa tu correo.", "exito");
    } catch (error) {
        console.error("Error al enviar correo:", error);
        mostrarMensaje("Hubo un error al enviar el correo. Verifica tu configuración de EmailJS.", "error");
    } finally {
        btnEnviarCodigo.disabled = false;
        btnEnviarCodigo.textContent = "Enviar Código";
    }
});

// Botón para volver al paso 1
btnReenviar.addEventListener("click", () => {
    ocultarMensaje();
    formCodigo.classList.add("oculto");
    formCorreo.classList.remove("oculto");
});

// PASO 2: Validar el código ingresado
formCodigo.addEventListener("submit", (e) => {
    e.preventDefault();
    ocultarMensaje();

    const codigoIngresado = document.getElementById("codigo-verificacion").value.trim();
    const datosGuardados = JSON.parse(sessionStorage.getItem("recuperacion_data"));

    if (!datosGuardados || datosGuardados.correo !== correoActual) {
        mostrarMensaje("Sesión de recuperación inválida. Intenta nuevamente.", "error");
        return;
    }

    if (Date.now() > datosGuardados.expiracion) {
        sessionStorage.removeItem("recuperacion_data");
        mostrarMensaje("El código ha expirado. Solicita uno nuevo.", "error");
        formCodigo.classList.add("oculto");
        formCorreo.classList.remove("oculto");
        return;
    }

    if (codigoIngresado !== datosGuardados.codigo) {
        mostrarMensaje("El código ingresado es incorrecto.", "error");
        return;
    }

    // Código correcto -> Pasar al formulario de nueva contraseña
    formCodigo.classList.add("oculto");
    formNuevaClave.classList.remove("oculto");
    mostrarMensaje("Código verificado correctamente.", "exito");
});

// PASO 3: Actualizar contraseña en localStorage
formNuevaClave.addEventListener("submit", (e) => {
    e.preventDefault();
    ocultarMensaje();

    const nuevaClave = document.getElementById("nueva-password").value;
    const confirmarClave = document.getElementById("confirmar-password").value;

    if (nuevaClave !== confirmarClave) {
        mostrarMensaje("Las contraseñas no coinciden.", "error");
        return;
    }

    let usuarios = JSON.parse(localStorage.getItem("usuarios")) || [];
    const indice = usuarios.findIndex(u => (u.correo || u.email)?.toLowerCase() === correoActual);

    if (indice !== -1) {
        // Verificar
        if ("password" in usuarios[indice]) {
            usuarios[indice].password = nuevaClave;
        } else {
            usuarios[indice].contraseña = nuevaClave;
        }

        localStorage.setItem("usuarios", JSON.stringify(usuarios));
        sessionStorage.removeItem("recuperacion_data");

        mostrarMensaje("¡Contraseña actualizada! Redirigiendo al login...", "exito");
        formNuevaClave.querySelector("button").disabled = true;

        setTimeout(() => {
            window.location.href = "../Login/index.html";
        }, 2000);
    } else {
        mostrarMensaje("Error al actualizar el usuario.", "error");
    }
});