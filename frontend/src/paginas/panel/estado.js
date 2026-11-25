/* Estado compartido del panel (usuario de la sesión y control de navegación) — MansoViaje */
export const nombresRol = {
  ADMIN_BACKOFFICE: "Administrador",
  TRANSPORTISTA: "Transportista",
  DADOR_CARGA: "Dador de carga",
};

export const estadoPanel = {
  usuario: undefined,
  versionVista: 0,
  /** Lo registra panel.js; las vistas lo usan para recargar la ruta actual. */
  navegar: () => {},
};
