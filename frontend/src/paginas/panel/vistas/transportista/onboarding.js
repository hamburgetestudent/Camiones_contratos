/* Documentación y compliance — transportista — MansoViaje */
import { api, badgeEstado, fechaLocal, icono, mostrarAviso, nodo, tabla } from "../../ui.js";
import { estadoPanel } from "../../estado.js";
import { obtenerEstadoCompliance } from "./comun.js";

/* Vistas operativas para el rol TRANSPORTISTA dentro del panel unificado — MansoViaje */

const ETIQUETAS_DOCUMENTOS = {
  LICENCIA_CONDUCIR: "Licencia de conducir",
  PADRON_VEHICULO: "Padrón del vehículo",
  REVISION_TECNICA: "Revisión técnica",
  SEGURO_CARGA: "Seguro de carga",
  ANTECEDENTES: "Certificado de antecedentes",
};

export async function onboardingTransportista() {
  const estado = await obtenerEstadoCompliance();
  const docsPorTipo = new Map(estado.documentos_cargados.map((d) => [d.tipo, d]));
  const aprobados = estado.documentos_requeridos.filter(
    (tipo) => docsPorTipo.get(tipo)?.estado === "APROBADO"
  ).length;
  const porcentaje = Math.round((aprobados / estado.documentos_requeridos.length) * 100);

  const f = document.createDocumentFragment();
  const resumen = nodo("div", null, "tarjeta");
  const top = nodo("div", null, "resumen-estado");
  top.append(
    nodo(
      "strong",
      "Progreso de validación: " +
        aprobados +
        " de " +
        estado.documentos_requeridos.length +
        " aprobados (" +
        porcentaje +
        "%)"
    ),
    badgeEstado(estado.estado_global)
  );
  const barra = nodo("div", null, "barra-progreso");
  const relleno = nodo("span");
  relleno.style.width = porcentaje + "%";
  if (porcentaje === 100) relleno.className = "completo";
  barra.append(relleno);
  resumen.append(top, barra);
  f.append(resumen);

  f.append(
    nodo("h2", "Documentos requeridos"),
    tabla(
      ["Documento", "Archivo cargado", "Última actualización", "Estado"],
      estado.documentos_requeridos.map((tipo) => {
        const doc = docsPorTipo.get(tipo);
        return [
          ETIQUETAS_DOCUMENTOS[tipo] || tipo,
          doc ? nodo("code", doc.archivo, "id-corto") : nodo("span", "Sin cargar", "texto-suave"),
          doc ? nodo("span", fechaLocal(doc.created_at), "num-tabular") : "—",
          doc ? badgeEstado(doc.estado) : badgeEstado("FALTANTE"),
        ];
      }),
      "No se encontraron documentos requeridos."
    )
  );

  const form = nodo("form", null, "form-panel");
  form.append(nodo("h3", "Cargar o actualizar documento"));
  const grid = nodo("div", null, "form-grid");

  const lTipo = nodo("label", "Tipo de documento *");
  const sTipo = nodo("select");
  sTipo.name = "tipo";
  let primeroPendiente = null;
  for (const tipo of estado.documentos_requeridos) {
    const doc = docsPorTipo.get(tipo);
    if (!primeroPendiente && (!doc || doc.estado === "RECHAZADO")) {
      primeroPendiente = tipo;
    }
    const opt = nodo("option", ETIQUETAS_DOCUMENTOS[tipo] || tipo);
    opt.value = tipo;
    sTipo.append(opt);
  }
  if (primeroPendiente) sTipo.value = primeroPendiente;
  lTipo.append(sTipo);

  const lArchivoWrap = nodo("div", null, "archivo-selector-wrap");
  const lArchivo = nodo("label", "Nombre o ruta de archivo (.pdf, .jpg, .jpeg, .png) *");
  const iArchivo = nodo("input");
  iArchivo.type = "text";
  iArchivo.name = "archivo";
  iArchivo.required = true;
  iArchivo.placeholder = "Ej: licencia_conducir_2026.pdf";
  lArchivo.append(iArchivo);

  const selectorDrop = nodo("label", null, "archivo-drop");
  const textoDrop = nodo("span", "Seleccionar archivo desde tu equipo (autocompleta el nombre)");
  const iFile = nodo("input");
  iFile.type = "file";
  iFile.accept = ".pdf,.jpg,.jpeg,.png";
  iFile.addEventListener("change", () => {
    const archivo = iFile.files && iFile.files[0];
    if (archivo) {
      iArchivo.value = archivo.name;
      textoDrop.textContent = "Seleccionado: " + archivo.name;
    }
  });
  selectorDrop.append(icono("subir", 16), textoDrop, iFile);
  lArchivoWrap.append(lArchivo, selectorDrop);

  grid.append(lTipo, lArchivoWrap);
  const btnCargar = nodo("button", "Cargar documento", "btn-primario");
  btnCargar.type = "submit";
  form.append(grid, btnCargar);

  form.onsubmit = async (e) => {
    e.preventDefault();
    btnCargar.disabled = true;
    try {
      await api(
        "/onboarding/transportista/documentos",
        {
          tipo: sTipo.value,
          archivo: iArchivo.value.trim(),
        },
        { method: "POST", headers: { "X-User-Id": estadoPanel.usuario.id } }
      );
      await estadoPanel.navegar();
      mostrarAviso("Documento cargado correctamente. Quedó en estado PENDIENTE.", "exito");
    } catch (error) {
      mostrarAviso(error.message, "error");
    } finally {
      btnCargar.disabled = false;
    }
  };

  f.append(form);
  return f;
}
