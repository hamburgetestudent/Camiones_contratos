# Guía e Instrucciones de Formateo de Código

Este documento contiene los comandos e instrucciones para formatear y verificar el estilo del código en el proyecto **Camiones Contratos**, tanto para el **Frontend (Prettier)** como para el **Backend (Ruff)**, ya sea de forma conjunta o por separado.

---

## 🚀 Resumen Rápido de Comandos

Todos los comandos se pueden ejecutar directamente desde la **raíz del proyecto**:

| Objetivo | Comando de Formateo (Aplica cambios) | Comando de Verificación (Solo chequea) |
| :--- | :--- | :--- |
| **Todo el Proyecto** (Front + Back) | `npm run format:all` (o `npm run format`) | `npm run format:all:check` (o `npm run format:check`) |
| **Solo Frontend** (Electron / TS / JS / HTML / CSS) | `npm run format:frontend` | `npm run format:frontend:check` |
| **Solo Backend** (Python / FastAPI) | `npm run format:backend` | `npm run format:backend:check` |

---

## 🎨 1. Frontend: Formateo con Prettier

El frontend utiliza **Prettier** con configuración de comillas dobles, sangría de 2 espacios y saltos de línea automáticos (`endOfLine: "auto"`).

### Opción A: Desde la raíz del proyecto
* **Formatear y corregir:**
  ```bash
  npm run format:frontend
  ```
* **Verificar sin modificar archivos:**
  ```bash
  npm run format:frontend:check
  ```

### Opción B: Dentro de la carpeta `Camiones_contratos/frontend/`
* **Formatear:**
  ```bash
  npm run format
  ```
* **Verificar:**
  ```bash
  npm run format:check
  ```

Archivos que formatea: `.ts`, `.js`, `.html`, `.css`, `.json`. Ignora automáticamente `node_modules/` y `dist/`.

---

## 🐍 2. Backend: Formateo y Linter con Ruff

El backend en Python utiliza **Ruff**, que unifica el formateo (estilo Black), el ordenamiento de importaciones (estilo isort) y la detección de problemas comunes de sintaxis y variables no utilizadas (estilo Flake8).

### Opción A: Desde la raíz del proyecto
* **Formatear, ordenar imports y corregir advertencias:**
  ```bash
  npm run format:backend
  ```
* **Verificar formato y linter sin modificar archivos:**
  ```bash
  npm run format:backend:check
  ```

### Opción B: Directo con Python / Ruff (dentro de `Camiones_contratos/`)
Con tu entorno virtual activo (`source venv/bin/activate` en Linux/Mac o `venv\Scripts\activate` en Windows):

* **Formatear archivos Python:**
  ```bash
  ruff format .
  ```
* **Ordenar imports y autofix de linter:**
  ```bash
  ruff check . --fix
  ```
* **Solo verificar formato (sin modificar):**
  ```bash
  ruff format --check .
  ```
* **Solo verificar linter (sin modificar):**
  ```bash
  ruff check .
  ```

---

## 💻 3. Formateo Automático en VS Code (Al Guardar)

Para que el código se formatee solo al presionar `Ctrl + S` (o `Cmd + S` en macOS):

1. **Instala las 2 extensiones recomendadas:**
   * **Prettier - Code formatter** (`esbenp.prettier-vscode`)
   * **Ruff** (`charliermarsh.ruff`)

2. La configuración del espacio de trabajo en [`.vscode/settings.json`](file:///home/f4cks/Escritorio/Ing/camiones/.vscode/settings.json) ya viene lista con:
   ```json
   {
     "editor.formatOnSave": true,
     "editor.defaultFormatter": "esbenp.prettier-vscode",
     "[python]": {
       "editor.defaultFormatter": "charliermarsh.ruff",
       "editor.formatOnSave": true,
       "editor.codeActionsOnSave": {
         "source.fixAll.ruff": "explicit",
         "source.organizeImports.ruff": "explicit"
       }
     }
   }
   ```

---

## 🌐 4. Compatibilidad Windows y Linux

Tanto Prettier ([`.prettierrc`](file:///home/f4cks/Escritorio/Ing/camiones/Camiones_contratos/frontend/.prettierrc)) como Ruff ([`pyproject.toml`](file:///home/f4cks/Escritorio/Ing/camiones/Camiones_contratos/pyproject.toml)) están configurados con:
* `endOfLine: "auto"` / `line-ending = "auto"`

Esto evita que Git detecte cambios fantasma o conflictos de fin de línea (`CRLF` vs `LF`) cuando distintos miembros del equipo trabajan desde Linux o Windows.
