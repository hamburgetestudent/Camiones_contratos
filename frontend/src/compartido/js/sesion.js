/* Sesión del usuario en el navegador (localStorage) — MansoViaje */
const CLAVES = ["usuario_actual", "access_token", "usuario_rol", "sesion_usuario"];
const RUTA_LOGIN = "../login/login.html";
const RUTA_PANEL = "../panel/panel.html";

function token() {
  return localStorage.getItem("access_token");
}

function guardar(datos) {
  localStorage.setItem("usuario_actual", JSON.stringify(datos));
  localStorage.setItem("access_token", datos.access_token);
  localStorage.setItem("usuario_rol", datos.rol);
}

function limpiar() {
  for (const clave of CLAVES) localStorage.removeItem(clave);
}

function volverLogin() {
  limpiar();
  window.location.replace(RUTA_LOGIN);
}

export const MVSesion = { RUTA_LOGIN, RUTA_PANEL, token, guardar, limpiar, volverLogin };
