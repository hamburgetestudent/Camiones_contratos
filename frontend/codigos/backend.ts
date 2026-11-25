import { spawn, type ChildProcess } from "node:child_process";
import { randomUUID } from "node:crypto";
import { closeSync, openSync } from "node:fs";
import path from "node:path";
import { setTimeout as delay } from "node:timers/promises";

export function launchBackend(
  executable: string,
  userData: string,
  version: string,
  onStopped: (reason: string) => void
) {
  const instance = randomUUID();
  const logPath = path.join(userData, "backend.log");
  const log = openSync(logPath, "w");
  let child: ChildProcess;
  try {
    child = spawn(executable, [], {
      cwd: userData,
      windowsHide: true,
      stdio: ["pipe", log, log],
      env: {
        ...process.env,
        MV_INSTANCE_ID: instance,
        SQLITE_DB_PATH: path.join(userData, "camiones.db"),
      },
    });
  } finally {
    closeSync(log);
  }
  let stopping = false;
  let ready = false;
  let failure = "";
  child.on("error", (error) => {
    failure =
      (error as NodeJS.ErrnoException).code === "ENOENT"
        ? "Falta el ejecutable de la API. Vuelve a instalar MansoViaje."
        : "No se pudo iniciar la API: " + error.message;
  });
  // El pipe puede cerrarse mientras el proceso termina por sí mismo.
  child.stdin?.on("error", () => {});
  const closed = new Promise<void>((resolve) => {
    child.once("close", (code) => {
      failure ||= `La API se ha detenido (código ${code}). Comprueba que el puerto 8000 esté libre. Detalles en ${logPath}`;
      if (ready && !stopping) onStopped(failure);
      resolve();
    });
  });

  async function waitUntilReady() {
    const deadline = Date.now() + 30000;
    while (!stopping && !failure && Date.now() < deadline) {
      let response: Response | undefined;
      try {
        response = await fetch("http://127.0.0.1:8000/health", {
          signal: AbortSignal.timeout(750),
        });
      } catch {
        // Uvicorn aún puede estar inicializando la base de datos.
      }
      if (response) {
        const health = await response.json().catch(() => null);
        if (
          response.status === 200 &&
          health?.instance === instance &&
          health.version === version
        ) {
          if (failure || stopping) break;
          ready = true;
          return;
        }
        throw new Error("El puerto 8000 responde desde otro servicio. Ciérralo y reintenta.");
      }
      await delay(200);
    }
    throw new Error(failure || `La API no estuvo lista a tiempo. Consulta ${logPath}`);
  }

  async function stop() {
    if (!stopping) {
      stopping = true;
      child.stdin?.end();
    }
    // Uvicorn dispone de un plazo para completar las peticiones activas.
    const timer = setTimeout(() => child.kill(), 5000);
    try {
      await closed;
    } finally {
      clearTimeout(timer);
    }
  }

  return { waitUntilReady, stop };
}
