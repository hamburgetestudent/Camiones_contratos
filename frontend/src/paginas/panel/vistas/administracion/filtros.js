/* Filtros y opciones de los listados — admin — MansoViaje */
import { enlace, icono, nodo } from "../../ui.js";

export function filtrosListado(ruta, campos, params) {
  const form = nodo("form", null, "barra-filtros");
  const titulo = nodo("p", null, "barra-filtros-titulo");
  titulo.append(icono("filtro", 14), nodo("span", "Filtros"));
  const grid = nodo("div", null, "barra-filtros-grid");

  for (const [clave, etiqueta, tipo, opcionesLista] of campos) {
    const label = nodo("label", tipo === "checkbox" ? null : etiqueta);
    let control;
    if (opcionesLista) {
      control = nodo("select");
      for (const [v, t] of opcionesLista) {
        const o = nodo("option", t);
        o.value = v;
        control.append(o);
      }
    } else {
      control = nodo("input");
      control.type = tipo;
    }
    control.name = clave;
    if (tipo === "checkbox") {
      label.className = "filtro-check";
      control.value = "1";
      control.checked = params.get(clave) === "1";
      label.append(control, nodo("span", etiqueta));
    } else {
      control.value = params.get(clave) || "";
      label.append(control);
    }
    grid.append(label);
  }

  const acciones = nodo("div", null, "barra-filtros-acciones");
  const btnAplicar = nodo("button", "Aplicar filtros", "btn-primario");
  btnAplicar.type = "submit";
  acciones.append(btnAplicar, enlace("Limpiar", ruta));

  form.append(titulo, grid, acciones);
  form.onsubmit = (e) => {
    e.preventDefault();
    const consulta = new URLSearchParams();
    for (const [k, v] of new FormData(form)) {
      if (v.trim()) consulta.set(k, v.trim());
    }
    location.hash = ruta + (consulta.toString() ? "?" + consulta.toString() : "");
  };
  return form;
}

export function opciones(valores) {
  return [["", "Todos"], ...valores.map((v) => [v, v])];
}
