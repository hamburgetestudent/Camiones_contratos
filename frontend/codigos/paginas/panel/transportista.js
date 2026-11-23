/* Vistas operativas para el rol TRANSPORTISTA dentro del panel unificado. */

const ETIQUETAS_DOCUMENTOS = {
  LICENCIA_CONDUCIR: "Licencia de conducir",
  PADRON_VEHICULO: "Padrón del vehículo",
  REVISION_TECNICA: "Revisión técnica",
  SEGURO_CARGA: "Seguro de carga",
  ANTECEDENTES: "Certificado de antecedentes",
};

const TIPOS_CARGA_FILTRO = [
  "GENERAL",
  "REFRIGERADA",
  "PERECEDERA",
  "PELIGROSA",
  "FRAGIL",
  "VALORES",
  "GRANEL_LIQUIDO",
  "GRANEL_SOLIDO",
  "SOBREDIMENSIONADA",
  "VIVA",
  "VEHICULAR",
];

async function obtenerEstadoCompliance() {
  return api("/onboarding/transportista/estado", undefined, {
    headers: { "X-User-Id": usuario.id },
  });
}

async function inicioTransportista() {
  const [estadoKyc, cargas, contratos] = await Promise.all([
    obtenerEstadoCompliance(),
    api("/subastas/cargas"),
    api("/contratos"),
  ]);
  const asignados = contratos.filter((c) => c.id_transportista === usuario.id);

  const f = document.createDocumentFragment();
  f.append(
    nodo(
      "p",
      "Explora cargas disponibles para postular, gestiona tu documentación de cumplimiento y reporta el avance de tus viajes.",
      "texto-suave"
    )
  );

  const grid = nodo("div", null, "rejilla");
  const kpis = [
    ["Estado Compliance", estadoKyc.estado_global, "onboarding"],
    ["Cargas disponibles", String(cargas.length), "subastas"],
    ["Despachos asignados", String(asignados.length), "seguimiento"],
  ];
  for (const [titulo, valor, modulo] of kpis) {
    const card = enlace("", modulo);
    card.className = "tarjeta";
    card.append(nodo("span", titulo), nodo("strong", valor, "indicador"));
    grid.append(card);
  }

  f.append(grid, nodo("h2", "Accesos rápidos"), tarjetas(FUNCIONALIDADES_POR_ROL.TRANSPORTISTA));
  return f;
}

