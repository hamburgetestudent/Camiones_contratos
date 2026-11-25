window.PanelVistas = window.PanelVistas || {};
(function () {
  /* Vistas operativas para el rol TRANSPORTISTA dentro del panel unificado — MansoViaje */

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

  function obtenerChipsRequisitos(carga) {
    const chips = [];
    if (carga.requiere_termo) chips.push("Equipo termo");
    if (carga.req_blindaje) chips.push("Blindado");
    if (carga.numero_onu) chips.push("ONU " + carga.numero_onu);
    if (carga.req_embalaje) chips.push("Embalaje especial");
    return chips;
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
        "subtitulo-seccion"
      )
    );

    const grid = nodo("div", null, "rejilla-kpi");
    for (const kpi of [
      {
        titulo: "Estado Compliance",
        valor: estadoKyc.estado_global,
        modulo: "onboarding",
        iconoNombre: "validaciones",
        esEstado: true,
      },
      {
        titulo: "Cargas disponibles",
        valor: cargas.length,
        modulo: "subastas",
        iconoNombre: "subastas",
      },
      {
        titulo: "Despachos asignados",
        valor: asignados.length,
        modulo: "seguimiento",
        iconoNombre: "seguimiento",
      },
    ]) {
      grid.append(tarjetaKpi(kpi));
    }

    f.append(grid, nodo("h2", "Accesos rápidos"), tarjetas(FUNCIONALIDADES_POR_ROL.TRANSPORTISTA));
    return f;
  }

  async function subastasTransportista(params) {
    const consulta = new URLSearchParams();
    if (params.get("region")) consulta.set("region", params.get("region"));
    if (params.get("tipo_carroceria"))
      consulta.set("tipo_carroceria", params.get("tipo_carroceria"));
    if (params.get("distancia_max_km"))
      consulta.set("distancia_max_km", params.get("distancia_max_km"));

    const [cargas, estadoKyc] = await Promise.all([
      api("/subastas/cargas" + (consulta.toString() ? "?" + consulta : "")),
      obtenerEstadoCompliance(),
    ]);

    const f = document.createDocumentFragment();
    const barra = nodo("div", null, "acciones-barra");
    const btnCatalogo = nodo("a", "Abrir vista catálogo", "boton");
    btnCatalogo.href = "../catalogo-contratos/catalogo-contratos.html";
    btnCatalogo.prepend(icono("catalogo", 15));
    barra.append(
      btnCatalogo,
      badgeEstado(estadoKyc.estado_global, "KYC: " + estadoKyc.estado_global)
    );
    f.append(barra);

    const cargaId = params.get("carga");
    if (cargaId) {
      const carga = cargas.find((c) => c.id === cargaId);
      const barraVolver = nodo("div", null, "acciones-barra");
      barraVolver.append(enlace("← Volver a cargas disponibles", "subastas"));
      f.append(barraVolver);

      if (!carga) {
        f.append(estadoVacio("La carga seleccionada ya no está disponible."));
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
          [
            "Peso / Capacidad",
            nodo("span", carga.peso_total + " KG / " + carga.input_camionKG + " KG", "num-tabular"),
          ],
          [
            "Distancia",
            carga.distancia_km != null ? carga.distancia_km + " km" : "Estimada 150 km",
          ],
          [
            "Monto referencial",
            nodo("span", formatearMoneda(carga.monto_total, carga.moneda), "num-tabular"),
          ],
          [
            "Cierre de postulaciones",
            nodo("span", fechaLocal(carga.f_cierre_postulaciones), "num-tabular"),
          ],
          ["Salida estimada", nodo("span", fechaLocal(carga.f_estimada_salida), "num-tabular")],
          ["Llegada estimada", nodo("span", fechaLocal(carga.f_estimada_llegada), "num-tabular")],
          ["Requisitos especiales", requisitos.length ? requisitos.join(" · ") : "Ninguno"],
        ])
      );

      const aprobado = estadoKyc.estado_global === "APROBADO";
      if (!aprobado) {
        const alerta = nodo("div", null, "aviso-banner aviso-info");
        alerta.style.marginBottom = "14px";
        const cuerpoAlerta = nodo("div", null, "aviso-banner-contenido");
        cuerpoAlerta.append(
          icono("alerta", 17),
          nodo(
            "span",
            "Tu documentación aún no está en estado APROBADO (" +
              estadoKyc.estado_global +
              "). Completa tus documentos para poder postular."
          )
        );
        alerta.append(cuerpoAlerta, enlace("Ir a Documentación", "onboarding"));
        f.append(alerta);
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
    const formFiltros = nodo("form", null, "barra-filtros");
    const tituloFiltros = nodo("p", null, "barra-filtros-titulo");
    tituloFiltros.append(icono("filtro", 14), nodo("span", "Filtrar cargas disponibles"));
    const gridFiltros = nodo("div", null, "barra-filtros-grid");

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

    gridFiltros.append(lRegion, lTipo, lDist);

    const accionesFiltros = nodo("div", null, "barra-filtros-acciones");
    const btnBuscar = nodo("button", "Buscar", "btn-primario");
    btnBuscar.type = "submit";
    accionesFiltros.append(btnBuscar, enlace("Limpiar", "subastas"));

    formFiltros.append(tituloFiltros, gridFiltros, accionesFiltros);
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
        estadoVacio(
          "No hay cargas disponibles que coincidan con los filtros actuales.",
          consulta.toString() ? enlace("Limpiar filtros", "subastas") : null
        )
      );
      return f;
    }

    const lista = nodo("div", null, "lista-tarjetas");
    for (const c of cargas) {
      const card = nodo("article", null, "tarjeta-carga");
      const top = nodo("div", null, "tarjeta-carga-top");
      top.append(
        badgeEstado(c.estado),
        nodo("span", formatearMoneda(c.monto_total, c.moneda), "monto-destacado num-tabular")
      );
      const meta = nodo("div", null, "meta-linea");
      meta.append(
        nodo("span", "Carga: " + c.tipo_carga),
        nodo("span", c.peso_total + " / " + c.input_camionKG + " KG", "num-tabular"),
        nodo("span", "Cierre: " + fechaLocal(c.f_cierre_postulaciones), "num-tabular")
      );

      card.append(top, nodo("h3", c.origen + " → " + c.destino), meta);

      const chips = obtenerChipsRequisitos(c);
      if (chips.length) {
        const chipsWrap = nodo("div", null, "chips-requisitos");
        for (const ch of chips) chipsWrap.append(nodo("span", ch, "chip-requisito"));
        card.append(chipsWrap);
      }

      const btnPostular = enlace("Ver detalle y postular", "subastas", { carga: c.id });
      btnPostular.classList.add("btn-primario");
      card.append(btnPostular);
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
        "subtitulo-seccion"
      )
    );

    async function avanzarEstado(contratoId, nuevoEstado, confirmacion) {
      if (confirmacion) {
        const ok = await confirmarAccion(confirmacion);
        if (!ok) return;
      }
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
              boton(
                "Iniciar tránsito",
                () =>
                  avanzarEstado(c.id, "EN_TRANSITO", {
                    titulo: "Confirmar inicio de tránsito",
                    descripcion:
                      "El despacho " +
                      c.origen +
                      " → " +
                      c.destino +
                      " pasará a estado EN_TRANSITO.",
                    textoConfirmar: "Iniciar tránsito",
                    variante: "btn-primario",
                  }),
                "btn-primario btn-sm"
              )
            );
          } else if (c.estado === "EN_TRANSITO") {
            acciones.append(
              boton(
                "Confirmar entrega",
                () =>
                  avanzarEstado(c.id, "ENTREGADO", {
                    titulo: "Confirmar entrega en destino",
                    descripcion:
                      "Registrarás la entrega definitiva de la carga en " +
                      c.destino +
                      " para que el dador pueda finalizar el contrato.",
                    textoConfirmar: "Confirmar entrega",
                    variante: "btn-exito",
                  }),
                "btn-exito btn-sm"
              ),
              boton(
                "Reportar disputa",
                () =>
                  avanzarEstado(c.id, "EN_DISPUTA", {
                    titulo: "Reportar incidencia o disputa",
                    descripcion:
                      "El contrato pasará a estado EN_DISPUTA y se detendrá el cierre normal hasta su resolución.",
                    textoConfirmar: "Reportar disputa",
                    variante: "btn-peligro-solido",
                  }),
                "peligro btn-sm"
              )
            );
          } else {
            acciones.append(nodo("span", "Sin acciones pendientes", "texto-suave"));
          }
          return [
            c.origen + " → " + c.destino,
            c.tipo_carga,
            nodo("span", fechaLocal(c.f_estimada_salida), "num-tabular"),
            nodo("span", formatearMoneda(c.monto_total, c.moneda), "num-tabular"),
            badgeEstado(c.estado),
            acciones,
          ];
        }),
        "Aún no tienes contratos adjudicados asignados a tu cuenta.",
        enlace("Explorar cargas disponibles", "subastas")
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

  window.PanelVistas.transportista = vistaTransportista;
})();
