/* Prueba de las páginas que carga Electron, con el backend real y una base temporal. */
const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const { pathToFileURL } = require("node:url");
const { spawn } = require("node:child_process");
const { setTimeout: pausa } = require("node:timers/promises");
const { chromium } = require("playwright");

const raiz = path.resolve(__dirname, "../..");
const temporal = fs.mkdtempSync(path.join(os.tmpdir(), "camiones-panel-"));
let servidor, navegador;

async function iniciarApi() {
  // El propio servidor reserva un puerto libre para evitar interferir con la aplicación.
  servidor = spawn(
    process.env.PYTHON || "python",
    [
      "-u",
      "-c",
      "import socket,uvicorn; s=socket.socket(); s.bind(('127.0.0.1',0)); print(s.getsockname()[1],flush=True); uvicorn.Server(uvicorn.Config('main:app',log_level='error')).run(sockets=[s])",
    ],
    {
      cwd: raiz,
      windowsHide: true,
      env: { ...process.env, SQLITE_DB_PATH: path.join(temporal, "prueba.db") },
    }
  );
  servidor.stderr.pipe(process.stderr);
  const puerto = await new Promise((resolve, reject) => {
    servidor.once("error", reject);
    servidor.once("exit", () => reject(Error("FastAPI terminó al iniciar.")));
    servidor.stdout.once("data", (data) => resolve(Number(data.toString().trim())));
  });
  const api = "http://127.0.0.1:" + puerto;
  for (let i = 0; i < 100; i++) {
    try {
      if ((await fetch(api + "/openapi.json")).ok) return api;
    } catch {}
    await pausa(50);
  }
  throw Error("FastAPI no inició.");
}

