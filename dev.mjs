import { spawn, spawnSync } from "node:child_process";
import fs from "node:fs";
import http from "node:http";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { resolvePythonExecutable } from "./scripts/run-py.mjs";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const isWindows = process.platform === "win32";

const BACKEND_HOST = "127.0.0.1";
const BACKEND_PORT = 8000;
const HEALTH_URL = `http://${BACKEND_HOST}:${BACKEND_PORT}/openapi.json`;

/**
 * Termina un proceso y todo su árbol de procesos hijos.
 */
function killProcessTree(child) {
  if (!child || child.killed || child.exitCode !== null) {
    return;
  }
  if (isWindows && child.pid) {
    spawnSync("taskkill", ["/pid", String(child.pid), "/T", "/F"], {
      stdio: "ignore",
    });
  } else {
    child.kill("SIGTERM");
  }
}

/**
 * Espera a que el servidor FastAPI responda antes de abrir Electron.
 */
function waitForBackend(url, backendProcess, timeoutMs = 30000) {
  const startTime = Date.now();

  return new Promise((resolve, reject) => {
    const check = () => {
      if (backendProcess.exitCode !== null) {
        reject(
          new Error(
            `El backend se detuvo inesperadamente (código ${backendProcess.exitCode}).`
          )
        );
        return;
      }

      const req = http.get(url, (res) => {
        res.resume();
        if (res.statusCode && res.statusCode < 500) {
          resolve();
        } else {
          retry();
        }
      });

      req.on("error", retry);
      req.setTimeout(1000, () => {
        req.destroy();
        retry();
      });
    };

    const retry = () => {
      if (Date.now() - startTime >= timeoutMs) {
        reject(
          new Error(
            `Tiempo de espera agotado (${timeoutMs}ms) esperando al backend en ${url}.`
          )
        );
        return;
      }
      setTimeout(check, 300);
    };

    check();
  });
}

async function main() {
  const frontendDir = path.join(__dirname, "frontend");
  const frontendModules = path.join(frontendDir, "node_modules");

  if (!fs.existsSync(frontendModules)) {
    console.log("Instalando dependencias del frontend...");
    const installResult = spawnSync("npm", ["--prefix", "frontend", "install"], {
      cwd: __dirname,
      stdio: "inherit",
      shell: isWindows,
    });
    if (installResult.status !== 0) {
      process.exit(installResult.status ?? 1);
    }
  }

  const pythonExe = resolvePythonExecutable();
  console.log(`Iniciando backend FastAPI con: ${pythonExe}`);

  const backend = spawn(
    pythonExe,
    [
      "-m",
      "uvicorn",
      "main:app",
      "--reload",
      "--reload-exclude",
      ".venv",
      "--reload-exclude",
      "frontend/node_modules",
      "--host",
      BACKEND_HOST,
      "--port",
      String(BACKEND_PORT),
    ],
    {
      cwd: __dirname,
      stdio: "inherit",
    }
  );

  let frontend = null;
  let shuttingDown = false;

  const shutdown = (exitCode = 0) => {
    if (shuttingDown) {
      return;
    }
    shuttingDown = true;
    killProcessTree(frontend);
    killProcessTree(backend);
    process.exit(exitCode);
  };

  process.on("SIGINT", () => shutdown(0));
  process.on("SIGTERM", () => shutdown(0));

  backend.on("exit", (code) => {
    if (!shuttingDown) {
      console.error(`Backend finalizado (código ${code ?? 0}).`);
      shutdown(code ?? 0);
    }
  });

  try {
    await waitForBackend(HEALTH_URL, backend);
  } catch (err) {
    console.error(err.message);
    shutdown(1);
    return;
  }

  console.log("Backend listo. Compilando e iniciando frontend (Electron)...");
  frontend = spawn("npm", ["--prefix", "frontend", "start"], {
    cwd: __dirname,
    stdio: "inherit",
    shell: isWindows,
  });

  frontend.on("exit", (code) => {
    if (!shuttingDown) {
      console.log("Frontend cerrado. Deteniendo backend...");
      shutdown(code ?? 0);
    }
  });
}

main();