async function subastasTransportista(params) {
  const consulta = new URLSearchParams();
  if (params.get("region")) consulta.set("region", params.get("region"));
  if (params.get("tipo_carroceria")) consulta.set("tipo_carroceria", params.get("tipo_carroceria"));
  if (params.get("distancia_max_km"))
    consulta.set("distancia_max_km", params.get("distancia_max_km"));

  const [cargas, estadoKyc] = await Promise.all([
    api("/subastas/cargas" + (consulta.toString() ? "?" + consulta : "")),
    obtenerEstadoCompliance(),
  ]);

  const f = document.createDocumentFragment();
  const barra = nodo("div", null, "acciones-barra");
  const btnCatalogo = nodo("a", "Abrir vista catálogo", "boton");
  btnCatalogo.href = "../Principal/principal.html";
  barra.append(btnCatalogo, badgeEstado("KYC: " + estadoKyc.estado_global));
  f.append(barra);

  const cargaId = params.get("carga");
  if (cargaId) {
    const carga = cargas.find((c) => c.id === cargaId);
    f.append(enlace("← Volver a cargas disponibles", "subastas"));
    if (!carga) {
      f.append(nodo("p", "La carga seleccionada ya no está disponible.", "texto-suave"));
      return f;
    }

    const requisitos = [];
    if (carga.requiere_termo) requisitos.push("Equipo termo/refrigeración");
    if (carga.req_blindaje) requisitos.push("Camión blindado");
    if (carga.numero_onu) requisitos.push("ONU " + carga.numero_onu);
    if (carga.req_embalaje) requisitos.push("Embalaje: " + carga.req_embalaje);

    f.append(
      nodo("h2", carga.origen + " → " + carga.destino),
      ficha([
        ["Estado", badgeEstado(carga.estado)],
        ["Tipo de carga", carga.tipo_carga],
        ["Peso / Capacidad", carga.peso_total + " KG / " + carga.input_camionKG + " KG"],
        ["Distancia", carga.distancia_km != null ? carga.distancia_km + " km" : "Estimada 150 km"],
        ["Monto referencial", formatearMoneda(carga.monto_total, carga.moneda)],
        ["Cierre de postulaciones", fechaLocal(carga.f_cierre_postulaciones)],
        ["Salida estimada", fechaLocal(carga.f_estimada_salida)],
        ["Llegada estimada", fechaLocal(carga.f_estimada_llegada)],
        ["Requisitos especiales", requisitos.length ? requisitos.join(" · ") : "Ninguno"],
      ])
    );

    const aprobado = estadoKyc.estado_global === "APROBADO";
    if (!aprobado) {
      const alerta = nodo(
        "p",
        "Tu documentación aún no está en estado APROBADO (" +
          estadoKyc.estado_global +
          "). Completa tus documentos para poder postular.",
        "aviso-info"
      );
      alerta.style.padding = "12px";
      f.append(alerta, enlace("Ir a Documentación y Compliance", "onboarding"));
    }

    const form = nodo("form", null, "form-panel");
    form.append(nodo("h3", "Enviar postulación / oferta"));
    const grid = nodo("div", null, "form-grid");

    const lPrecio = nodo("label", "Tarifa ofertada (CLP, mín. $5.000) *");
    const iPrecio = nodo("input");
    iPrecio.type = "number";
    iPrecio.min = "5000";
    iPrecio.step = "100";
    iPrecio.required = true;
    iPrecio.value = String(Math.max(5000, Math.round(carga.monto_neto || 50000)));
    lPrecio.append(iPrecio);

    const lTiempo = nodo("label", "Tiempo estimado de entrega (horas) *");
    const iTiempo = nodo("input");
    iTiempo.type = "number";
    iTiempo.min = "0.5";
    iTiempo.step = "0.5";
    iTiempo.required = true;
    iTiempo.value = "8";
    lTiempo.append(iTiempo);

    grid.append(lPrecio, lTiempo);

    const lComentario = nodo("label", "Comentario adicional (opcional)");
    const iComentario = nodo("textarea");
    iComentario.rows = 3;
    iComentario.maxLength = 500;
    iComentario.placeholder = "Indica disponibilidad, tipo de camión o condiciones de retiro...";
    lComentario.append(iComentario);

    const btnEnviar = nodo("button", "Enviar postulación", "btn-primario");
    btnEnviar.type = "submit";

    form.append(grid, lComentario, btnEnviar);
    form.onsubmit = async (e) => {
      e.preventDefault();
      btnEnviar.disabled = true;
      try {
        await api(
          "/subastas/postular?onboarding_aprobado=" + String(aprobado),
          {
            carga_id: carga.id,
            transportista_id: usuario.id,
            precio_oferta: Number(iPrecio.value),
            tiempo_entrega_horas: Number(iTiempo.value),
            comentario: iComentario.value.trim() || null,
          },
          { method: "POST" }
        );
        mostrarAviso("¡Postulación enviada correctamente!", "exito");
        iComentario.value = "";
      } catch (error) {
        mostrarAviso(error.message, "error");
      } finally {
        btnEnviar.disabled = false;
      }
    };

    f.append(form);
    return f;
  }

  // Filtros reales conectados a GET /subastas/cargas
  const formFiltros = nodo("form");
  const fs = nodo("fieldset");
  fs.append(nodo("legend", "Filtrar cargas disponibles"));

  const lRegion = nodo("label", "Región / Comuna");
  const iRegion = nodo("input");
  iRegion.type = "text";
  iRegion.name = "region";
  iRegion.placeholder = "Ej: Santiago, Valparaíso";
  iRegion.value = params.get("region") || "";
  lRegion.append(iRegion);

  const lTipo = nodo("label", "Tipo de carga");
  const sTipo = nodo("select");
  sTipo.name = "tipo_carroceria";
  const optTodos = nodo("option", "Todos");
  optTodos.value = "";
  sTipo.append(optTodos);
  for (const tipo of TIPOS_CARGA_FILTRO) {
    const opt = nodo("option", tipo);
    opt.value = tipo;
    sTipo.append(opt);
  }
  sTipo.value = params.get("tipo_carroceria") || "";
  lTipo.append(sTipo);

  const lDist = nodo("label", "Distancia máxima (km)");
  const iDist = nodo("input");
  iDist.type = "number";
  iDist.name = "distancia_max_km";
  iDist.min = "1";
  iDist.placeholder = "Sin límite";
  iDist.value = params.get("distancia_max_km") || "";
  lDist.append(iDist);

  const btnBuscar = nodo("button", "Buscar", "btn-primario");
  btnBuscar.type = "submit";
  fs.append(lRegion, lTipo, lDist, btnBuscar, enlace("Limpiar", "subastas"));
  formFiltros.append(fs);
  formFiltros.onsubmit = (e) => {
    e.preventDefault();
    const q = new URLSearchParams();
    if (iRegion.value.trim()) q.set("region", iRegion.value.trim());
    if (sTipo.value) q.set("tipo_carroceria", sTipo.value);
    if (iDist.value) q.set("distancia_max_km", iDist.value);
    location.hash = "subastas" + (q.toString() ? "?" + q : "");
  };

  f.append(formFiltros);

  if (!cargas.length) {
    f.append(
      nodo("p", "No hay cargas disponibles que coincidan con los filtros actuales.", "texto-suave")
    );
    return f;
  }

  const lista = nodo("div", null, "lista-tarjetas");
  for (const c of cargas) {
    const card = nodo("article", null, "tarjeta-carga");
    const top = nodo("div", null, "tarjeta-carga-top");
    top.append(
      badgeEstado(c.estado),
      nodo("span", formatearMoneda(c.monto_total, c.moneda), "monto-destacado")
    );
    const meta = nodo("div", null, "meta-linea");
    meta.append(
      nodo("span", "Carga: " + c.tipo_carga),
      nodo("span", c.peso_total + " / " + c.input_camionKG + " KG"),
      nodo("span", "Cierre: " + fechaLocal(c.f_cierre_postulaciones))
    );
    const btnPostular = enlace("Ver detalle y postular", "subastas", { carga: c.id });
    btnPostular.classList.add("btn-primario");
    card.append(top, nodo("h3", c.origen + " → " + c.destino), meta, btnPostular);
    lista.append(card);
  }
  f.append(lista);
  return f;
}

