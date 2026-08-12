import { app, BrowserWindow, ipcMain, shell } from 'electron';
import * as path from 'path';

function createWindow() {
    // Create the browser window.
    const mainWindow = new BrowserWindow({
        width: 1280,
        height: 800,
        backgroundColor: '#0b0f19', // matches CSS --bg-main
        webPreferences: {
            // Load preload.js from the same directory where main.js will reside after compilation
            preload: path.join(__dirname, 'preload.js'),
            contextIsolation: true,
            nodeIntegration: false
        },
        title: "Monitoreo de Contratos de Camiones"
    });

    // Load the index.html of the app.
    mainWindow.loadFile(path.join(__dirname, 'index.html'));

    // Remove the default menu bar for a cleaner look
    mainWindow.removeMenu();
}

// IPC listener to open external URLs in the user's default browser (e.g. Swagger documentation)
ipcMain.on('open-external', (_event, url) => {
    if (url.startsWith('http://') || url.startsWith('https://')) {
        shell.openExternal(url);
    }
});

// Initialize Electron
app.whenReady().then(() => {
    createWindow();

    app.on('activate', () => {
        // On macOS it's common to re-create a window in the app when the
        // dock icon is clicked and there are no other windows open.
        if (BrowserWindow.getAllWindows().length === 0) createWindow();
    });
});

// Quit when all windows are closed, except on macOS.
app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') app.quit();
});
