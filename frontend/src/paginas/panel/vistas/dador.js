window.PanelVistas = window.PanelVistas || {};
(function () {
  /* Vistas operativas para el rol DADOR_CARGA dentro del panel unificado — MansoViaje */

  const ESTADOS_CONTRATO_DADOR = [
    "BORRADOR",
    "PUBLICADO",
    "EN_SUBASTA",
    "EN_POSTULACION",
    "ADJUDICADO",
    "EN_TRANSITO",
    "ENTREGADO",
    "FINALIZADO",
    "CANCELADO",
    "EN_DISPUTA",
  ];

  async function obtenerPerfilDadorOpcional() {
    try {
      return await api("/onboarding/dador/perfil", undefined, {
        headers: { "X-User-Id": usuario.id },
      });
    } catch {
      return null;
    }
  }

  async function inicioDador() {
    const [contratos, perfil] = await Promise.all([
      api("/contratos"),
      obtenerPerfilDadorOpcional(),
    ]);
    const propios = contratos.filter((c) => c.id_empresa_generadora === usuario.id);
    const enSubasta = propios.filter((c) =>
      ["PUBLICADO", "EN_SUBASTA", "EN_POSTULACION"].includes(c.estado)
    ).length;
    const activos = propios.filter((c) =>
      ["ADJUDICADO", "EN_TRANSITO", "ENTREGADO"].includes(c.estado)
    ).length;

    const f = document.createDocumentFragment();
    f.append(
      nodo(
        "p",
        "Administra tus contratos de transporte, supervisa postulaciones y mantén al día tu perfil tributario.",
        "subtitulo-seccion"
      )
    );

    const grid = nodo("div", null, "rejilla-kpi");
    for (const kpi of [
      {
        titulo: "Estado KYC tributario",
        valor: perfil ? perfil.estado_validacion : "SIN REGISTRAR",
        modulo: "tributario",
        iconoNombre: "validaciones",
        esEstado: true,
      },
      {
        titulo: "Mis contratos",
        valor: propios.length,
        modulo: "contratos",
        iconoNombre: "contratos",
      },
      {
        titulo: "En subasta / postulación",
        valor: enSubasta,
        modulo: "subastas",
        iconoNombre: "subastas",
      },
      {
        titulo: "Adjudicados / en curso",
        valor: activos,
        modulo: "contratos",
        iconoNombre: "seguimiento",
      },
    ]) {
      grid.append(tarjetaKpi(kpi));
    }

    f.append(grid, nodo("h2", "Accesos rápidos"), tarjetas(FUNCIONALIDADES_POR_ROL.DADOR_CARGA));
    return f;
  }

  async function cambiarEstadoContratoDador(contratoId, nuevoEstado, confirmacion = null) {
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
      mostrarAviso("Estado del contrato actualizado a " + nuevoEstado + ".", "exito");
    } catch (error) {
      mostrarAviso(error.message, "error");
    }
  }

  function accionesEstadoDador(contrato) {
    const grupo = nodo("div", null, "acciones-grupo");
    const confirmarCancelar = {
      titulo: "Cancelar contrato",
      descripcion:
        "El contrato pasará a estado CANCELADO (terminal) y dejará de aceptar postulaciones o avanzar en el flujo.",
      textoConfirmar: "Sí, cancelar contrato",
      variante: "btn-peligro-solido",
    };
    const confirmarFinalizar = {
      titulo: "Finalizar contrato",
      descripcion:
        "Confirmas la conformidad del servicio. El contrato pasará a estado FINALIZADO y no podrá modificarse.",
      textoConfirmar: "Finalizar contrato",
      variante: "btn-exito",
    };
    const confirmarDisputa = {
      titulo: "Abrir disputa",
      descripcion:
        "El contrato quedará marcado EN_DISPUTA para su revisión y resolución posterior.",
      textoConfirmar: "Abrir disputa",
      variante: "btn-peligro-solido",
    };

    if (contrato.estado === "BORRADOR") {
      grupo.append(
        boton(
          "Publicar",
          () => cambiarEstadoContratoDador(contrato.id, "PUBLICADO"),
          "btn-primario"
        ),
        boton("Abrir subasta", () => cambiarEstadoContratoDador(contrato.id, "EN_SUBASTA")),
        boton(
          "Cancelar",
          () => cambiarEstadoContratoDador(contrato.id, "CANCELADO", confirmarCancelar),
          "peligro"
        )
      );
    } else if (["PUBLICADO", "EN_SUBASTA", "EN_POSTULACION"].includes(contrato.estado)) {
      if (contrato.estado === "PUBLICADO") {
        grupo.append(
          boton("Abrir subasta", () => cambiarEstadoContratoDador(contrato.id, "EN_SUBASTA"))
        );
      }
      grupo.append(
        enlace("Ver postulaciones", "subastas", { contrato: contrato.id }),
        boton(
          "Cancelar",
          () => cambiarEstadoContratoDador(contrato.id, "CANCELADO", confirmarCancelar),
          "peligro"
        )
      );
    } else if (contrato.estado === "ENTREGADO") {
      grupo.append(
        boton(
          "Finalizar contrato",
          () => cambiarEstadoContratoDador(contrato.id, "FINALIZADO", confirmarFinalizar),
          "btn-exito"
        ),
        boton(
          "Abrir disputa",
          () => cambiarEstadoContratoDador(contrato.id, "EN_DISPUTA", confirmarDisputa),
          "peligro"
        )
      );
    } else if (contrato.estado === "EN_DISPUTA") {
      grupo.append(
        boton(
          "Finalizar contrato",
          () => cambiarEstadoContratoDador(contrato.id, "FINALIZADO", confirmarFinalizar),
          "btn-exito"
        ),
        boton(
          "Cancelar",
          () => cambiarEstadoContratoDador(contrato.id, "CANCELADO", confirmarCancelar),
          "peligro"
        )
      );
    }
    return grupo;
  }

  async function contratosDador(params) {
    const contratos = await api("/contratos");
    const propios = contratos.filter((c) => c.id_empresa_generadora === usuario.id);
    const detalleId = params.get("detalle");

    const f = document.createDocumentFragment();
    const barra = nodo("div", null, "acciones-barra");
    const links = nodo("div", null, "acciones-grupo");
    const btnCrear = nodo("a", "+ Nuevo contrato", "boton btn-primario");
    btnCrear.href = "../crear-contrato/crear-contrato.html?desde=panel";
    const btnCatalogo = nodo("a", "Abrir vista catálogo", "boton");
    btnCatalogo.href = "../catalogo-contratos/catalogo-contratos.html";
    btnCatalogo.prepend(icono("catalogo", 15));
    links.append(btnCrear, btnCatalogo);
    barra.append(links);
    f.append(barra);

    if (detalleId) {
      const c = propios.find((item) => item.id === detalleId);
      const barraVolver = nodo("div", null, "acciones-barra");
      barraVolver.append(enlace("← Volver a mis contratos", "contratos"));
      f.append(barraVolver);

      if (!c) {
        f.append(estadoVacio("No se encontró el contrato solicitado."));
        return f;
      }
      f.append(
        ficha([
          ["Identificador", celdaId(c.id)],
          ["Estado", badgeEstado(c.estado)],
          ["Ruta", c.origen + " → " + c.destino],
          ["Tipo de carga", c.tipo_carga],
          [
            "Peso / Capacidad",
            nodo("span", c.peso_total + " KG / " + c.input_camionKG + " KG", "num-tabular"),
          ],
          [
            "Cierre postulaciones",
            nodo("span", fechaLocal(c.f_cierre_postulaciones), "num-tabular"),
          ],
          ["Salida estimada", nodo("span", fechaLocal(c.f_estimada_salida), "num-tabular")],
          ["Llegada estimada", nodo("span", fechaLocal(c.f_estimada_llegada), "num-tabular")],
          ["Monto neto", nodo("span", formatearMoneda(c.monto_neto, c.moneda), "num-tabular")],
          ["IVA", nodo("span", formatearMoneda(c.monto_iva, c.moneda), "num-tabular")],
          ["Monto total", nodo("span", formatearMoneda(c.monto_total, c.moneda), "num-tabular")],
          [
            "Transportista asignado",
            c.id_transportista ? celdaId(c.id_transportista) : "Sin asignar",
          ],
        ]),
        accionesEstadoDador(c)
      );
      return f;
    }

    const estadoFiltro = params.get("estado") || "";
    const formFiltro = nodo("form", null, "barra-filtros");
    const tituloFiltro = nodo("p", null, "barra-filtros-titulo");
    tituloFiltro.append(icono("filtro", 14), nodo("span", "Filtrar mis contratos"));
    const gridFiltro = nodo("div", null, "barra-filtros-grid");

    const labelEstado = nodo("label", "Estado");
    const selEstado = nodo("select");
    selEstado.name = "estado";
    const optTodos = nodo("option", "Todos");
    optTodos.value = "";
    selEstado.append(optTodos);
    for (const est of ESTADOS_CONTRATO_DADOR) {
      const opt = nodo("option", est);
      opt.value = est;
      selEstado.append(opt);
    }
    selEstado.value = estadoFiltro;
    labelEstado.append(selEstado);
    gridFiltro.append(labelEstado);

    const accionesFiltro = nodo("div", null, "barra-filtros-acciones");
    const btnFiltrar = nodo("button", "Filtrar", "btn-primario");
    btnFiltrar.type = "submit";
    accionesFiltro.append(btnFiltrar, enlace("Limpiar", "contratos"));

    formFiltro.append(tituloFiltro, gridFiltro, accionesFiltro);
    formFiltro.onsubmit = (e) => {
      e.preventDefault();
      location.hash = selEstado.value ? "contratos?estado=" + selEstado.value : "contratos";
    };

    const filtrados = estadoFiltro ? propios.filter((c) => c.estado === estadoFiltro) : propios;
    const ctaNuevo = nodo("a", "+ Crear primer contrato", "boton btn-primario");
    ctaNuevo.href = "../crear-contrato/crear-contrato.html?desde=panel";

    f.append(
      formFiltro,
      tabla(
        ["Ruta", "Tipo carga", "Monto total", "Salida", "Estado", "Acciones"],
        filtrados.map((c) => [
          c.origen + " → " + c.destino,
          c.tipo_carga,
          nodo("span", formatearMoneda(c.monto_total, c.moneda), "num-tabular"),
          nodo("span", fechaLocal(c.f_estimada_salida), "num-tabular"),
          badgeEstado(c.estado),
          enlace("Gestionar", "contratos", { detalle: c.id }),
        ]),
        "Aún no tienes contratos registrados con este filtro.",
        estadoFiltro ? enlace("Ver todos mis contratos", "contratos") : ctaNuevo
      )
    );
    return f;
  }

  async function subastasDador(params) {
    const contratos = await api("/contratos");
    const subastables = contratos.filter(
      (c) =>
        c.id_empresa_generadora === usuario.id &&
        ["PUBLICADO", "EN_SUBASTA", "EN_POSTULACION", "ADJUDICADO"].includes(c.estado)
    );
    const f = document.createDocumentFragment();
    const seleccionadoId = params.get("contrato");

    if (seleccionadoId) {
      const contrato = subastables.find((c) => c.id === seleccionadoId);
      const barra = nodo("div", null, "acciones-barra");
      barra.append(enlace("← Volver a mis subastas", "subastas"));
      f.append(barra);

      if (!contrato) {
        f.append(estadoVacio("No se encontró la subasta solicitada."));
        return f;
      }

      const postulaciones = await api("/subastas/cargas/" + contrato.id + "/postulaciones");
      f.append(
        nodo("h2", contrato.origen + " → " + contrato.destino),
        ficha([
          ["Estado", badgeEstado(contrato.estado)],
          [
            "Monto referencial",
            nodo("span", formatearMoneda(contrato.monto_total, contrato.moneda), "num-tabular"),
          ],
          [
            "Cierre postulaciones",
            nodo("span", fechaLocal(contrato.f_cierre_postulaciones), "num-tabular"),
          ],
          ["Postulaciones recibidas", nodo("span", String(postulaciones.length), "num-tabular")],
        ])
      );

      async function adjudicar(postulacion) {
        const ok = await confirmarAccion({
          titulo: "Confirmar adjudicación",
          descripcion:
            "Adjudicarás esta carga por " +
            formatearMoneda(postulacion.precio_oferta, "CLP") +
            " (" +
            postulacion.tiempo_entrega_horas +
            " h). Las demás postulaciones pasarán automáticamente a RECHAZADA.",
          textoConfirmar: "Adjudicar oferta",
          variante: "btn-exito",
        });
        if (!ok) return;

        try {
          await api("/subastas/adjudicar", {
            carga_id: contrato.id,
            postulacion_id: postulacion.id,
          });
          await navegar();
          mostrarAviso("Subasta adjudicada correctamente.", "exito");
        } catch (error) {
          mostrarAviso(error.message, "error");
        }
      }

      const adjudicable = ["PUBLICADO", "EN_SUBASTA", "EN_POSTULACION"].includes(contrato.estado);
      f.append(
        nodo("h2", "Ofertas recibidas"),
        tabla(
          ["Transportista ID", "Oferta", "Tiempo entrega", "Comentario", "Estado", "Acción"],
          postulaciones.map((p) => [
            celdaId(p.transportista_id),
            nodo("span", formatearMoneda(p.precio_oferta, "CLP"), "num-tabular"),
            nodo("span", p.tiempo_entrega_horas + " h", "num-tabular"),
            p.comentario || "—",
            badgeEstado(p.estado),
            adjudicable && p.estado === "POSTULADA"
              ? boton("Adjudicar oferta", () => adjudicar(p), "btn-exito btn-sm")
              : "—",
          ]),
          "Aún no se han recibido postulaciones para esta carga."
        )
      );
      return f;
    }

    f.append(
      nodo(
        "p",
        "Selecciona uno de tus contratos publicados o en subasta para revisar ofertas y adjudicar al transportista ganador.",
        "subtitulo-seccion"
      ),
      tabla(
        ["Ruta", "Tipo carga", "Monto total", "Cierre postulaciones", "Estado", "Ofertas"],
        subastables.map((c) => [
          c.origen + " → " + c.destino,
          c.tipo_carga,
          nodo("span", formatearMoneda(c.monto_total, c.moneda), "num-tabular"),
          nodo("span", fechaLocal(c.f_cierre_postulaciones), "num-tabular"),
          badgeEstado(c.estado),
          enlace("Revisar ofertas", "subastas", { contrato: c.id }),
        ]),
        "No tienes cargas en subasta o publicadas actualmente. Crea o publica un contrato desde Mis Contratos.",
        enlace("Ir a Mis Contratos", "contratos")
      )
    );
    return f;
  }

  async function tributarioDador() {
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
        perfil?.datos_facturacion?.correo_facturacion || usuario.email || "",
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
          { method: "POST", headers: { "X-User-Id": usuario.id } }
        );
        await navegar();
        mostrarAviso(
          "Perfil tributario guardado. Estado actual: PENDIENTE de validación.",
          "exito"
        );
      } catch (error) {
        mostrarAviso(error.message, "error");
      } finally {
        btnGuardar.disabled = false;
      }
    };

    f.append(form);
    return f;
  }

  async function vistaDador(ruta, params) {
    if (ruta === "inicio") return inicioDador();
    if (ruta === "contratos") return contratosDador(params);
    if (ruta === "subastas") return subastasDador(params);
    if (ruta === "tributario") return tributarioDador();
    return inicioDador();
  }

  window.PanelVistas.dador = vistaDador;
})();
