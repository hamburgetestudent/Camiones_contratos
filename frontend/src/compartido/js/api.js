/* Cliente HTTP de la API de FastAPI — MansoViaje. Requiere sesion.js cargado antes. */
(function () {
  const baseUrl =
    window.API_BASE_URL ||
    (window.location.protocol.startsWith("http")
      ? window.location.origin
      : "http://127.0.0.1:8000");

  function extraerMensajeError(cuerpo, porDefecto = "No se pudo completar la solicitud.") {
    if (!cuerpo || typeof cuerpo !== "object") return porDefecto;
    if (typeof cuerpo.detail === "string") return cuerpo.detail;
    if (Array.isArray(cuerpo.detail) && cuerpo.detail.length > 0) {
      return cuerpo.detail.map((item) => item.msg || JSON.stringify(item)).join(" | ");
    }
    return porDefecto;
  }

  /**
   * Llama a un endpoint autenticado. Devuelve el JSON (o null en 204).
   * Ante 401 o falta de token limpia la sesión y vuelve al login.
   * `textos` permite personalizar sinSesion, expirada y error.
   */
  async function solicitar(ruta, opciones = {}, textos = {}) {
    const token = window.MVSesion.token();
    if (!token) {
      window.MVSesion.volverLogin();
      throw new Error(textos.sinSesion || "Debes iniciar sesión.");
    }
    const respuesta = await fetch(baseUrl + ruta, {
      cache: "no-store",
      ...opciones,
      headers: {
        Authorization: "Bearer " + token,
        ...(opciones.body ? { "Content-Type": "application/json" } : {}),
        ...(opciones.headers || {}),
      },
    });
    if (respuesta.status === 401) {
      window.MVSesion.volverLogin();
      throw new Error(textos.expirada || "Tu sesión ha expirado.");
    }
    const cuerpo = respuesta.status === 204 ? null : await respuesta.json().catch(() => ({}));
    if (!respuesta.ok) throw new Error(extraerMensajeError(cuerpo, textos.error));
    return cuerpo;
  }

  /** Cierra la sesión en el servidor y vuelve al login; falla si el servidor no responde bien. */
  async function cerrarSesion() {
    const respuesta = await fetch(baseUrl + "/auth/logout", {
      method: "POST",
      headers: { Authorization: "Bearer " + window.MVSesion.token() },
    });
    if (!respuesta.ok && respuesta.status !== 401) throw new Error("No se pudo cerrar la sesión.");
    window.MVSesion.volverLogin();
  }

  window.MVApi = { baseUrl, extraerMensajeError, solicitar, cerrarSesion };
})();
