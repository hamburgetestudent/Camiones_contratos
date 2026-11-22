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
      window.location.replace("../panel/index.html");
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

// Cargar sesión si ya existe en localStorage
document.addEventListener("DOMContentLoaded", () => {
  try {
    const sesionGuardada = localStorage.getItem("usuario_actual");
    if (sesionGuardada) {
      const datos = JSON.parse(sesionGuardada);
      if (datos && datos.access_token && datos.rol) {
        window.location.replace("../panel/index.html");
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
