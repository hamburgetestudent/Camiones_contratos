/* Perfil tributario — dador — MansoViaje */
import { api, badgeEstado, mostrarAviso, nodo } from "../../ui.js";
import { estadoPanel } from "../../estado.js";
import { obtenerPerfilDadorOpcional } from "./comun.js";

export async function tributarioDador() {
  const perfil = await obtenerPerfilDadorOpcional();
  const f = document.createDocumentFragment();

  const cabecera = nodo("div", null, "resumen-estado");
  cabecera.append(
    nodo(
      "p",
      "Tu perfil tributario debe estar APROBADO por backoffice para poder emitir contratos.",
      "texto-suave"
    ),
    badgeEstado(perfil ? perfil.estado_validacion : "SIN REGISTRAR")
  );
  f.append(cabecera);

  const form = nodo("form", null, "form-panel");
  const grid = nodo("div", null, "form-grid");

  const campos = [
    [
      "rut_id_empresa",
      "RUT de la empresa *",
      "text",
      perfil?.rut_id_empresa || "",
      "Ej: 76123456-7",
    ],
    [
      "razon_social",
      "Razón social *",
      "text",
      perfil?.datos_facturacion?.razon_social || "",
      "Ej: Logística del Sur S.A.",
    ],
    [
      "direccion",
      "Dirección tributaria *",
      "text",
      perfil?.datos_facturacion?.direccion || "",
      "Ej: Av. Principal 123, Santiago",
    ],
    [
      "correo_facturacion",
      "Correo de facturación *",
      "email",
      perfil?.datos_facturacion?.correo_facturacion || estadoPanel.usuario.email || "",
      "facturacion@empresa.cl",
    ],
  ];

  const inputs = {};
  for (const [nombre, etiqueta, tipo, valor, placeholder] of campos) {
    const label = nodo("label", etiqueta);
    const input = nodo("input");
    input.type = tipo;
    input.name = nombre;
    input.required = true;
    input.value = valor;
    input.placeholder = placeholder;
    inputs[nombre] = input;
    label.append(input);
    grid.append(label);
  }

  const nota = nodo(
    "p",
    "Nota: Actualizar tus datos tributarios reinicia la validación a estado PENDIENTE hasta ser aprobada por un administrador.",
    "texto-suave"
  );
  const btnGuardar = nodo(
    "button",
    perfil ? "Actualizar perfil tributario" : "Registrar perfil tributario",
    "btn-primario"
  );
  btnGuardar.type = "submit";

  form.append(grid, nota, btnGuardar);
  form.onsubmit = async (e) => {
    e.preventDefault();
    btnGuardar.disabled = true;
    try {
      await api(
        "/onboarding/dador/perfil",
        {
          rut_id_empresa: inputs.rut_id_empresa.value.trim(),
          datos_facturacion: {
            razon_social: inputs.razon_social.value.trim(),
            direccion: inputs.direccion.value.trim(),
            correo_facturacion: inputs.correo_facturacion.value.trim(),
          },
        },
        { method: "POST", headers: { "X-User-Id": estadoPanel.usuario.id } }
      );
      await estadoPanel.navegar();
      mostrarAviso("Perfil tributario guardado. Estado actual: PENDIENTE de validación.", "exito");
    } catch (error) {
      mostrarAviso(error.message, "error");
    } finally {
      btnGuardar.disabled = false;
    }
  };

  f.append(form);
  return f;
}
