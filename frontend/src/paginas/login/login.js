// =============================================
// LOGIN — MansoViaje
// Redirige al panel según el rol entregado por el backend.
// =============================================

const API_BASE_URL =
  window.API_BASE_URL ||
  (window.location.protocol.startsWith("http")
    ? window.location.origin
    : "http://127.0.0.1:8000");

const loginForm = document.getElementById("loginForm");
const btnLogin = document.getElementById("btnLogin");
const emailInput = document.getElementById("email");
const passwordInput = document.getElementById("password");
const mensajeLogin = document.getElementById("mensajeLogin");
const togglePassword = document.getElementById("togglePassword");

function inicializarIconosLogin() {
  if (!window.MVIconos) return;
  const logo = document.getElementById("logoMarca");
  if (logo) logo.replaceChildren(window.MVIconos.crear("isotipo", { size: 22 }));

  if (btnLogin) {
    btnLogin.append(window.MVIconos.crear("flechaDer", { size: 16 }));
  }

  if (togglePassword) {
    togglePassword.replaceChildren(window.MVIconos.crear("ojo", { size: 17 }));
  }

  document.querySelectorAll("[data-icono]").forEach((el) => {
    const nombre = el.getAttribute("data-icono");
    el.replaceChildren(window.MVIconos.crear(nombre, { size: 15 }));
  });
}

function mostrarMensajeLogin(texto, tipo = "") {
  if (!mensajeLogin) return;
  if (!texto) {
    mensajeLogin.textContent = "";
    mensajeLogin.className = "mensaje-login oculto";
    return;
  }
  mensajeLogin.textContent = texto;
  mensajeLogin.className = "mensaje-login" + (tipo ? " " + tipo : "");
}

function marcarErroresCampos(emailInvalido, passInvalido) {
  if (emailInput) emailInput.classList.toggle("campo-error", emailInvalido);
  if (passwordInput) passwordInput.classList.toggle("campo-error", passInvalido);
}

async function ejecutarLogin(evento) {
  if (evento) evento.preventDefault();
  if (!emailInput || !passwordInput || !btnLogin) return;

  const email = emailInput.value.trim();
  const password = passwordInput.value;
  mostrarMensajeLogin("");
  marcarErroresCampos(false, false);

  if (!email || !password) {
    marcarErroresCampos(!email, !password);
    mostrarMensajeLogin("Debes ingresar tu correo electrónico y contraseña.", "error");
    (!email ? emailInput : passwordInput).focus();
    return;
  }

  btnLogin.disabled = true;
  mostrarMensajeLogin("Verificando credenciales...", "info");

  try {
    const respuesta = await fetch(`${API_BASE_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });

    const datos = await respuesta.json().catch(() => ({}));

    if (!respuesta.ok) {
      const detalle =
        typeof datos.detail === "string" ? datos.detail : "Usuario o contraseña incorrectos.";
      mostrarMensajeLogin(detalle, "error");
      return;
    }

    if (!datos || typeof datos !== "object" || Array.isArray(datos)) {
      mostrarMensajeLogin("El servidor devolvió una respuesta no válida.", "error");
      return;
    }

    localStorage.setItem("usuario_actual", JSON.stringify(datos));
    localStorage.setItem("access_token", datos.access_token);
    localStorage.setItem("usuario_rol", datos.rol);

    mostrarMensajeLogin("Inicio de sesión exitoso. Abriendo tu panel...", "success");
    window.location.replace("../panel/panel.html");
  } catch (error) {
    console.error("Error al conectar con el backend:", error);
    mostrarMensajeLogin(
      `No se pudo conectar con el servidor (${API_BASE_URL}). Verifica que el backend esté en ejecución.`,
      "error"
    );
  } finally {
    btnLogin.disabled = false;
  }
}

if (loginForm) {
  loginForm.addEventListener("submit", ejecutarLogin);
}

[emailInput, passwordInput].filter(Boolean).forEach((campo) => {
  campo.addEventListener("input", () => {
    campo.classList.remove("campo-error");
  });
});

if (togglePassword && passwordInput) {
  togglePassword.addEventListener("click", () => {
    const mostrar = passwordInput.type === "password";
    passwordInput.type = mostrar ? "text" : "password";
    togglePassword.setAttribute("aria-pressed", String(mostrar));
    togglePassword.setAttribute(
      "aria-label",
      mostrar ? "Ocultar contraseña" : "Mostrar contraseña"
    );
    if (window.MVIconos) {
      togglePassword.replaceChildren(
        window.MVIconos.crear(mostrar ? "ojoCerrado" : "ojo", { size: 17 })
      );
    }
  });
}

const recuperarContraseña = document.getElementById("recuperarContraseña");
if (recuperarContraseña) {
  recuperarContraseña.addEventListener("click", (evento) => {
    evento.preventDefault();
    mostrarMensajeLogin(
      "La recuperación automática de contraseña aún no está habilitada. Contacta al administrador de MansoViaje.",
      "info"
    );
  });
}

inicializarIconosLogin();

if (localStorage.getItem("access_token")) {
  window.location.replace("../panel/panel.html");
}
