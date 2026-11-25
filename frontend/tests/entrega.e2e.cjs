/* Aceptación del ejecutable instalado. Requiere Windows, el puerto 8000 libre
 * y las dependencias de pruebas del frontend en la máquina que automatiza. */
const assert = require("node:assert/strict");
const fs = require("node:fs");
const http = require("node:http");
const os = require("node:os");
const path = require("node:path");
const { once } = require("node:events");
const { _electron: electron } = require("playwright");

const api = "http://127.0.0.1:8000";
const cuentas = {
  dador: ["contacto@logisticasur.cl", "dador123"],
  transportista: ["juan.perez@rutanorte.cl", "camion123"],
};

async function entrar(pagina, rol) {
  const [email, password] = cuentas[rol];
  await pagina.locator("#email").fill(email);
  await pagina.locator("#password").fill(password);
  await pagina.locator("#btnLogin").click();
  await pagina.locator("nav [aria-current=page]").waitFor();
}

async function salir(pagina) {
  await pagina.getByRole("button", { name: "Cerrar sesión" }).click();
  await pagina.locator("#btnLogin").waitFor();
}

async function publicar(pagina) {
  await pagina
    .locator("nav")
    .getByRole("link", { name: /Registrar Contrato/ })
    .click();
  await pagina.getByRole("link", { name: "+ Nuevo contrato" }).click();
  await pagina.getByText("KYC Aprobado", { exact: true }).waitFor();
  await pagina.locator("#origen").fill("Valparaíso");
  await pagina.locator("#destino").fill("Concepción");
  await pagina.locator("#tipo_carga").selectOption("GENERAL");
  await pagina.locator("#input_camionKG").fill("12000");
  await pagina.locator("#peso_total").fill("6000");
  await pagina.locator("#monto_neto").fill("200000");
  const [respuesta] = await Promise.all([
    pagina.waitForResponse((r) => r.request().method() === "PATCH" && r.url().endsWith("/estado")),
    pagina.locator("#btn-crear-publicar").click(),
  ]);
  assert.equal(respuesta.status(), 200);
  const contrato = await respuesta.json();
  assert.equal(contrato.estado, "PUBLICADO");
  await pagina.locator("#resultado-detalle").filter({ hasText: contrato.id }).waitFor();
  await pagina.locator("#enlace-resultado-volver").click();
  await salir(pagina);
  return contrato;
}

async function revisarComoDador(pagina, contrato, oferta) {
  await entrar(pagina, "dador");
  await pagina
    .locator("nav")
    .getByRole("link", { name: /Gestión de Subastas/ })
    .click();
  const [respuesta] = await Promise.all([
    pagina.waitForResponse((r) => r.url().endsWith("/" + contrato.id + "/postulaciones")),
    pagina.getByRole("link", { name: "Revisar ofertas" }).click(),
  ]);
  assert.equal(respuesta.status(), 200);
  assert.deepEqual(await respuesta.json(), [oferta]);
  await pagina.getByText("EN_POSTULACION", { exact: true }).waitFor();
  await pagina
    .getByRole("row")
    .filter({ hasText: "POSTULADA" })
    .filter({ hasText: /180.000/ })
    .waitFor();
  await salir(pagina);
}

async function postular(pagina, contrato) {
  // Un segundo login de dador permite lecturas independientes mientras la UI opera como transportista.
  const identidad = await pagina.request.post(api + "/auth/login", {
    data: { email: cuentas.dador[0], password: cuentas.dador[1] },
  });
  assert.equal(identidad.status(), 200);
  const headers = { Authorization: "Bearer " + (await identidad.json()).access_token };
  async function leer(ruta) {
    const respuesta = await pagina.request.get(api + ruta, { headers });
    assert.equal(respuesta.status(), 200);
    return respuesta.json();
  }
  const urlContrato = "/contratos/" + contrato.id;
  const urlOfertas = "/subastas/cargas/" + contrato.id + "/postulaciones";
  const original = await leer(urlContrato);
  assert.equal(original.estado, "PUBLICADO");
  assert.deepEqual(await leer(urlOfertas), []);

  await entrar(pagina, "transportista");
  await pagina
    .locator("nav")
    .getByRole("link", { name: /Subastas y Cargas/ })
    .click();
  await pagina.locator('a[href*="' + contrato.id + '"]').click();
  const tarifa = pagina.getByLabel(/Tarifa ofertada/);
  const enviar = pagina.getByRole("button", { name: "Enviar postulación" });
  await tarifa.fill("4900");
  await enviar.click();
  assert.equal(await tarifa.evaluate((input) => input.validity.rangeUnderflow), true);

  // La validación HTML bloquea el envío anterior. Desactivamos solo ese límite
  // en este formulario de prueba para observar la validación real del servidor.
  await tarifa.evaluate((input) => input.removeAttribute("min"));
  const respondePostulacion = (r) =>
    r.request().method() === "POST" && new URL(r.url()).pathname === "/subastas/postular";
  const [invalida] = await Promise.all([
    pagina.waitForResponse(respondePostulacion),
    enviar.click(),
  ]);
  assert.equal(invalida.status(), 422);
  await pagina.locator("#aviso.aviso-error").filter({ hasText: /5000/ }).waitFor();
  assert.deepEqual(await leer(urlContrato), original);
  assert.deepEqual(await leer(urlOfertas), []);
  console.log(
    "Inválido: 4900 CLP bloqueados por HTML. FastAPI respondió 422 al envío controlado; Electron mostró el límite. Contrato intacto y cero ofertas."
  );

  await tarifa.fill("180000");
  await pagina.getByLabel(/Tiempo estimado de entrega/).fill("6");
  const [valida] = await Promise.all([pagina.waitForResponse(respondePostulacion), enviar.click()]);
  assert.equal(valida.status(), 201);
  const oferta = await valida.json();
  assert.equal(oferta.precio_oferta, 180000);
  assert.equal(oferta.tiempo_entrega_horas, 6);
  assert.equal(oferta.carga_id, contrato.id);
  assert.equal(oferta.estado, "POSTULADA");
  await pagina.getByText("¡Postulación enviada correctamente!").waitFor();
  assert.equal((await leer(urlContrato)).estado, "EN_POSTULACION");
  await salir(pagina);
  return oferta;
}

