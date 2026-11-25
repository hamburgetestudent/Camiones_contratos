// =============================================
// LOGIN — MansoViaje
// Redirige al panel según el rol entregado por el backend.
// =============================================
import { MVApi } from "../../compartido/js/api.js";
import { MVIconos } from "../../compartido/js/iconos.js";
import { MVSesion } from "../../compartido/js/sesion.js";

const API_BASE_URL = MVApi.baseUrl;

const loginForm = document.getElementById("loginForm");
const btnLogin = document.getElementById("btnLogin");
const emailInput = document.getElementById("email");
const passwordInput = document.getElementById("password");
const mensajeLogin = document.getElementById("mensajeLogin");
const togglePassword = document.getElementById("togglePassword");

function inicializarIconosLogin() {
  const logo = document.getElementById("logoMarca");
  if (logo) logo.replaceChildren(MVIconos.crear("isotipo", { size: 22 }));

  if (btnLogin) {
    btnLogin.append(MVIconos.crear("flechaDer", { size: 16 }));
  }

  if (togglePassword) {
    togglePassword.replaceChildren(MVIconos.crear("ojo", { size: 17 }));
  }

  document.querySelectorAll("[data-icono]").forEach((el) => {
    const nombre = el.getAttribute("data-icono");
    el.replaceChildren(MVIconos.crear(nombre, { size: 15 }));
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

    MVSesion.guardar(datos);

    mostrarMensajeLogin("Inicio de sesión exitoso. Abriendo tu panel...", "success");
    window.location.replace(MVSesion.RUTA_PANEL);
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
    if (MVIconos) {
      togglePassword.replaceChildren(MVIconos.crear(mostrar ? "ojoCerrado" : "ojo", { size: 17 }));
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

if (MVSesion.token()) {
  window.location.replace(MVSesion.RUTA_PANEL);
}
