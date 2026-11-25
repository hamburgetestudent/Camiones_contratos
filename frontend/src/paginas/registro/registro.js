const API_BASE_URL =
  window.API_BASE_URL ||
  (window.location.protocol.startsWith("http")
    ? window.location.origin
    : "http://127.0.0.1:8000");

const registroForm = document.getElementById("registroForm");
const empresaSection = document.getElementById("empresaSection");
const mensaje = document.getElementById("mensaje");
const btnSubmitRegistro = document.getElementById("btnSubmitRegistro");
const barraFortaleza = document.getElementById("barraFortaleza");
const textoFortaleza = document.getElementById("textoFortaleza");

const camposEmpresaIds = ["razon_social", "rut_empresa", "direccion_empresa"];

function inicializarIconosRegistro() {
  if (!window.MVIconos) return;
  const logo = document.getElementById("logoRegistro");
  if (logo) logo.replaceChildren(window.MVIconos.crear("isotipo", { size: 20 }));

  document.querySelectorAll("[data-icono]").forEach((el) => {
    el.replaceChildren(window.MVIconos.crear(el.getAttribute("data-icono"), { size: 18 }));
  });

  document.querySelectorAll("[data-toggle-target]").forEach((btn) => {
    btn.replaceChildren(window.MVIconos.crear("ojo", { size: 17 }));
    btn.addEventListener("click", () => {
      const target = document.getElementById(btn.getAttribute("data-toggle-target"));
      if (!target) return;
      const mostrar = target.type === "password";
      target.type = mostrar ? "text" : "password";
      btn.setAttribute("aria-pressed", String(mostrar));
      btn.replaceChildren(window.MVIconos.crear(mostrar ? "ojoCerrado" : "ojo", { size: 17 }));
    });
  });
}

function obtenerRolSeleccionado() {
  const seleccionado = document.querySelector('input[name="rol_usuario"]:checked');
  return seleccionado ? seleccionado.value : "TRANSPORTISTA";
}

function mostrarMensajeGeneral(texto, tipo = "") {
  if (!texto) {
    mensaje.textContent = "";
    mensaje.className = "mensaje oculto";
    return;
  }
  mensaje.textContent = texto;
  mensaje.className = "mensaje" + (tipo ? " " + tipo : "");
}

function establecerErrorCampo(id, texto) {
  const input = document.getElementById(id);
  const errorEl = document.getElementById("error-" + id);
  if (input && input.type !== "checkbox") {
    input.classList.toggle("campo-error", Boolean(texto));
  }
  if (errorEl) {
    errorEl.textContent = texto || "";
    errorEl.classList.toggle("oculto", !texto);
  }
}

function limpiarErrores() {
  [
    "nombre",
    "apellido",
    "email",
    "razon_social",
    "rut_empresa",
    "correo_facturacion",
    "direccion_empresa",
    "password",
    "confirm_password",
    "aceptaTerminos",
  ].forEach((id) => establecerErrorCampo(id, ""));
}

function actualizarFormulario() {
  const esDador = obtenerRolSeleccionado() === "DADOR_CARGA";
  empresaSection.classList.toggle("oculto", !esDador);
  camposEmpresaIds.forEach((id) => {
    const campo = document.getElementById(id);
    if (campo) campo.required = esDador;
    if (!esDador) establecerErrorCampo(id, "");
  });
  if (!esDador) establecerErrorCampo("correo_facturacion", "");
}

function evaluarFortaleza(valor) {
  if (!barraFortaleza || !textoFortaleza) return;
  if (!valor) {
    barraFortaleza.style.width = "0";
    textoFortaleza.textContent = "Mínimo 8 caracteres.";
    return;
  }
  let puntaje = 0;
  if (valor.length >= 8) puntaje += 1;
  if (/[A-Z]/.test(valor) && /[a-z]/.test(valor)) puntaje += 1;
  if (/\d/.test(valor)) puntaje += 1;
  if (/[^A-Za-z0-9]/.test(valor) || valor.length >= 12) puntaje += 1;

  const niveles = [
    { ancho: "25%", color: "#b91c1c", texto: "Débil (mínimo 8 caracteres)" },
    { ancho: "50%", color: "#b45309", texto: "Media" },
    { ancho: "75%", color: "#1d4ed8", texto: "Buena" },
    { ancho: "100%", color: "#15803d", texto: "Segura" },
  ];
  const nivel = niveles[Math.max(0, Math.min(puntaje - 1, niveles.length - 1))];
  barraFortaleza.style.width = nivel.ancho;
  barraFortaleza.style.background = nivel.color;
  textoFortaleza.textContent = "Seguridad: " + nivel.texto;
}

function extraerMensajeError(datos) {
  if (!datos) return "No se pudo completar el registro.";
  if (typeof datos.detail === "string") return datos.detail;
  if (Array.isArray(datos.detail) && datos.detail.length > 0) {
    return datos.detail.map((item) => item.msg || JSON.stringify(item)).join(" | ");
  }
  return "Datos inválidos al registrar el usuario.";
}

