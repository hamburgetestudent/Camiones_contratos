/* Cliente HTTP y gestión de sesión compartidos entre vistas — MansoViaje */
(function () {
  const CLAVES_SESION = ["usuario_actual", "access_token", "usuario_rol", "sesion_usuario"];

  function obtenerBaseUrl() {
    return (
      window.API_BASE_URL ||
      (window.location.protocol.startsWith("http")
        ? window.location.origin
        : "http://127.0.0.1:8000")
    );
  }

  function obtenerToken() {
    return localStorage.getItem("access_token");
  }

  function guardarSesion(datos) {
    localStorage.setItem("usuario_actual", JSON.stringify(datos));
    localStorage.setItem("access_token", datos.access_token);
    localStorage.setItem("usuario_rol", datos.rol);
  }

  function limpiarSesion() {
    for (const clave of CLAVES_SESION) {
      localStorage.removeItem(clave);
    }
  }

  function volverALogin(ruta = "../Login/index.html") {
    limpiarSesion();
    window.location.replace(ruta);
  }

  function extraerMensajeError(cuerpo, respaldo = "No se pudo completar la solicitud.") {
    if (!cuerpo || typeof cuerpo !== "object") return respaldo;
    if (typeof cuerpo.detail === "string") return cuerpo.detail;
    if (Array.isArray(cuerpo.detail) && cuerpo.detail.length > 0) {
      return cuerpo.detail.map((item) => item.msg || JSON.stringify(item)).join(" | ");
    }
    return respaldo;
  }

  async function solicitarPublica(ruta, opciones = {}) {
    const headers = { ...(opciones.headers || {}) };
    const config = {
      method: opciones.method || "GET",
      headers,
    };
    if (opciones.body !== undefined) {
      config.body =
        typeof opciones.body === "string" ? opciones.body : JSON.stringify(opciones.body);
      if (!headers["Content-Type"]) {
        headers["Content-Type"] = "application/json";
      }
    }
    const respuesta = await fetch(obtenerBaseUrl() + ruta, config);
    const datos = await respuesta.json().catch(() => ({}));
    return { respuesta, datos };
  }

  async function solicitar(ruta, opciones = {}) {
    const token = obtenerToken();
    if (!token) {
      volverALogin();
      throw new Error(opciones.mensajeSinSesion || "Debes iniciar sesión.");
    }

    const headers = {
      Authorization: "Bearer " + token,
      ...(opciones.headers || {}),
    };
    const config = {
      method: opciones.method || "GET",
      headers,
      cache: opciones.cache || "no-store",
    };
    if (opciones.body !== undefined) {
      config.body =
        typeof opciones.body === "string" ? opciones.body : JSON.stringify(opciones.body);
      if (!headers["Content-Type"]) {
        headers["Content-Type"] = "application/json";
      }
    }

    const respuesta = await fetch(obtenerBaseUrl() + ruta, config);
    if (respuesta.status === 401) {
      volverALogin();
      throw new Error(opciones.mensajeExpirada || "Sesión expirada.");
    }
    if (!respuesta.ok) {
      const cuerpo = await respuesta.json().catch(() => ({}));
      throw new Error(
        extraerMensajeError(cuerpo, opciones.mensajeError || "No se pudo completar la solicitud.")
      );
    }
    return respuesta.status === 204 ? null : respuesta.json();
  }

  async function cerrarSesionEnServidor() {
    return fetch(obtenerBaseUrl() + "/auth/logout", {
      method: "POST",
      headers: { Authorization: "Bearer " + (obtenerToken() || "") },
    });
  }

  window.MVApi = {
    CLAVES_SESION,
    obtenerBaseUrl,
    obtenerToken,
    guardarSesion,
    limpiarSesion,
    volverALogin,
    extraerMensajeError,
    solicitarPublica,
    solicitar,
    cerrarSesionEnServidor,
  };
})();
