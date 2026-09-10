"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const electron_1 = require("electron");
const path_1 = __importDefault(require("path"));
// Función que crea la ventana principal
function createWindow() {
    electron_1.Menu.setApplicationMenu(null);
    const ventana = new electron_1.BrowserWindow({
        width: 900,
        height: 550,
        resizable: false
    });
    // Carga el archivo HTML de la interfaz
    ventana.loadFile(path_1.default.join(__dirname, "../paginas/Login/index.html"));
}
// Cuando Electron termina de iniciar
electron_1.app.whenReady().then(() => {
    createWindow();
    // En macOS, vuelve a crear la ventana
    // si no hay ninguna ventana abierta
    electron_1.app.on("activate", () => {
        if (electron_1.BrowserWindow.getAllWindows().length === 0) {
            createWindow();
        }
    });
});
// Cierra la aplicación cuando todas las ventanas
// se hayan cerrado
electron_1.app.on("window-all-closed", () => {
    if (process.platform !== "darwin") {
        electron_1.app.quit();
    }
});
//# sourceMappingURL=main.js.map