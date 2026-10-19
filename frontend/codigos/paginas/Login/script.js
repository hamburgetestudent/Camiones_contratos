// =================================
// CONFIGURACIÓN DE API BACKEND
// =================================

const API_BASE_URL = window.API_BASE_URL || "http://127.0.0.1:8000";

// =================================
// BOTÓN DE INICIO DE SESIÓN
// =================================

const btnLogin = document.getElementById("btnLogin");
const emailInput = document.getElementById("email");
const passwordInput = document.getElementById("password");
const mensajeLogin = document.getElementById("mensajeLogin");

function mostrarMensajeLogin(texto, tipo = "") {
    if (!mensajeLogin) return;
    mensajeLogin.textContent = texto;
    mensajeLogin.className = "mensaje-login";
    if (tipo) {
        mensajeLogin.classList.add(tipo);
    }
}

async function ejecutarLogin() {
    const email = emailInput.value.trim();
    const password = passwordInput.value;

    mostrarMensajeLogin("");

    // Comprobamos que los campos no estén vacíos
    if (email === "" || password === "") {
        mostrarMensajeLogin("Debes ingresar tu email y contraseña.", "error");
        return;
    }

    btnLogin.disabled = true;
    mostrarMensajeLogin("Verificando credenciales...");

    try {
        const respuesta = await fetch(`${API_BASE_URL}/auth/login`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                usuario: email,
                password: password,
            }),
        });

        const datos = await respuesta.json().catch(() => ({}));

        if (!respuesta.ok) {
            const detalle =
                typeof datos.detail === "string"
                    ? datos.detail
                    : "Usuario o contraseña incorrectos.";
            mostrarMensajeLogin(detalle, "error");
            return;
        }

        // Guardamos la sesión del usuario autenticado
        localStorage.setItem("usuario_actual", JSON.stringify(datos));

        const nombreMostrar = datos.nombre || datos.usuario || email;
        const rolMostrar = datos.rol ? ` (${datos.rol})` : "";
        mostrarMensajeLogin(
            `${datos.mensaje || "Inicio de sesión exitoso"}: ${nombreMostrar}${rolMostrar}`,
            "success"
        );
        
        window.location.href = "../Registrar_nuevoUsuario/registro.html";

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

btnLogin.addEventListener("click", ejecutarLogin);

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



// INICIO GOOGLE
// =================================

const btnGoogle = document.getElementById("btnGoogle");

btnGoogle.addEventListener("click", () => {

    alert("Inicio de sesión con Google");

});


// INICIO MICROSOFT
// =================================

const btnMicrosoft = document.getElementById("btnMicrosoft");

btnMicrosoft.addEventListener("click", () => {

    alert("Inicio de sesión con Microsoft");

});



// INICIO APPLE
// =================================

const btnApple = document.getElementById("btnApple");

btnApple.addEventListener("click", () => {

    alert("Inicio de sesión con Apple");

});



// RECUPERAR CONTRASEÑA
// ================================

const recuperarContraseña =
    document.getElementById("recuperarContraseña");

recuperarContraseña.addEventListener("click", (event) => {

    event.preventDefault();

    alert("Aquí irá el sistema para recuperar la contraseña.");

});



// REGISTRO NUEVO USUARIO
// =================================

const btnRegistro = document.getElementById("btnRegistro");

btnRegistro.addEventListener("click", (event) => {

    event.preventDefault();

    window.location.href = "../Registrar_nuevoUsuario/registro.html";

});