function validarFormulario() {
  limpiarErrores();
  const rol = obtenerRolSeleccionado();
  const esDador = rol === "DADOR_CARGA";
  const regexEmail = /^[\w.-]+@[\w.-]+\.\w+$/;
  let primerInvalido = null;

  const fallar = (id, msg) => {
    establecerErrorCampo(id, msg);
    if (!primerInvalido) primerInvalido = document.getElementById(id);
  };

  const nombre = document.getElementById("nombre").value.trim();
  const apellido = document.getElementById("apellido").value.trim();
  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value;
  const confirmPassword = document.getElementById("confirm_password").value;
  const acepta = document.getElementById("aceptaTerminos").checked;

  if (nombre.length < 2) fallar("nombre", "Ingresa tu nombre (mínimo 2 caracteres).");
  if (apellido.length < 1) fallar("apellido", "Ingresa tu apellido.");
  if (!regexEmail.test(email)) fallar("email", "Ingresa un correo electrónico válido.");

  if (esDador) {
    const razonSocial = document.getElementById("razon_social").value.trim();
    const rutEmpresa = document.getElementById("rut_empresa").value.trim();
    const direccion = document.getElementById("direccion_empresa").value.trim();
    const correoFact = document.getElementById("correo_facturacion").value.trim();

    if (razonSocial.length < 2) fallar("razon_social", "Ingresa la razón social de la empresa.");
    if (rutEmpresa.length < 7) fallar("rut_empresa", "Ingresa un RUT empresarial válido.");
    if (direccion.length < 4) fallar("direccion_empresa", "Ingresa la dirección tributaria.");
    if (correoFact && !regexEmail.test(correoFact)) {
      fallar("correo_facturacion", "Ingresa un correo de facturación válido o déjalo vacío.");
    }
  }

  if (password.length < 8) {
    fallar("password", "La contraseña debe tener al menos 8 caracteres.");
  }
  if (!confirmPassword) {
    fallar("confirm_password", "Confirma tu contraseña.");
  } else if (password !== confirmPassword) {
    fallar("confirm_password", "Las contraseñas no coinciden.");
  }
  if (!acepta) {
    fallar("aceptaTerminos", "Debes aceptar los términos de uso para continuar.");
  }

  return primerInvalido;
}

document.querySelectorAll('input[name="rol_usuario"]').forEach((radio) => {
  radio.addEventListener("change", actualizarFormulario);
});

registroForm.querySelectorAll("input").forEach((input) => {
  input.addEventListener("input", () => {
    establecerErrorCampo(input.id, "");
    if (input.id === "password") evaluarFortaleza(input.value);
  });
  if (input.type === "checkbox") {
    input.addEventListener("change", () => establecerErrorCampo(input.id, ""));
  }
});

registroForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  mostrarMensajeGeneral("");

  const primerInvalido = validarFormulario();
  if (primerInvalido) {
    mostrarMensajeGeneral("Revisa los campos marcados antes de crear tu cuenta.", "error");
    primerInvalido.focus();
    return;
  }

  const rol = obtenerRolSeleccionado();
  const esDador = rol === "DADOR_CARGA";
  const nombre = document.getElementById("nombre").value.trim();
  const apellido = document.getElementById("apellido").value.trim();
  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value;
  const nombreCompleto = `${nombre} ${apellido}`.trim();

  const payload = {
    nombre: nombreCompleto,
    email,
    rol,
    password,
  };

  if (esDador) {
    const razonSocial = document.getElementById("razon_social").value.trim();
    const rutEmpresa = document.getElementById("rut_empresa").value.trim();
    const direccionEmpresa = document.getElementById("direccion_empresa").value.trim();
    const correoFact = document.getElementById("correo_facturacion").value.trim();

    payload.perfil_tributario = {
      rut_id_empresa: rutEmpresa,
      datos_facturacion: {
        razon_social: razonSocial || nombreCompleto,
        direccion: direccionEmpresa,
        correo_facturacion: correoFact || email,
      },
    };
  }

  if (btnSubmitRegistro) btnSubmitRegistro.disabled = true;
  mostrarMensajeGeneral("Creando tu cuenta en MansoViaje...", "info");

  try {
    const respuesta = await fetch(`${API_BASE_URL}/auth/registro`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const datos = await respuesta.json().catch(() => ({}));

    if (!respuesta.ok) {
      mostrarMensajeGeneral(extraerMensajeError(datos), "error");
      return;
    }

    mostrarMensajeGeneral(
      `Cuenta creada exitosamente para ${datos.nombre || nombreCompleto}. Redirigiendo al inicio de sesión...`,
      "success"
    );

    setTimeout(() => {
      window.location.href = "../login/login.html";
    }, 1500);
  } catch (error) {
    console.error("Error al conectar con el backend:", error);
    mostrarMensajeGeneral(
      `No se pudo conectar con el servidor (${API_BASE_URL}). Verifica que el backend esté en ejecución.`,
      "error"
    );
  } finally {
    if (btnSubmitRegistro) btnSubmitRegistro.disabled = false;
  }
});

inicializarIconosRegistro();
actualizarFormulario();
