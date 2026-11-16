import { app, BrowserWindow } from "electron";
import path from "path";

// Función que crea la ventana principal
function createWindow(): void {
  const ventana = new BrowserWindow({
    width: 980,
    height: 680,
    resizable: true,
  });

  // Carga el archivo HTML de la interfaz de inicio de sesión
  ventana.loadFile(path.join(__dirname, "../paginas/Login/index.html"));
}

// Cuando Electron termina de iniciar
app.whenReady().then(() => {
  createWindow();

  // En macOS, vuelve a crear la ventana si no hay ninguna ventana abierta
  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

// Cierra la aplicación cuando todas las ventanas se hayan cerrado
app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
});
