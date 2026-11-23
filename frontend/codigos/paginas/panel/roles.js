const FUNCIONALIDADES_POR_ROL = {
  TRANSPORTISTA: [
    {
      icono: "🚛",
      titulo: "Subastas y Cargas Disponibles",
      descripcion:
        "Explora las cargas publicadas en la plataforma y envía tus postulaciones con ofertas de flete.",
      accionTexto: "Ver Subastas",
      modulo: "subastas",
    },
    {
      icono: "📄",
      titulo: "Documentación y Compliance",
      descripcion:
        "Revisa el estado de verificación de tu licencia, padrón vehicular, revisión técnica, seguro y antecedentes.",
      accionTexto: "Mis Documentos",
      modulo: "onboarding",
    },
    {
      icono: "🛣️",
      titulo: "Despacho y Seguimiento",
      descripcion:
        "Reporta el inicio de tránsito de tus contratos adjudicados y confirma la entrega definitiva en destino.",
      accionTexto: "Mis Despachos",
      modulo: "seguimiento",
    },
  ],
  DADOR_CARGA: [
    {
      icono: "📦",
      titulo: "Registrar Contrato de Carga",
      descripcion:
        "Crea y administra tus contratos de transporte, controla su publicación y gestiona su ciclo de vida.",
      accionTexto: "Mis Contratos",
      modulo: "contratos",
    },
    {
      icono: "⚖️",
      titulo: "Gestión de Subastas y Adjudicación",
      descripcion:
        "Supervisa las postulaciones recibidas de los transportistas y adjudica la carga al mejor postor.",
      accionTexto: "Mis Subastas",
      modulo: "subastas",
    },
    {
      icono: "💼",
      titulo: "Perfil Tributario y Facturación",
      descripcion:
        "Administra el RUT empresarial, razón social y datos fiscales requeridos para emitir contratos.",
      accionTexto: "Datos Fiscales",
      modulo: "tributario",
    },
  ],
  ADMIN_BACKOFFICE: [
    {
      icono: "▤",
      titulo: "Gestión de contratos",
      descripcion:
        "Consulta los contratos y gestiona su cancelación o eliminación según su estado.",
      accionTexto: "Administrar contratos",
      modulo: "contratos",
    },
    {
      icono: "♙",
      titulo: "Gestión de cuentas",
      descripcion: "Consulta los usuarios registrados y gestiona la eliminación de sus cuentas.",
      accionTexto: "Administrar cuentas",
      modulo: "cuentas",
    },
    {
      icono: "✓",
      titulo: "Validaciones KYC",
      descripcion:
        "Aprueba o rechaza documentos de transportistas y perfiles tributarios de dadores de carga.",
      accionTexto: "Revisar validaciones",
      modulo: "validaciones",
    },
    {
      icono: "⚙",
      titulo: "Configuración",
      descripcion:
        "Ajusta reglas globales del sistema: porcentaje de IVA, tolerancia financiera y anticipación mínima.",
      accionTexto: "Editar reglas",
      modulo: "configuracion",
    },
    {
      icono: "◷",
      titulo: "Historial de acciones",
      descripcion: "Consulta quién realizó cada acción administrativa, cuándo y por qué.",
      accionTexto: "Consultar historial",
      modulo: "historial",
    },
  ],
};
