/* Catálogo offline de íconos SVG monocromáticos y helpers de UI compartidos — MansoViaje */
const SVG_NS = "http://www.w3.org/2000/svg";

const ICONOS = {
  inicio: [
    ["path", { d: "M3 10.5L12 3l9 7.5" }],
    ["path", { d: "M5 9.5V20a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V9.5" }],
    ["path", { d: "M9 21v-6h6v6" }],
  ],
  contratos: [
    ["path", { d: "M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" }],
    ["polyline", { points: "14 2 14 8 20 8" }],
    ["line", { x1: "8", y1: "13", x2: "16", y2: "13" }],
    ["line", { x1: "8", y1: "17", x2: "13", y2: "17" }],
  ],
  cuentas: [
    ["path", { d: "M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" }],
    ["circle", { cx: "9", cy: "7", r: "4" }],
    ["path", { d: "M22 21v-2a4 4 0 0 0-3-3.87" }],
    ["path", { d: "M16 3.13a4 4 0 0 1 0 7.75" }],
  ],
  validaciones: [
    ["path", { d: "M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" }],
    ["path", { d: "m9 12 2 2 4-4" }],
  ],
  configuracion: [
    ["circle", { cx: "12", cy: "12", r: "3" }],
    [
      "path",
      {
        d: "M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 1 1-4 0v-.09a1.65 1.65 0 0 0-1-1.51 1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 1 1 0-4h.09a1.65 1.65 0 0 0 1.51-1 1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33h.01a1.65 1.65 0 0 0 .99-1.51V3a2 2 0 1 1 4 0v.09a1.65 1.65 0 0 0 1 1.51h.01a1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82v.01a1.65 1.65 0 0 0 1.51.99H21a2 2 0 1 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z",
      },
    ],
  ],
  historial: [
    ["circle", { cx: "12", cy: "12", r: "9" }],
    ["polyline", { points: "12 7 12 12 15.5 14" }],
  ],
  subastas: [
    ["path", { d: "M12 3v18" }],
    ["path", { d: "M5 7h14" }],
    ["path", { d: "m5 7-2 6a4 4 0 0 0 4 0l-2-6z" }],
    ["path", { d: "m19 7-2 6a4 4 0 0 0 4 0l-2-6z" }],
    ["path", { d: "M8 21h8" }],
  ],
  documentos: [
    ["path", { d: "M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" }],
    ["polyline", { points: "14 2 14 8 20 8" }],
    ["path", { d: "m9 15 2 2 4-4" }],
  ],
  seguimiento: [
    ["rect", { x: "1", y: "5", width: "15", height: "11", rx: "2" }],
    ["path", { d: "M16 9h4l3 4v3h-7V9z" }],
    ["circle", { cx: "5.5", cy: "18.5", r: "2.5" }],
    ["circle", { cx: "18.5", cy: "18.5", r: "2.5" }],
  ],
  tributario: [
    ["rect", { x: "3", y: "4", width: "18", height: "16", rx: "2" }],
    ["line", { x1: "3", y1: "10", x2: "21", y2: "10" }],
    ["line", { x1: "7", y1: "15", x2: "11", y2: "15" }],
  ],
  camion: [
    ["rect", { x: "1", y: "5", width: "15", height: "11", rx: "2" }],
    ["path", { d: "M16 9h4l3 4v3h-7V9z" }],
    ["circle", { cx: "5.5", cy: "18.5", r: "2.5" }],
    ["circle", { cx: "18.5", cy: "18.5", r: "2.5" }],
  ],
  empresa: [
    ["rect", { x: "4", y: "3", width: "16", height: "18", rx: "2" }],
    ["path", { d: "M9 21v-4h6v4" }],
    ["path", { d: "M8 7h2" }],
    ["path", { d: "M14 7h2" }],
    ["path", { d: "M8 11h2" }],
    ["path", { d: "M14 11h2" }],
  ],
  catalogo: [
    ["rect", { x: "3", y: "3", width: "7", height: "7", rx: "1.5" }],
    ["rect", { x: "14", y: "3", width: "7", height: "7", rx: "1.5" }],
    ["rect", { x: "3", y: "14", width: "7", height: "7", rx: "1.5" }],
    ["rect", { x: "14", y: "14", width: "7", height: "7", rx: "1.5" }],
  ],
  salir: [
    ["path", { d: "M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" }],
    ["polyline", { points: "16 17 21 12 16 7" }],
    ["line", { x1: "21", y1: "12", x2: "9", y2: "12" }],
  ],
  menu: [
    ["line", { x1: "4", y1: "6", x2: "20", y2: "6" }],
    ["line", { x1: "4", y1: "12", x2: "20", y2: "12" }],
    ["line", { x1: "4", y1: "18", x2: "20", y2: "18" }],
  ],
  ojo: [
    ["path", { d: "M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7-10-7-10-7z" }],
    ["circle", { cx: "12", cy: "12", r: "3" }],
  ],
  ojoCerrado: [
    [
      "path",
      { d: "M17.94 17.94A10.94 10.94 0 0 1 12 19c-6.5 0-10-7-10-7a18.4 18.4 0 0 1 5.06-5.94" },
    ],
    ["path", { d: "M9.9 4.24A10.9 10.9 0 0 1 12 5c6.5 0 10 7 10 7a18.5 18.5 0 0 1-2.16 3.19" }],
    ["line", { x1: "2", y1: "2", x2: "22", y2: "22" }],
  ],
  copiar: [
    ["rect", { x: "9", y: "9", width: "13", height: "13", rx: "2" }],
    ["path", { d: "M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" }],
  ],
  check: [["polyline", { points: "20 6 9 17 4 12" }]],
  exito: [
    ["circle", { cx: "12", cy: "12", r: "9" }],
    ["path", { d: "m9 12 2 2 4-4" }],
  ],
  alerta: [
    [
      "path",
      {
        d: "M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z",
      },
    ],
    ["line", { x1: "12", y1: "9", x2: "12", y2: "13" }],
    ["line", { x1: "12", y1: "17", x2: "12.01", y2: "17" }],
  ],
  error: [
    ["circle", { cx: "12", cy: "12", r: "9" }],
    ["line", { x1: "15", y1: "9", x2: "9", y2: "15" }],
    ["line", { x1: "9", y1: "9", x2: "15", y2: "15" }],
  ],
  info: [
    ["circle", { cx: "12", cy: "12", r: "9" }],
    ["line", { x1: "12", y1: "16", x2: "12", y2: "12" }],
    ["line", { x1: "12", y1: "8", x2: "12.01", y2: "8" }],
  ],
  cerrar: [
    ["line", { x1: "18", y1: "6", x2: "6", y2: "18" }],
    ["line", { x1: "6", y1: "6", x2: "18", y2: "18" }],
  ],
  flechaIzq: [
    ["line", { x1: "19", y1: "12", x2: "5", y2: "12" }],
    ["polyline", { points: "12 19 5 12 12 5" }],
  ],
  flechaDer: [
    ["line", { x1: "5", y1: "12", x2: "19", y2: "12" }],
    ["polyline", { points: "12 5 19 12 12 19" }],
  ],
  mas: [
    ["line", { x1: "12", y1: "5", x2: "12", y2: "19" }],
    ["line", { x1: "5", y1: "12", x2: "19", y2: "12" }],
  ],
  buscar: [
    ["circle", { cx: "11", cy: "11", r: "7" }],
    ["line", { x1: "21", y1: "21", x2: "16.65", y2: "16.65" }],
  ],
  filtro: [["polygon", { points: "22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3" }]],
  subir: [
    ["path", { d: "M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" }],
    ["polyline", { points: "17 8 12 3 7 8" }],
    ["line", { x1: "12", y1: "3", x2: "12", y2: "15" }],
  ],
  bandejaVacia: [
    ["polyline", { points: "22 12 16 12 14 15 10 15 8 12 2 12" }],
    [
      "path",
      {
        d: "M5.45 5.11 2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z",
      },
    ],
  ],
  isotipo: [
    ["path", { d: "M3 16V7a2 2 0 0 1 2-2h9v11H3z" }],
    ["path", { d: "M14 9h4.5L21 12.5V16h-7V9z" }],
    ["circle", { cx: "7.5", cy: "17.5", r: "2" }],
    ["circle", { cx: "17.5", cy: "17.5", r: "2" }],
  ],
};

