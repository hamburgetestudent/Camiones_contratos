@echo off
setlocal

REM =========================================================
REM CAMIONES_CONTRATOS - NPM PORTATIL
REM =========================================================

set "PROJECT_DIR=%~dp0"
set "NODE_DIR=%PROJECT_DIR%herramientas\node"
set "NODE_EXE=%NODE_DIR%\node.exe"
set "NPM_CLI=%NODE_DIR%\node_modules\npm\bin\npm-cli.js"

REM ---------------------------------------------------------
REM Comprobar si Node.js ya existe
REM ---------------------------------------------------------

if exist "%NODE_EXE%" (
    goto NODE_READY
)

echo.
echo ========================================================
echo   CAMIONES_CONTRATOS - PREPARANDO NODE.JS
echo ========================================================
echo.
echo Node.js no encontrado.
echo Se descargara automaticamente.
echo.

set "NODE_VERSION=24.21.0"
set "NODE_ZIP=%PROJECT_DIR%herramientas\node.zip"
set "NODE_URL=https://nodejs.org/download/release/v%NODE_VERSION%/node-v%NODE_VERSION%-win-x64.zip"

if not exist "%PROJECT_DIR%herramientas" (
    mkdir "%PROJECT_DIR%herramientas"
)

echo Descargando Node.js v%NODE_VERSION%...
echo.

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "$ProgressPreference='SilentlyContinue'; Invoke-WebRequest -Uri '%NODE_URL%' -OutFile '%NODE_ZIP%'"

if errorlevel 1 (
    echo.
    echo ERROR: No se pudo descargar Node.js.
    echo Comprueba tu conexion a Internet.
    pause
    exit /b 1
)

echo.
echo Descarga completada.
echo Extrayendo Node.js...
echo.

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "Expand-Archive -Path '%NODE_ZIP%' -DestinationPath '%PROJECT_DIR%herramientas' -Force"

if errorlevel 1 (
    echo.
    echo ERROR: No se pudo extraer Node.js.
    pause
    exit /b 1
)

REM ---------------------------------------------------------
REM Mover la carpeta extraida al nombre "node"
REM ---------------------------------------------------------

if exist "%NODE_DIR%" (
    rmdir /s /q "%NODE_DIR%"
)

move "%PROJECT_DIR%herramientas\node-v%NODE_VERSION%-win-x64" "%NODE_DIR%" >nul

if errorlevel 1 (
    echo.
    echo ERROR: No se pudo preparar la carpeta de Node.js.
    pause
    exit /b 1
)

del "%NODE_ZIP%" >nul 2>&1

:NODE_READY

echo.
echo ========================================================
echo   NODE.JS
echo ========================================================
echo.

"%NODE_EXE%" --version


if errorlevel 1 (
    echo.
    echo ERROR: Node.js no pudo ejecutarse.
    pause
    exit /b 1
)

echo.
echo ========================================================
echo   NPM
echo ========================================================
echo.

"%NODE_EXE%" "%NPM_CLI%" --version

if errorlevel 1 (
    echo.
    echo ERROR: npm no pudo ejecutarse.
    pause
    exit /b 1
)

echo.

REM ---------------------------------------------------------
REM Ejecutar npm real usando el Node.js portatil
REM ---------------------------------------------------------

"%NODE_EXE%" "%NPM_CLI%" %*

exit /b %errorlevel%