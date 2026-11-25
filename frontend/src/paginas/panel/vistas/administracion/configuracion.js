/* Configuración de reglas de negocio — admin — MansoViaje */
import { api, mostrarAviso, nodo } from "../../ui.js";

export async function configuracionAdmin() {
  const cfg = await api("/configuracion");
  const f = document.createDocumentFragment();
  f.append(
    nodo(
      "p",
      "Ajusta las reglas de negocio globales vigentes para la creación y validación de contratos.",
      "subtitulo-seccion"
    )
  );

  const form = nodo("form", null, "form-panel");
  const grid = nodo("div", null, "form-grid");

  const labelIva = nodo("label", "Tasa de IVA (decimal entre 0 y 1)");
  const inputIva = nodo("input");
  inputIva.type = "number";
  inputIva.name = "iva_porcentaje";
  inputIva.min = "0";
  inputIva.max = "1";
  inputIva.step = "0.01";
  inputIva.required = true;
  inputIva.value = String(cfg.iva_porcentaje);
  labelIva.append(inputIva, nodo("small", "Ejemplo: 0.19 equivale a 19%.", "texto-suave"));

  const labelTol = nodo("label", "Tolerancia financiera máxima");
  const inputTol = nodo("input");
  inputTol.type = "number";
  inputTol.name = "tolerancia_max";
  inputTol.min = "0";
  inputTol.step = "0.01";
  inputTol.required = true;
  inputTol.value = String(cfg.tolerancia_max);
  labelTol.append(inputTol, nodo("small", "Margen máximo en cuadratura de montos.", "texto-suave"));

  const labelAnt = nodo("label", "Anticipación mínima de salida (horas)");
  const inputAnt = nodo("input");
  inputAnt.type = "number";
  inputAnt.name = "anticipacion_min_h";
  inputAnt.min = "0";
  inputAnt.step = "1";
  inputAnt.required = true;
  inputAnt.value = String(cfg.anticipacion_min_h);
  labelAnt.append(
    inputAnt,
    nodo("small", "Horas mínimas antes de la salida programada.", "texto-suave")
  );

  grid.append(labelIva, labelTol, labelAnt);

  const acciones = nodo("div", null, "acciones-grupo");
  const btnGuardar = nodo("button", "Guardar configuración", "btn-primario");
  btnGuardar.type = "submit";
  acciones.append(btnGuardar);

  form.append(grid, acciones);
  form.onsubmit = async (e) => {
    e.preventDefault();
    btnGuardar.disabled = true;
    try {
      const actualizado = await api(
        "/configuracion",
        {
          iva_porcentaje: Number(inputIva.value),
          tolerancia_max: Number(inputTol.value),
          anticipacion_min_h: Number(inputAnt.value),
        },
        { method: "PATCH" }
      );
      inputIva.value = String(actualizado.iva_porcentaje);
      inputTol.value = String(actualizado.tolerancia_max);
      inputAnt.value = String(actualizado.anticipacion_min_h);
      mostrarAviso("Configuración global actualizada correctamente.", "exito");
    } catch (error) {
      mostrarAviso(error.message, "error");
    } finally {
      btnGuardar.disabled = false;
    }
  };

  f.append(form);
  return f;
}
