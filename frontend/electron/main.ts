import { app, BrowserWindow } from "electron";
import { mkdirSync } from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { launchBackend } from "./backend";

const login = "http://127.0.0.1:8000/login/login.html";
const errorPage = path.join(__dirname, "../src/paginas/Inicio/error.html");
const retry = pathToFileURL(path.join(__dirname, "../src/paginas/Inicio/reintentar")).href;

let window: BrowserWindow | null = null;
let backend: ReturnType<typeof launchBackend> | null = null;
let quitting = false;
let starting = false;

async function showError(reason: string) {
  if (!quitting && window && !window.isDestroyed()) {
    await window.loadFile(errorPage, { query: { motivo: reason } });
  }
}

async function openProduct() {
  if (starting || quitting || !window) return;
  starting = true;
  try {
    if (app.isPackaged) {
      if (backend) await backend.stop();
      if (quitting) return;
      backend = launchBackend(
        path.join(process.resourcesPath, "backend", "mansoviaje-api.exe"),
        app.getPath("userData"),
        app.getVersion(),
        (reason) => {
          void showError(reason);
        }
      );
      await backend.waitUntilReady();
    }
    if (!quitting && !window.isDestroyed()) await window.loadURL(login);
  } catch (error) {
    if (backend) await backend.stop();
    await showError(error instanceof Error ? error.message : String(error));
  } finally {
    starting = false;
  }
}

function createWindow() {
  window = new BrowserWindow({
    title: "MansoViaje — Contratos de carga",
    backgroundColor: "#f8fafc",
    width: 1180,
    height: 760,
    minWidth: 800,
    minHeight: 550,
    webPreferences: { contextIsolation: true, sandbox: true, nodeIntegration: false },
  });
  window.webContents.on("will-navigate", (event, url) => {
    if (url === retry) {
      event.preventDefault();
      void openProduct();
    }
  });
  void openProduct();
}

const override = process.env.MANSOVIAJE_DATA_DIR;
if (override) {
  if (!path.isAbsolute(override))
    throw new Error("MANSOVIAJE_DATA_DIR debe ser una ruta absoluta.");
  mkdirSync(override, { recursive: true });
  app.setPath("userData", override);
}

if (app.isPackaged && !app.requestSingleInstanceLock()) {
  app.quit();
} else {
  app.on("second-instance", () => {
    if (window?.isMinimized()) window.restore();
    window?.focus();
  });
  app.whenReady().then(createWindow);
  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
}

app.on("before-quit", (event) => {
  if (!backend) return;
  event.preventDefault();
  if (quitting) return;
  quitting = true;
  void backend.stop().finally(() => {
    backend = null;
    app.quit();
  });
});
app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});
