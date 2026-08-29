"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const electron_1 = require("electron");
// Función que crea la ventana principal 
function createWindow() {
    const ventana = new electron_1.BrowserWindow({ width: 800, height: 600 });
    // Carga una página HTML sencilla
    ventana.loadURL("data:text/html;charset=utf-8," + encodeURIComponent(` <html> <body> <h1>Electron funcionando correctamente</h1> <p>Node.js + Electron + TypeScript están funcionando.</p> </body> </html> `));
}
// Cuando Electron termina de iniciar, crea la ventana 
electron_1.app.whenReady().then(() => {
    createWindow();
    // En macOS, vuelve a crear la ventana si no hay ninguna abierta 
    electron_1.app.on("activate", () => { if (electron_1.BrowserWindow.getAllWindows().length === 0) {
        createWindow();
    } });
});
// Cierra la aplicación cuando todas las ventanas se cierran 
electron_1.app.on("window-all-closed", () => { if (process.platform !== "darwin") {
    electron_1.app.quit();
} });
//# sourceMappingURL=main.js.map