function crear(nombre, opciones = {}) {
  const tamano = opciones.size || 18;
  const svg = document.createElementNS(SVG_NS, "svg");
  svg.setAttribute("viewBox", "0 0 24 24");
  svg.setAttribute("width", String(tamano));
  svg.setAttribute("height", String(tamano));
  svg.setAttribute("fill", "none");
  svg.setAttribute("stroke", "currentColor");
  svg.setAttribute("stroke-width", String(opciones.strokeWidth || 1.75));
  svg.setAttribute("stroke-linecap", "round");
  svg.setAttribute("stroke-linejoin", "round");
  svg.setAttribute("aria-hidden", "true");
  svg.setAttribute("class", "mv-icono" + (opciones.className ? " " + opciones.className : ""));

  const formas = ICONOS[nombre] || ICONOS.info;
  for (const [tag, attrs] of formas) {
    const el = document.createElementNS(SVG_NS, tag);
    for (const [k, v] of Object.entries(attrs)) {
      el.setAttribute(k, v);
    }
    svg.appendChild(el);
  }
  return svg;
}

function claseBadgeEstado(estado) {
  const valor = String(estado || "")
    .trim()
    .toUpperCase();
  if (
    ["APROBADO", "SELECCIONADA", "FINALIZADO", "ENTREGADO", "COMPLETADO", "VIGENTE"].includes(
      valor
    ) ||
    valor.includes("APROBADO")
  ) {
    return "badge-aprobado";
  }
  if (
    ["PENDIENTE", "EN_REVISION", "EN_SUBASTA", "EN_POSTULACION", "EN_DISPUTA"].includes(valor) ||
    valor.includes("PENDIENTE") ||
    valor.includes("REVISION")
  ) {
    return "badge-pendiente";
  }
  if (
    ["RECHAZADO", "RECHAZADA", "CANCELADO", "ELIMINADO", "FALTANTE", "SIN REGISTRAR"].includes(
      valor
    ) ||
    valor.includes("RECHAZADO")
  ) {
    return "badge-rechazado";
  }
  if (["PUBLICADO", "ADJUDICADO", "EN_TRANSITO", "POSTULADA"].includes(valor)) {
    return "badge-info";
  }
  return "badge-neutro";
}

function badgeEstado(estado, textoPersonalizado) {
  const span = document.createElement("span");
  const etiqueta = textoPersonalizado ?? String(estado || "—");
  span.className = "badge " + claseBadgeEstado(estado);
  span.textContent = etiqueta;
  return span;
}

function iniciales(nombre) {
  return (
    String(nombre || "MV")
      .trim()
      .split(/\s+/)
      .slice(0, 2)
      .map((palabra) => palabra.charAt(0).toLocaleUpperCase("es-CL"))
      .join("") || "MV"
  );
}

export const MVIconos = {
  crear,
  claseBadgeEstado,
  badgeEstado,
  iniciales,
};
