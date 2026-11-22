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
  await pagina.goto(pathToFileURL(path.join(raiz, "frontend/codigos/paginas/Login/index.html")).href);
  async function login(correo, clave) {
    await pagina.locator("#email").fill(correo);
    await pagina.locator("#password").fill(clave);
    await pagina.locator("#btnLogin").click();
    await pagina.locator("nav [aria-current=page]").waitFor();
  }
  await login("admin@camiones.cl", "admin123");
  await pagina.getByRole("heading", { name: "Panel de administración" }).waitFor();
  assert.equal(await pagina.locator("nav a").count(), 4);
  await pagina.locator(".indicador").first().waitFor();
  assert.deepEqual(await pagina.locator(".indicador").allTextContents(), ["0", "5", "0"]);
  await pagina.getByRole("link", { name: /Cuentas activas/ }).click();
  await pagina.getByRole("row").filter({ hasText: "Administrador Backoffice" }).getByRole("link").click();
  await pagina.getByText(/Las cuentas administrativas están protegidas/).waitFor();
  assert.equal(await pagina.getByRole("button", { name: "Eliminar cuenta", exact: true }).count(), 0);
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
  await pagina.setViewportSize({ width: 520, height: 680 });
  const menu = pagina.getByRole("button", { name: /Menú/ });
  await menu.focus();
  await menu.press("Enter");
  assert.equal(await menu.getAttribute("aria-expanded"), "true");
  await pagina.getByRole("button", { name: "Cerrar sesión" }).click();
  await pagina.setViewportSize({ width: 980, height: 680 });
  for (const [correo, clave, acceso] of [
    ["contacto@logisticasur.cl", "dador123", "Registrar Contrato"],
    ["juan.perez@rutanorte.cl", "camion123", "Subastas y Cargas"],
  ]) {
    await login(correo, clave);
    const nav = pagina.locator("nav");
    assert.ok((await nav.innerText()).includes(acceso));
    assert.equal(await nav.getByRole("link", { name: "Historial de acciones" }).count(), 0);
    await nav.getByRole("link", { name: new RegExp(acceso) }).click();
    await pagina.locator('main a[href="../Principal/principal.html"]').click();
    await pagina.locator("#boton-perfil").click();
    await pagina.locator('[data-accion-perfil="cerrar"]').click();
    await pagina.locator("#btnLogin").waitFor();
  }
  console.log("OK: tres roles, resumen, baja, historial, menú con teclado y cierre de sesión.");
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
