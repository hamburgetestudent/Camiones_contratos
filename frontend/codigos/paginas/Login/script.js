// =============================================
// LOGIN — MansoViaje
// Redirige al panel según el rol entregado por el backend.
// =============================================

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
    const { respuesta, datos } = await window.MVApi.solicitarPublica("/auth/login", {
      method: "POST",
      body: { email, password },
    });

    if (!respuesta.ok) {
      const detalle = window.MVApi.extraerMensajeError(datos, "Usuario o contraseña incorrectos.");
      mostrarMensajeLogin(detalle, "error");
      return;
    }

    if (!datos || typeof datos !== "object" || Array.isArray(datos)) {
      mostrarMensajeLogin("El servidor devolvió una respuesta no válida.", "error");
      return;
    }

    window.MVApi.guardarSesion(datos);

    mostrarMensajeLogin("Inicio de sesión exitoso. Abriendo tu panel...", "success");
    window.location.replace("../panel/index.html");
  } catch (error) {
    console.error("Error al conectar con el backend:", error);
    mostrarMensajeLogin(
      `No se pudo conectar con el servidor (${window.MVApi.obtenerBaseUrl()}). Verifica que el backend esté en ejecución.`,
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

if (window.MVApi.obtenerToken()) {
  window.location.replace("../panel/index.html");
}
