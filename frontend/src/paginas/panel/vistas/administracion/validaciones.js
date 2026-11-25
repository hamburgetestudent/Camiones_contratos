/* Validaciones de cuentas (KYC) — admin — MansoViaje */
import {
  api,
  badgeEstado,
  boton,
  celdaId,
  fechaLocal,
  mostrarAviso,
  nodo,
  tabla,
} from "../../ui.js";
import { estadoPanel } from "../../estado.js";

export async function validacionesAdmin() {
  const [documentos, dadores] = await Promise.all([
    api("/onboarding/admin/documentos"),
    api("/onboarding/admin/dadores"),
  ]);
  const f = document.createDocumentFragment();
  f.append(
    nodo(
      "p",
      "Revisa y aprueba o rechaza la documentación de transportistas y los perfiles tributarios de dadores pendientes.",
      "subtitulo-seccion"
    )
  );

  async function resolverDocumento(id, estado) {
    try {
      await api("/onboarding/admin/documentos/" + id + "/validar", { estado }, { method: "PATCH" });
      await estadoPanel.navegar();
      mostrarAviso("Documento marcado como " + estado + ".", "exito");
    } catch (error) {
      mostrarAviso(error.message, "error");
    }
  }

  async function resolverDador(id, estado_validacion) {
    try {
      await api(
        "/onboarding/admin/dadores/" + id + "/validar",
        { estado_validacion },
        { method: "PATCH" }
      );
      await estadoPanel.navegar();
      mostrarAviso("Perfil de dador marcado como " + estado_validacion + ".", "exito");
    } catch (error) {
      mostrarAviso(error.message, "error");
    }
  }

  f.append(
    nodo("h2", "Documentos de transportistas pendientes (" + documentos.length + ")"),
    tabla(
      ["Tipo de documento", "Archivo", "Usuario ID", "Fecha carga", "Estado", "Acciones"],
      documentos.map((doc) => {
        const acciones = nodo("div", null, "acciones-grupo");
        acciones.append(
          boton("Aprobar", () => resolverDocumento(doc.id, "APROBADO"), "btn-exito btn-sm"),
          boton("Rechazar", () => resolverDocumento(doc.id, "RECHAZADO"), "peligro btn-sm")
        );
        return [
          doc.tipo,
          doc.archivo,
          celdaId(doc.user_id),
          nodo("span", fechaLocal(doc.created_at), "num-tabular"),
          badgeEstado(doc.estado),
          acciones,
        ];
      }),
      "No hay documentos de transportistas pendientes de revisión."
    )
  );

  f.append(
    nodo("h2", "Perfiles tributarios de dadores pendientes (" + dadores.length + ")"),
    tabla(
      ["RUT empresa", "Razón social", "Dirección", "Correo facturación", "Estado", "Acciones"],
      dadores.map((dador) => {
        const acciones = nodo("div", null, "acciones-grupo");
        acciones.append(
          boton("Aprobar", () => resolverDador(dador.id, "APROBADO"), "btn-exito btn-sm"),
          boton("Rechazar", () => resolverDador(dador.id, "RECHAZADO"), "peligro btn-sm")
        );
        return [
          nodo("span", dador.rut_id_empresa, "num-tabular"),
          dador.datos_facturacion?.razon_social,
          dador.datos_facturacion?.direccion,
          dador.datos_facturacion?.correo_facturacion,
          badgeEstado(dador.estado_validacion),
          acciones,
        ];
      }),
      "No hay perfiles tributarios de dadores pendientes de validación."
    )
  );

  return f;
}
