const API_BASE_URL = window.API_BASE_URL || "http://127.0.0.1:8000";

const registroForm = document.getElementById("registroForm");
const empresaSection = document.getElementById("empresaSection");
const mensaje = document.getElementById("mensaje");
const btnSubmitRegistro = document.getElementById("btnSubmitRegistro");

const camposEmpresa = [
    document.getElementById("razon_social"),
    document.getElementById("rut_empresa"),
    document.getElementById("giro"),
    document.getElementById("cargo"),
    document.getElementById("direccion_empresa"),
].filter(Boolean);

function obtenerTipoUsuario() {
    const seleccionado = document.querySelector('input[name="tipo_usuario"]:checked');
    return seleccionado ? seleccionado.value : null;
}

function actualizarFormulario() {
    const tipo_usuario = obtenerTipoUsuario();
    const esEmpresa = tipo_usuario === "empresa";

    empresaSection.classList.toggle("hidden", !esEmpresa);
    camposEmpresa.forEach((campo) => {
        campo.required = esEmpresa;
    });
}

document.querySelectorAll('input[name="tipo_usuario"]').forEach((radio) => {
    radio.addEventListener("change", actualizarFormulario);
});

function extraerMensajeError(datos) {
    if (!datos) {
        return "No se pudo completar el registro.";
    }
    if (typeof datos.detail === "string") {
        return datos.detail;
    }
    if (Array.isArray(datos.detail) && datos.detail.length > 0) {
        return datos.detail
            .map((item) => item.msg || JSON.stringify(item))
            .join(" | ");
    }
    return "Datos inválidos al registrar el usuario.";
}

registroForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    mensaje.textContent = "";
    mensaje.className = "mensaje";

    const tipo_usuario = obtenerTipoUsuario();
    const esEmpresa = tipo_usuario === "empresa";
    const password = document.getElementById("password").value;
    const confirmPassword = document.getElementById("confirm_password").value;

    if (!registroForm.checkValidity()) {
        mensaje.textContent = "Completa todos los campos obligatorios.";
        mensaje.classList.add("error");
        registroForm.reportValidity();
        return;
    }

    if (password !== confirmPassword) {
        mensaje.textContent = "Las contraseñas no coinciden.";
        mensaje.classList.add("error");
        return;
    }

    const nombre = document.getElementById("nombre").value.trim();
    const apellido = document.getElementById("apellido").value.trim();
    const email = document.getElementById("email").value.trim();
    const razonSocialEl = document.getElementById("razon_social");
    const razonSocial = razonSocialEl ? razonSocialEl.value.trim() : "";
    const rutEmpresa = document.getElementById("rut_empresa").value.trim();
    const direccionEmpresa = document.getElementById("direccion_empresa").value.trim();

    const nombreCompleto = `${nombre} ${apellido}`.trim();
    const rol = esEmpresa ? "DADOR_CARGA" : "TRANSPORTISTA";

    const payload = {
        nombre: nombreCompleto,
        email: email,
        rol: rol,
        password: password,
    };

    if (esEmpresa) {
        payload.perfil_tributario = {
            rut_id_empresa: rutEmpresa,
            datos_facturacion: {
                razon_social: razonSocial || nombreCompleto,
                direccion: direccionEmpresa,
                correo_facturacion: email,
            },
        };
    }

    if (btnSubmitRegistro) {
        btnSubmitRegistro.disabled = true;
    }
    mensaje.textContent = "Registrando usuario...";

    try {
        const respuesta = await fetch(`${API_BASE_URL}/auth/registro`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(payload),
        });

        const datos = await respuesta.json().catch(() => ({}));

        if (!respuesta.ok) {
            mensaje.textContent = extraerMensajeError(datos);
            mensaje.classList.add("error");
            return;
        }

        mensaje.textContent = `Cuenta creada exitosamente para ${datos.nombre || nombreCompleto}. Redirigiendo al inicio de sesión...`;
        mensaje.classList.add("success");

        setTimeout(() => {
            window.location.href = "../Login/index.html";
        }, 1500);
    } catch (error) {
        console.error("Error al conectar con el backend:", error);
        mensaje.textContent =
            "No se pudo conectar con el servidor (http://127.0.0.1:8000). Verifica que el backend esté en ejecución.";
        mensaje.classList.add("error");
    } finally {
        if (btnSubmitRegistro) {
            btnSubmitRegistro.disabled = false;
        }
    }
});

actualizarFormulario();