// =============================================
// PANEL DE FUNCIONES - versión 1.0
// Este panel organiza la navegación por rol.
// No reemplaza la autorización que debe realizar el backend.
// =============================================

const usuarioGuardado = localStorage.getItem("usuario_actual");
const saludoUsuario = document.getElementById("saludoUsuario");
const tituloRol = document.getElementById("tituloRol");
const descripcionRol = document.getElementById("descripcionRol");
const listaFunciones = document.getElementById("listaFunciones");
const mensajePanel = document.getElementById("mensajePanel");
const btnCerrarSesion = document.getElementById("btnCerrarSesion");

const funcionesPorRol = {
  TRANSPORTISTA: {
    nombre: "Transportista",
    descripcion:
      "Puedes encontrar oportunidades de transporte y revisar la actividad asociada a tu cuenta.",
    funciones: [
      {
        icono: "⌕",
        titulo: "Buscar contratos",
        descripcion: "Explora los contratos publicados y revisa sus detalles.",
        disponible: true,
        destino: "../catalogo-contratos/catalogo-contratos.html",
      },
      {
        icono: "▤",
        titulo: "Mis contratos",
        descripcion: "Consulta los contratos que has solicitado o aceptado.",
        disponible: false,
      },
      {
        icono: "♙",
        titulo: "Administrar perfil",
        descripcion: "Revisa y actualiza la información de tu cuenta.",
        disponible: false,
      },
    ],
  },
  DADOR_CARGA: {
    nombre: "Dador de carga",
    descripcion:
      "Puedes publicar necesidades de transporte y administrar los contratos de tu empresa o actividad.",
    funciones: [
      {
        icono: "+",
        titulo: "Crear contratos",
        descripcion: "Prepara una nueva publicación de transporte.",
        disponible: true,
        destino: "../catalogo-contratos/catalogo-contratos.html",
      },
      {
        icono: "▤",
        titulo: "Mis contratos",
        descripcion: "Consulta y administra los contratos que has publicado.",
        disponible: false,
      },
      {
        icono: "♙",
        titulo: "Administrar perfil",
        descripcion: "Revisa y actualiza la información de tu cuenta.",
        disponible: false,
      },
    ],
  },
  ADMIN_BACKOFFICE: {
    nombre: "Administrador Backoffice",
    descripcion:
      "Tu cuenta está destinada a la gestión y supervisión administrativa de la plataforma.",
    funciones: [
      {
        icono: "♙",
        titulo: "Gestionar usuarios",
        descripcion: "Revisa y administra las cuentas registradas.",
        disponible: false,
      },
      {
        icono: "▤",
        titulo: "Gestionar contratos",
        descripcion: "Supervisa los contratos de la plataforma.",
        disponible: false,
      },
      {
        icono: "▦",
        titulo: "Supervisar operaciones",
        descripcion: "Consulta la actividad y el estado de las operaciones.",
        disponible: false,
      },
    ],
  },
};

function obtenerUsuarioActual() {
  if (!usuarioGuardado) return null;

  try {
    const usuario = JSON.parse(usuarioGuardado);
    return usuario && typeof usuario === "object" && !Array.isArray(usuario) ? usuario : null;
  } catch {
    return null;
  }
}

function normalizarRol(usuario) {
  const rolRecibido = usuario.rol || usuario.tipo_usuario || usuario.tipoUsuario || "";
  const rol = String(rolRecibido).trim().toUpperCase();

  // Compatibilidad con el valor de selección usado en el formulario de registro.
  if (rol === "EMPRESA") return "DADOR_CARGA";
  if (rol === "INDEPENDIENTE") return "TRANSPORTISTA";
  return rol;
}

function crearTarjetaFuncion(funcion) {
  const tarjeta = document.createElement("button");
  tarjeta.type = "button";
  tarjeta.className = `tarjeta-funcion${funcion.disponible ? " disponible" : ""}`;
  tarjeta.disabled = !funcion.disponible;

  const icono = document.createElement("span");
  icono.className = "icono-funcion";
  icono.setAttribute("aria-hidden", "true");
  icono.textContent = funcion.icono;

  const titulo = document.createElement("strong");
  titulo.textContent = funcion.titulo;

  const descripcion = document.createElement("span");
  descripcion.textContent = funcion.descripcion;

  tarjeta.append(icono, titulo, descripcion);

  if (funcion.disponible && funcion.destino) {
    tarjeta.addEventListener("click", () => {
      window.location.href = funcion.destino;
    });
  } else {
    const estado = document.createElement("span");
    estado.className = "estado-proximamente";
    estado.textContent = "Disponible en una próxima etapa";
    tarjeta.appendChild(estado);
  }

  return tarjeta;
}

function mostrarPanel(usuario) {
  const rol = normalizarRol(usuario);
  const configuracion = funcionesPorRol[rol];

  if (!configuracion) {
    tituloRol.textContent = "Rol no reconocido";
    descripcionRol.textContent =
      "La respuesta del servidor no contiene un rol compatible con la aplicación.";
    mensajePanel.textContent =
      "Contacta al administrador o vuelve a iniciar sesión. No se habilitaron funciones.";
    return;
  }

  const nombre = usuario.nombre || usuario.usuario || usuario.email || "usuario";
  saludoUsuario.textContent = `Bienvenido/a, ${nombre}`;
  tituloRol.textContent = configuracion.nombre;
  descripcionRol.textContent = configuracion.descripcion;

  configuracion.funciones.forEach((funcion) => {
    listaFunciones.appendChild(crearTarjetaFuncion(funcion));
  });
}

function cerrarSesion() {
  // Se elimina la misma clave que se utiliza al guardar el inicio de sesión.
  localStorage.removeItem("usuario_actual");
  window.location.replace("../login/login.html");
}

function inicializarPanel() {
  if (!usuarioGuardado) {
    window.location.replace("../login/login.html");
    return;
  }

  const usuario = obtenerUsuarioActual();
  if (!usuario) {
    localStorage.removeItem("usuario_actual");
    window.location.replace("../login/login.html");
    return;
  }

  mostrarPanel(usuario);
  btnCerrarSesion.addEventListener("click", cerrarSesion);
}

document.addEventListener("DOMContentLoaded", inicializarPanel);
