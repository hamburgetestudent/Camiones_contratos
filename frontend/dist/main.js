"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const electron_1 = require("electron");
const path_1 = __importDefault(require("path"));
// Función que crea la ventana principal adaptada a la pantalla de escritorio
function createWindow() {
    const primaryDisplay = electron_1.screen.getPrimaryDisplay();
    const { width, height } = primaryDisplay.workAreaSize;
    // Tamaño adecuado proporcional a la resolución de la pantalla de escritorio
    const windowWidth = Math.min(1280, Math.max(1000, Math.floor(width * 0.85)));
    const windowHeight = Math.min(850, Math.max(680, Math.floor(height * 0.85)));
    const ventana = new electron_1.BrowserWindow({
        width: windowWidth,
        height: windowHeight,
        minWidth: 960,
        minHeight: 620,
        resizable: true,
        center: true,
        autoHideMenuBar: true,
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true
        }
    });
    // Abre la ventana maximizada para adaptarse al escritorio
    ventana.maximize();
    // Carga el archivo HTML de la interfaz
    ventana.loadFile(path_1.default.join(__dirname, "../paginas/Login/index.html"));
}
// Cuando Electron termina de iniciar
electron_1.app.whenReady().then(() => {
    createWindow();
    // En macOS, vuelve a crear la ventana si no hay ninguna abierta
    electron_1.app.on("activate", () => {
        if (electron_1.BrowserWindow.getAllWindows().length === 0) {
            createWindow();
        }
    });
});
// Cierra la aplicación cuando todas las ventanas se hayan cerrado
electron_1.app.on("window-all-closed", () => {
    if (process.platform !== "darwin") {
        electron_1.app.quit();
    }
});
//# sourceMappingURL=main.js.map