async function onboardingTransportista() {
  const estado = await obtenerEstadoCompliance();
  const docsPorTipo = new Map(estado.documentos_cargados.map((d) => [d.tipo, d]));
  const aprobados = estado.documentos_requeridos.filter(
    (tipo) => docsPorTipo.get(tipo)?.estado === "APROBADO"
  ).length;
  const porcentaje = Math.round((aprobados / estado.documentos_requeridos.length) * 100);

  const f = document.createDocumentFragment();
  const resumen = nodo("div", null, "tarjeta");
  const top = nodo("div", null, "resumen-estado");
  top.style.width = "100%";
  top.append(
    nodo(
      "strong",
      "Progreso de validación: " +
        aprobados +
        " de " +
        estado.documentos_requeridos.length +
        " aprobados"
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
          doc ? doc.archivo : "Sin cargar",
          doc ? fechaLocal(doc.created_at) : "—",
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
  for (const tipo of estado.documentos_requeridos) {
    const opt = nodo("option", ETIQUETAS_DOCUMENTOS[tipo] || tipo);
    opt.value = tipo;
    sTipo.append(opt);
  }
  lTipo.append(sTipo);

  const lArchivo = nodo("label", "Nombre o ruta de archivo (.pdf, .jpg, .jpeg, .png) *");
  const iArchivo = nodo("input");
  iArchivo.type = "text";
  iArchivo.name = "archivo";
  iArchivo.required = true;
  iArchivo.placeholder = "Ej: licencia_conducir_2026.pdf";
  lArchivo.append(iArchivo);

  grid.append(lTipo, lArchivo);
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
        { method: "POST", headers: { "X-User-Id": usuario.id } }
      );
      await navegar();
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

async function seguimientoTransportista() {
  const contratos = await api("/contratos");
  const asignados = contratos.filter((c) => c.id_transportista === usuario.id);
  const f = document.createDocumentFragment();

  f.append(
    nodo(
      "p",
      "Reporta el inicio de tránsito y la entrega de los contratos que te fueron adjudicados.",
      "texto-suave"
    )
  );

  async function avanzarEstado(contratoId, nuevoEstado) {
    try {
      await api(
        "/contratos/" + contratoId + "/estado",
        { nuevo_estado: nuevoEstado },
        { method: "PATCH" }
      );
      await navegar();
      mostrarAviso("Despacho actualizado a estado " + nuevoEstado + ".", "exito");
    } catch (error) {
      mostrarAviso(error.message, "error");
    }
  }

  f.append(
    tabla(
      ["Ruta", "Tipo carga", "Salida estimada", "Monto total", "Estado", "Acciones"],
      asignados.map((c) => {
        const acciones = nodo("div", null, "acciones-grupo");
        if (c.estado === "ADJUDICADO") {
          acciones.append(
            boton("Iniciar tránsito", () => avanzarEstado(c.id, "EN_TRANSITO"), "btn-primario")
          );
        } else if (c.estado === "EN_TRANSITO") {
          acciones.append(
            boton("Confirmar entrega", () => avanzarEstado(c.id, "ENTREGADO"), "btn-exito"),
            boton("Reportar disputa", () => avanzarEstado(c.id, "EN_DISPUTA"), "peligro")
          );
        } else {
          acciones.append(nodo("span", "Sin acciones pendientes", "texto-suave"));
        }
        return [
          c.origen + " → " + c.destino,
          c.tipo_carga,
          fechaLocal(c.f_estimada_salida),
          formatearMoneda(c.monto_total, c.moneda),
          badgeEstado(c.estado),
          acciones,
        ];
      }),
      "Aún no tienes contratos adjudicados asignados a tu cuenta."
    )
  );
  return f;
}

async function vistaTransportista(ruta, params) {
  if (ruta === "inicio") return inicioTransportista();
  if (ruta === "subastas") return subastasTransportista(params);
  if (ruta === "onboarding") return onboardingTransportista();
  if (ruta === "seguimiento") return seguimientoTransportista();
  return inicioTransportista();
}
