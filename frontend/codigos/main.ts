import { app, BrowserWindow } from "electron";
import path from "path";

// Función que crea la ventana principal
function createWindow(): void {

    const ventana = new BrowserWindow({
        width: 900,
        height: 550,
        resizable: false
    });

    // Carga el archivo HTML de la interfaz
    ventana.loadFile(
        path.join(__dirname, "../codigos/paginas/Login/index.html")
    );
}

// Cuando Electron termina de iniciar
app.whenReady().then(() => {

    createWindow();

    // En macOS, vuelve a crear la ventana
    // si no hay ninguna ventana abierta
    app.on("activate", () => {

        if (BrowserWindow.getAllWindows().length === 0) {
            createWindow();
        }

    });

});

// Cierra la aplicación cuando todas las ventanas
// se hayan cerrado
app.on("window-all-closed", () => {

    if (process.platform !== "darwin") {
        app.quit();
    }

});