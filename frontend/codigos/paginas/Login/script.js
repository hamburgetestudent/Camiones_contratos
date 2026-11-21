// =============================================
// LOGIN - versión 1.1
// Redirige al panel según el rol entregado por el backend.
// =============================================

const API_BASE_URL = window.API_BASE_URL || "http://127.0.0.1:8000";

const btnLogin = document.getElementById("btnLogin");
const emailInput = document.getElementById("email");
const passwordInput = document.getElementById("password");
const mensajeLogin = document.getElementById("mensajeLogin");

function mostrarMensajeLogin(texto, tipo = "") {
    if (!mensajeLogin) return;

    mensajeLogin.textContent = texto;
    mensajeLogin.className = "mensaje-login";
    if (tipo) mensajeLogin.classList.add(tipo);
}

async function ejecutarLogin() {
    if (!emailInput || !passwordInput || !btnLogin) return;

    const email = emailInput.value.trim();
    const password = passwordInput.value;
    mostrarMensajeLogin("");

    if (!email || !password) {
        mostrarMensajeLogin("Debes ingresar tu email y contraseña.", "error");
        return;
    }

    btnLogin.disabled = true;
    mostrarMensajeLogin("Verificando credenciales...");

    try {
        const respuesta = await fetch(`${API_BASE_URL}/auth/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            // Se conserva la estructura que utiliza el backend actual.
            body: JSON.stringify({ usuario: email, password })
        });

        const datos = await respuesta.json().catch(() => ({}));

        if (!respuesta.ok) {
            const detalle = typeof datos.detail === "string"
                ? datos.detail
                : "Usuario o contraseña incorrectos.";
            mostrarMensajeLogin(detalle, "error");
            return;
        }

        if (!datos || typeof datos !== "object" || Array.isArray(datos)) {
            mostrarMensajeLogin("El servidor devolvió una respuesta no válida.", "error");
            return;
        }

        // Se conserva la respuesta para que el panel pueda mostrar los datos.
        // La autorización real debe validarse siempre en el backend.
        localStorage.setItem("usuario_actual", JSON.stringify(datos));

        mostrarMensajeLogin("Inicio de sesión exitoso. Abriendo tu panel...", "success");
        window.location.replace("../panel_funciones/panel_funciones.html");
    } catch (error) {
        console.error("Error al conectar con el backend:", error);
        mostrarMensajeLogin(
            "No se pudo conectar con el servidor (http://127.0.0.1:8000). Verifica que el backend esté en ejecución.",
            "error"
        );
    } finally {
        btnLogin.disabled = false;
    }
}

if (btnLogin) btnLogin.addEventListener("click", ejecutarLogin);

[emailInput, passwordInput].filter(Boolean).forEach((campo) => {
    campo.addEventListener("keydown", (evento) => {
        if (evento.key === "Enter") {
            evento.preventDefault();
            ejecutarLogin();
        }
    });
});

// Los proveedores sociales siguen siendo informativos: aún no existe OAuth.
const btnGoogle = document.getElementById("btnGoogle");
if (btnGoogle) btnGoogle.addEventListener("click", () => alert("El inicio con Google todavía no está conectado."));

const btnMicrosoft = document.getElementById("btnMicrosoft");
if (btnMicrosoft) btnMicrosoft.addEventListener("click", () => alert("El inicio con Microsoft todavía no está conectado."));

const btnApple = document.getElementById("btnApple");
if (btnApple) btnApple.addEventListener("click", () => alert("El inicio con Apple todavía no está conectado."));

const recuperarContraseña = document.getElementById("recuperarContraseña");
if (recuperarContraseña) {
    recuperarContraseña.addEventListener("click", (evento) => {
        evento.preventDefault();
        alert("El sistema para recuperar la contraseña todavía no está conectado.");
    });
}

const btnRegistro = document.getElementById("btnRegistro");
if (btnRegistro) {
    btnRegistro.addEventListener("click", (evento) => {
        evento.preventDefault();
        window.location.href = "../Registrar_nuevoUsuario/registro.html";
    });
}