async function probar() {
  const api = await iniciarApi();
  navegador = await chromium.launch({ channel: process.env.PANEL_BROWSER || "msedge" });
  const pagina = await navegador.newPage({ viewport: { width: 980, height: 680 } });
  pagina.setDefaultTimeout(8000);
  await pagina.addInitScript((url) => {
    window.API_BASE_URL = url;
  }, api);
  await pagina.goto(
    pathToFileURL(path.join(raiz, "frontend/codigos/paginas/Login/index.html")).href
  );
  async function login(correo, clave) {
    await pagina.locator("#email").fill(correo);
    await pagina.locator("#password").fill(clave);
    await pagina.locator("#btnLogin").click();
    await pagina.locator("nav [aria-current=page]").waitFor();
  }
  await login("admin@camiones.cl", "admin123");
  await pagina.getByRole("heading", { name: "Panel de administración" }).waitFor();
  assert.equal(await pagina.locator("nav a").count(), 6);
  await pagina.locator(".indicador").first().waitFor();
  assert.deepEqual(await pagina.locator(".indicador").allTextContents(), ["0", "5", "0"]);

  // Verificar nuevas vistas administrativas: Validaciones KYC y Configuración global.
  await pagina
    .locator("nav")
    .getByRole("link", { name: /Validaciones KYC/ })
    .click();
  await pagina.getByRole("heading", { name: /Documentos de transportistas pendientes/ }).waitFor();
  await pagina
    .locator("nav")
    .getByRole("link", { name: /Configuración/ })
    .click();
  await pagina.getByRole("button", { name: "Guardar configuración" }).click();
  await pagina.getByText("Configuración global actualizada correctamente.").waitFor();
  await pagina
    .locator("nav")
    .getByRole("link", { name: /Inicio/ })
    .click();
  await pagina.locator(".indicador").first().waitFor();
  await pagina.getByRole("link", { name: /Cuentas activas/ }).click();
  await pagina
    .getByRole("row")
    .filter({ hasText: "Administrador Backoffice" })
    .getByRole("link")
    .click();
  await pagina.getByText(/Las cuentas administrativas están protegidas/).waitFor();
  assert.equal(
    await pagina.getByRole("button", { name: "Eliminar cuenta", exact: true }).count(),
    0
  );
  await pagina.goBack();
  await pagina.getByRole("row").filter({ hasText: "Carlos Soto" }).getByRole("link").click();
  const eliminar = pagina.getByRole("button", { name: "Eliminar cuenta", exact: true });
  await eliminar.click();
  await pagina.getByRole("button", { name: "Volver", exact: true }).click();
  await eliminar.click();
  await pagina.getByLabel("Motivo de la eliminación").fill("Baja solicitada de prueba");
  await pagina.getByRole("button", { name: "Confirmar eliminación" }).click();
  await pagina.getByText("Eliminación registrada correctamente.").waitFor();
  await pagina.getByRole("link", { name: "Consultar historial del elemento" }).click();
  await pagina.getByRole("row").filter({ hasText: "Completado" }).getByRole("link").click();
  await pagina.getByText("Baja solicitada de prueba", { exact: true }).waitFor();
  // Usar la API real para preparar una convocatoria en la base temporal.
  const identidad = await pagina.request.post(api + "/auth/login", {
    data: { email: "contacto@logisticasur.cl", password: "dador123" },
  });
  const dador = await identidad.json();
  const headers = { Authorization: "Bearer " + dador.access_token };
  const fecha = (horas) => new Date(Date.now() + horas * 3600000).toISOString();
  const creada = await pagina.request.post(api + "/contratos", {
    headers,
    data: {
      id_empresa_generadora: dador.id,
      origen: "Santiago",
      destino: "Talca",
      f_cierre_postulaciones: fecha(3),
      f_estimada_salida: fecha(6),
      f_estimada_llegada: fecha(14),
      input_camionKG: 10000,
      tipo_carga: "GENERAL",
      peso_total: 5000,
      moneda: "CLP",
      monto_neto: 100000,
      monto_iva: 19000,
      monto_total: 119000,
    },
  });
  assert.equal(creada.status(), 201, await creada.text());
  const contrato = await creada.json();
  const publicada = await pagina.request.patch(api + "/contratos/" + contrato.id + "/estado", {
    headers,
    data: { nuevo_estado: "PUBLICADO" },
  });
  assert.equal(publicada.status(), 200, await publicada.text());
  await pagina
    .locator("nav")
    .getByRole("link", { name: /Gestión de contratos/ })
    .click();
  await pagina.getByRole("row").filter({ hasText: contrato.id }).getByRole("link").click();
  // Volver desde la confirmación de baja conserva la publicación y sus dos acciones.
  await pagina.getByRole("button", { name: "Eliminar contrato", exact: true }).click();
  await pagina.getByLabel("Motivo de la eliminación").waitFor();
  await pagina.getByRole("button", { name: "Volver", exact: true }).click();
  await pagina.getByRole("button", { name: "Cancelar contrato", exact: true }).click();
  await pagina.getByLabel("Motivo de la cancelación").fill("Retiro del flete");
  await pagina.getByRole("button", { name: "Confirmar cancelación" }).click();
  await pagina.getByText("Cancelación registrada correctamente.").waitFor();
  await pagina.getByText("CANCELADO", { exact: true }).waitFor();
  assert.equal(
    await pagina.getByRole("button", { name: "Cancelar contrato", exact: true }).count(),
    0
  );
  await pagina.getByRole("link", { name: "Consultar historial del elemento" }).click();
  await pagina.getByRole("row").filter({ hasText: "Cancelar contrato" }).getByRole("link").click();
  await pagina.getByText("Retiro del flete", { exact: true }).waitFor();
  await pagina.setViewportSize({ width: 520, height: 680 });
  const menu = pagina.getByRole("button", { name: /Menú/ });
  await menu.focus();
  await menu.press("Enter");
  assert.equal(await menu.getAttribute("aria-expanded"), "true");
  await pagina.getByRole("button", { name: "Cerrar sesión" }).click();
  await pagina.setViewportSize({ width: 980, height: 680 });
  // Crear un segundo contrato publicado para probar el flujo de Dador y Transportista.
  const creada2 = await pagina.request.post(api + "/contratos", {
    headers,
    data: {
      id_empresa_generadora: dador.id,
      origen: "Valparaíso",
      destino: "Concepción",
      f_cierre_postulaciones: fecha(3),
      f_estimada_salida: fecha(6),
      f_estimada_llegada: fecha(16),
      input_camionKG: 12000,
      tipo_carga: "GENERAL",
      peso_total: 6000,
      moneda: "CLP",
      monto_neto: 200000,
      monto_iva: 38000,
      monto_total: 238000,
    },
  });
  assert.equal(creada2.status(), 201, await creada2.text());
  const contratoSubasta = await creada2.json();
  const pub2 = await pagina.request.patch(api + "/contratos/" + contratoSubasta.id + "/estado", {
    headers,
    data: { nuevo_estado: "PUBLICADO" },
  });
  assert.equal(pub2.status(), 200, await pub2.text());

  for (const [correo, clave, acceso, extraRuta, extraTexto] of [
    [
      "contacto@logisticasur.cl",
      "dador123",
      "Registrar Contrato",
      /Perfil Tributario/,
      /perfil tributario/i,
    ],
    [
      "juan.perez@rutanorte.cl",
      "camion123",
      "Subastas y Cargas",
      /Documentación y Compliance/,
      /Progreso de validación/,
    ],
  ]) {
    await login(correo, clave);
    const nav = pagina.locator("nav");
    assert.ok((await nav.innerText()).includes(acceso));
    assert.equal(await nav.getByRole("link", { name: "Historial de acciones" }).count(), 0);
    await nav.getByRole("link", { name: extraRuta }).click();
    await pagina.getByText(extraTexto).first().waitFor();
    await nav.getByRole("link", { name: new RegExp(acceso) }).click();
    if (correo === "juan.perez@rutanorte.cl") {
      await pagina.getByRole("link", { name: "Ver detalle y postular" }).first().click();
      await pagina.getByRole("button", { name: "Enviar postulación" }).click();
      await pagina.getByText("¡Postulación enviada correctamente!").waitFor();
      await pagina.getByRole("link", { name: "← Volver a cargas disponibles" }).click();
    }
    await pagina.locator('main a[href="../Principal/principal.html"]').click();
    await pagina.locator("#boton-perfil").click();
    await pagina.locator('[data-accion-perfil="cerrar"]').click();
    await pagina.locator("#btnLogin").waitFor();
  }
  console.log(
    "OK: tres roles, resumen, KYC, configuración, subastas, baja, historial, menú con teclado y cierre de sesión."
  );
}
(async () => {
  try {
    await probar();
  } catch (error) {
    console.error(error);
    process.exitCode = 1;
  } finally {
    if (navegador) await navegador.close();
    if (servidor?.pid && servidor.exitCode === null) {
      const salida = new Promise((resolve) => servidor.once("exit", resolve));
      servidor.kill();
      await salida;
    }
    // El directorio proviene de mkdtemp y solo contiene nuestra base descartable.
    fs.rmSync(path.join(temporal, "prueba.db"), { force: true });
    fs.rmdirSync(temporal);
  }
})();