async function ocuparPuerto() {
  const servidor = http.createServer((req, res) => {
    res.writeHead(503, { Connection: "close" });
    res.end();
  });
  await new Promise((resolve, reject) => {
    servidor.once("error", reject);
    servidor.listen(8000, "127.0.0.1", resolve);
  });
  return servidor;
}

async function probar(executablePath) {
  assert.ok(fs.statSync(executablePath).isFile(), "Indica el ejecutable instalado.");
  const perfil = fs.mkdtempSync(path.join(os.tmpdir(), "mansoviaje-entrega-"));
  console.log("Perfil de aceptación:", perfil);
  let aplicacion;
  let conflicto;
  async function abrir() {
    aplicacion = await electron.launch({
      executablePath,
      cwd: perfil,
      env: { ...process.env, MANSOVIAJE_DATA_DIR: perfil },
      args: ["--user-data-dir=" + perfil],
      timeout: 60000,
    });
    const ruta = await aplicacion.evaluate(({ app }) => app.getPath("userData"));
    assert.equal(path.resolve(ruta), perfil, "El perfil debe estar aislado.");
    const pagina = await aplicacion.firstWindow();
    pagina.setDefaultTimeout(45000);
    return pagina;
  }
  async function cerrar() {
    const proceso = aplicacion.process();
    const salida = once(proceso, "exit");
    await aplicacion.close();
    await salida;
    aplicacion = undefined;
  }

  try {
    // Una reserva inicial fallará sin iniciar la aplicación si alguien ya usa el puerto.
    conflicto = await ocuparPuerto();
    await new Promise((resolve) => conflicto.close(resolve));
    conflicto = undefined;
    let pagina = await abrir();
    await entrar(pagina, "dador");
    const contrato = await publicar(pagina);
    const oferta = await postular(pagina, contrato);
    await revisarComoDador(pagina, contrato, oferta);
    console.log(
      "Válido: POST 201, oferta",
      oferta.id,
      "por 180000 CLP y contrato",
      contrato.id,
      "EN_POSTULACION, visibles para el dador."
    );
    await cerrar();
    assert.ok(fs.statSync(path.join(perfil, "camiones.db")).size > 0);

    conflicto = await ocuparPuerto();
    pagina = await abrir();
    await pagina.getByRole("heading", { name: "No se pudo conectar con MansoViaje" }).waitFor();
    console.log(
      "Recurso ausente: backend indisponible al ocupar el puerto; Electron mostró el error de conexión."
    );
    await new Promise((resolve) => conflicto.close(resolve));
    conflicto = undefined;
    await pagina.getByRole("button", { name: "Reintentar" }).click();
    await revisarComoDador(pagina, contrato, oferta);
    console.log(
      "Reinicio: Electron recuperó el servicio tras Reintentar. Misma oferta, mismo contrato y estado."
    );
    await cerrar();
    conflicto = await ocuparPuerto();
    console.log("Cierre: puerto 8000 libre tras salir.");
  } finally {
    if (conflicto) await new Promise((resolve) => conflicto.close(resolve));
    if (aplicacion) await cerrar();
    // Conservar los datos de la prueba facilita comprobar el resultado SQLite y el log.
  }
}

if (!process.argv[2]) {
  console.error("Uso: node frontend/tests/entrega.e2e.cjs <ruta al MansoViaje.exe instalado>");
  process.exitCode = 2;
} else {
  probar(path.resolve(process.argv[2])).catch((error) => {
    console.error(error);
    process.exitCode = 1;
  });
}
