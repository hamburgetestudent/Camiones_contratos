const registroForm = document.getElementById("registroForm");
const empresaSection = document.getElementById("empresaSection");
const mensaje = document.getElementById("mensaje");

const camposEmpresa = [
    document.getElementById("razon_social"),
    document.getElementById("rut_empresa"),
    document.getElementById("giro"),
    document.getElementById("cargo"),
    document.getElementById("direccion_empresa")
];

function obtenerTipoUsuario() {
    const seleccionado = document.querySelector('input[name="tipo_usuario"]:checked');
    return seleccionado ? seleccionado.value : null;
}

function actualizarFormulario() {
    const tipo_usuario = obtenerTipoUsuario();
    const esEmpresa = tipo_usuario === "empresa";

    empresaSection.classList.toggle("hidden", !esEmpresa);
    camposEmpresa.forEach(campo => campo.required = esEmpresa);

    console.log("tipo_usuario:", tipo_usuario);
}

document.querySelectorAll('input[name="tipo_usuario"]').forEach(radio => {
    radio.addEventListener("change", actualizarFormulario);
});

registroForm.addEventListener("submit", event => {
    event.preventDefault();
    mensaje.textContent = "";
    mensaje.className = "mensaje";

    const tipo_usuario = obtenerTipoUsuario();
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

    const datosUsuario = {
        tipo_usuario,
        nombre: document.getElementById("nombre").value.trim(),
        apellido: document.getElementById("apellido").value.trim(),
        rut_persona: document.getElementById("rut_persona").value.trim(),
        telefono: document.getElementById("telefono").value.trim(),
        email: document.getElementById("email").value.trim(),
        razon_social: document.getElementById("razon_social").value.trim(),
        rut_empresa: document.getElementById("rut_empresa").value.trim(),
        giro: document.getElementById("giro").value.trim(),
        cargo: document.getElementById("cargo").value.trim(),
        direccion_empresa: document.getElementById("direccion_empresa").value.trim()
    };

    console.log("Datos del usuario:", datosUsuario);
    mensaje.textContent = `Formulario válido. Tipo de usuario: ${tipo_usuario}.`;
    mensaje.classList.add("success");
});

actualizarFormulario();
