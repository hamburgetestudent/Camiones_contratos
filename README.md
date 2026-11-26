# MansoViaje — Camiones Contratos

Plataforma integral multiplataforma orientada a la centralización y digitalización de contratos de transporte terrestre de carga. Conecta a empresas generadoras de carga (**Dadores de Carga**) con **Transportistas** independientes o flotas de camioneros, cubriendo el registro y verificación documental (KYC), publicación de cargas, subastas/postulaciones, adjudicación y seguimiento del ciclo de vida del contrato.

La arquitectura separa claramente las responsabilidades entre cliente y servidor:

* **Frontend (`frontend/`):** Aplicación de escritorio desarrollada con **Electron** y **TypeScript**, con vistas por rol para autenticación, registro y operación comercial.
* **Backend (`backend/app/`, organizado por módulos de dominio):** API REST modular construida con **FastAPI** y **Pydantic**, lógica de negocio gobernada por una máquina de estados finitos y persistencia directa en **SQLite** (`camiones.db`).

## Entrega 1.0.1 para Windows x64

[Acta de aceptación del instalador 1.0.0: SHA-256, commit, instalación, CI y pruebas](docs/aceptacion-escritorio-1.0.0.md) · [Ficha para la revisión por otro equipo](docs/revision-externa.md)

### Instalar y ejecutar

1. Obtén `MansoViaje-1.0.1-win-x64.exe`, `SHA256SUMS.txt` y `VERSION.txt` de la [release v1.0.1](https://github.com/hamburgetestudent/Camiones_contratos/releases/tag/v1.0.1) o de la carpeta de entrega compartida por el equipo. En la copia de construcción están en `release/`. El primer archivo contiene la aplicación, FastAPI, SQLite, las vistas y las cuentas de demostración. El SHA identifica el instalador exacto. `VERSION.txt` identifica el commit y sus comprobaciones en GitHub.
2. En una carpeta nueva, abre PowerShell y ejecuta los comandos de abajo. Compara el hash con el listado antes de abrir el instalador. Elige una carpeta de instalación para tu usuario. Abre **MansoViaje** desde Inicio. Requiere Windows x64, permiso de escritura en el perfil y el puerto local 8000 libre. La instalación y el flujo funcionan localmente. La descarga inicial y el acceso a GitHub requieren conexión. Los usuarios de prueba vienen incluidos.
3. Al ver Login ya puedes operar. La primera apertura crea `camiones.db` en los datos de usuario de la aplicación. Para usar un perfil aislado, cierra la aplicación, define `MANSOVIAJE_DATA_DIR` con una ruta absoluta nueva y arranca el ejecutable desde esa misma terminal. Los archivos de datos y `backend.log` estarán allí. La [configuración de ejemplo](.env.example) documenta las variables de entorno.

```powershell
Get-FileHash -Algorithm SHA256 .\MansoViaje-1.0.1-win-x64.exe
Get-Content .\SHA256SUMS.txt
.\MansoViaje-1.0.1-win-x64.exe
```

Para reproducir el ensayo interno en un usuario de Windows sin una instalación previa, se puede instalar el mismo archivo en una carpeta nueva desde PowerShell. Copia el instalador a la carpeta actual y comprueba su hash con el comando anterior:

```powershell
$destino = Join-Path $env:LOCALAPPDATA 'MansoViaje-Hito3'
$instalacion = Start-Process .\MansoViaje-1.0.1-win-x64.exe -ArgumentList "/S /D=$destino" -Wait -PassThru
if ($instalacion.ExitCode -ne 0) { throw "Error de instalación: $($instalacion.ExitCode)" }
```

Abre `MansoViaje.exe` desde esa carpeta para la revisión manual. Para la aceptación automatizada, cierra primero la aplicación, extrae las fuentes en otra carpeta y ejecuta desde la raíz de esas fuentes, en la misma sesión de PowerShell:

```powershell
npm.cmd --prefix frontend ci
node frontend/tests/entrega.e2e.cjs "$destino\MansoViaje.exe"
```

El guion usa un perfil temporal independiente y conserva la base de prueba para inspección.

### Postular a una carga y comprobar la persistencia

1. Entra con `contacto@logisticasur.cl` y `dador123`. Abre **Registrar Contrato de Carga → + Nuevo contrato**. Usa origen Valparaíso, destino Concepción, carga general, camión de 12.000 kg, peso de 6.000 kg, CLP y neto de 200.000. Conserva las fechas futuras y los importes calculados. Pulsa **Crear y publicar contrato** y anota el ID.
2. Cierra sesión. Entra con `juan.perez@rutanorte.cl` y `camion123`. En **Subastas y Cargas Disponibles**, elige la carga y **Ver detalle y postular**. Intenta ofertar 4.900 CLP: el formulario exige al menos 5.000. Corrige a **180.000 CLP**, indica 6 horas y pulsa **Enviar postulación**. Debe aparecer la confirmación.
3. Vuelve a entrar como dador. En **Gestión de Subastas y Adjudicación → Revisar ofertas**, comprueba una oferta de 180.000 CLP en `POSTULADA` y el contrato en `EN_POSTULACION`. Cierra MansoViaje y vuelve a abrirlo con el mismo perfil. Inicia sesión de nuevo y comprueba los mismos datos.

### Resolver problemas frecuentes

| Síntoma | Qué comprobar |
|---|---|
| La pantalla de inicio indica que la API no está disponible | Cierra el Uvicorn de desarrollo si estaba abierto. Consulta `Get-NetTCPConnection -LocalPort 8000 -State Listen` y revisa el propietario antes de detener procesos. Pulsa **Reintentar** cuando el puerto esté disponible. |
| Falló la inicialización de datos | Comprueba permisos de escritura en la carpeta de datos y revisa `backend.log`. Conserva una copia de la base cerrando primero la aplicación. |
| Aparece Login de nuevo tras reiniciar | Inicia sesión con la cuenta del mismo rol y comprueba el contrato por ID. La clave de sesión puede renovarse al reiniciar. |
| El equipo bloquea el instalador | Comprueba el SHA y consulta al responsable del laboratorio si admite instaladores académicos sin firma. |
| Busco el código o las licencias | Junto al ejecutable instalado está `resources/entrega/` con `fuentes.zip`, `VERSION.txt`, `.env.example` y `THIRD_PARTY_LICENSES.txt`. Extrae el ZIP para seguir los enlaces relativos de este README. |

### Extender el comentario de una oferta y probarlo

Extrae `fuentes.zip` en una carpeta nueva. Para preparar desarrollo en Windows usa Python 3.12 x64, Node 24 con npm y la red para instalar dependencias. Desde la carpeta donde está este README:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt pytest httpx
npm.cmd --prefix frontend ci
npm.cmd start
```

Para admitir comentarios de hasta 600 caracteres, cambia `PostulacionBase.comentario` de 500 a 600 en [el modelo](backend/app/modules/subastas/models.py) y `iComentario.maxLength` al mismo valor en [el formulario](frontend/src/paginas/panel/vistas/transportista/subastas.js). SQLite ya guarda texto. Añade dos casos junto a [las validaciones de postulación](backend/tests/subastas/test_modelos_postulacion.py): construir `PostulacionCrear` con 600 caracteres debe conservar el comentario completo y con 601 debe producir `ValidationError`. Ejecuta la prueba desde la raíz:

```powershell
.\.venv\Scripts\python.exe -m pytest backend/tests/subastas/test_modelos_postulacion.py -q
```

### Reconstruir el instalador desde Git

En Windows x64, clona el repositorio, selecciona el commit completo que figura en `VERSION.txt` y ejecuta desde la raíz:

```powershell
python -m venv .venv
.\scripts\construir-entrega.ps1
```

El script usa el lock de Python para Windows y el lockfile npm, genera el backend con PyInstaller y produce el instalador NSIS y su SHA-256 en `release/`. La [suite y cobertura](.github/workflows/tests.yml), la [prueba del ejecutable](frontend/tests/entrega.e2e.cjs), las [notas y cierre](CHANGELOG.md), los [tres casos del panel](docs/integracion-postulacion.md) y la [ficha para otro equipo](docs/revision-externa.md) documentan aspectos distintos de la entrega.

### Enlaces Rápidos

* **Estructura modular:** [Antes, después y responsabilidades](docs/modularizacion.md)
* **Contrato reutilizable:** [Servicio de usuarios](docs/contrato-usuario-service.md)

* **Hito 3 · Intervenciones:** [Diagnóstico, tres refactorizaciones y pruebas (criterios 1 y 2)](docs/hito3-intervenciones.md)
* **Hito 3 · Modularización:** [Criterio 4: modularización de interfaces y dependencias](docs/criterio-4-modularizacion.md)
* **Hito 3 · Punto 6 (dependencia externa):** [Revisión de `email-validator`: utilidad, mantenimiento, licencia, riesgo y mitigación](docs/revision-dependencia-email-validator.md)
* **Modelado UML (Entrega 3):** [Índice de diagramas](docs/README.md)
* **Panel de administración:** [Navegación, bajas lógicas, auditoría y pruebas](docs/panel-administracion.md)
* **Reglas de Negocio:** [`REGLAS_DE_NEGOCIO.md`](REGLAS_DE_NEGOCIO.md)
* **Changelog, verificación del flujo y cierre de la entrega:** [`CHANGELOG.md`](CHANGELOG.md)
* **Guía de Pruebas y Cobertura:** [`backend/tests/README.md`](backend/tests/README.md)
* **Prototipo UI (Figma):** [Contratos camioneros centralizados](https://www.figma.com/design/leoA2Ejoi6cJi13esWBsXQ/Contratos_camioneros_centralizados?node-id=0-1&t=v76XFzFL7hSGl8TY-1)
* **Cronología de cambios e informes:** [Documento en Google Docs](https://docs.google.com/document/d/1p95pKZ2zpQuFnw19-MtfZ5WIhdKAEz30nYLUg9G9B-U/edit?tab=t.0)

---

## Requisitos previos para desarrollo

Antes de descargar y ejecutar el proyecto, asegúrate de contar con:

* **Git**
* **Python:** `3.12` *(probado en CI con Python `3.12`)*
* **Node.js:** `v24` en GitHub Actions; construcción local comprobada con `v26.13.0` y **npm** `v10+`

---

## Desarrollo con dos terminales

> [!IMPORTANT]
> La aplicación funciona en arquitectura cliente-servidor local: el **Backend** debe permanecer ejecutándose en una terminal (`http://127.0.0.1:8000`) mientras utilizas el **Frontend de Electron** desde una segunda terminal.

### Paso 1 — Clonar el repositorio

```bash
git clone https://github.com/hamburgetestudent/Camiones_contratos.git
cd Camiones_contratos
```

### Paso 2 — Instalar e iniciar el Backend (Terminal 1)

1. Crea y activa el entorno virtual de Python desde la raíz `Camiones_contratos/`:

   ```bash
   python -m venv venv
   ```

   Actívalo según tu sistema operativo y terminal:

   * **Windows (PowerShell):**
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   * **Windows (CMD):**
     ```bat
     venv\Scripts\activate.bat
     ```
   * **Linux / macOS:**
     ```bash
     source venv/bin/activate
     ```

2. Instala las dependencias del backend:

   ```bash
   pip install -r requirements.txt
   ```

3. Inicia el servidor FastAPI (**elige solo una** de las dos opciones y deja esta terminal abierta):

   ```bash
   # Opción recomendada (con recarga automática durante desarrollo):
   uvicorn app.main:app --app-dir backend --reload --host 127.0.0.1 --port 8000

   # Alternativa directa:
   cd backend && python -m app.main
   ```

> Al arrancar por primera vez, el servidor crea e inicializa automáticamente `camiones.db` usando [`backend/app/db/schema.sql`](backend/app/db/schema.sql) y carga las cuentas semilla iniciales. La documentación interactiva queda disponible en `http://127.0.0.1:8000/docs`.

### Paso 3 — Instalar e iniciar el Frontend de Escritorio (Terminal 2)

Con el backend ya corriendo en la Terminal 1, abre **una nueva terminal** en la carpeta `Camiones_contratos/` y ejecuta:

```bash
cd frontend
npm ci
npm start
```

* `npm start` compila el código TypeScript (`electron/` ➔ `dist/`) y abre la ventana de **Electron** conectada a `http://127.0.0.1:8000`.
* Para desarrollo continuo del archivo principal de Electron puedes ejecutar `npm run dev` (`tsc --watch`).

### Paso 4 — Verificar la instalación y cuentas de prueba

1. Abre `http://127.0.0.1:8000/docs` en tu navegador y confirma los **6 routers activos** cargados por [`backend/app/main.py`](backend/app/main.py):
   * `/auth`: Registro, inicio de sesión y consulta de usuarios.
   * `/admin`: Panel administrativo, resumen y bajas lógicas.
   * `/configuracion`: Consulta y actualización de reglas de negocio globales.
   * `/contratos`: Creación, listado y transiciones de estado de contratos.
   * `/onboarding`: Carga documental de transportistas, perfil tributario de dadores y validación KYC.
   * `/subastas`: Exploración de cargas, postulación y adjudicación de ofertas.
2. Las rutas de negocio (`/configuracion`, `/contratos`, `/onboarding`, `/subastas`) y las rutas de `/admin` están protegidas mediante token **JWT Bearer** validado en [`backend/app/modules/usuarios/sesion.py`](backend/app/modules/usuarios/sesion.py):
   * Para probarlas en **Swagger UI**, ejecuta primero `POST /auth/login` con una cuenta válida, copia el campo `access_token` de la respuesta y pégalo en el botón **Authorize** de Swagger.
   * Desde la aplicación de **Electron**, basta con iniciar sesión en la pantalla de Login.
3. **Cuentas semilla precargadas** (definidas en [`backend/app/db/conexion.py`](backend/app/db/conexion.py)):

| Rol | Correo electrónico | Contraseña | Estado inicial |
|---|---|---|---|
| `ADMIN_BACKOFFICE` | `admin@camiones.cl` | `admin123` | `APROBADO` |
| `DADOR_CARGA` | `contacto@logisticasur.cl` | `dador123` | `APROBADO` |
| `DADOR_CARGA` | `operaciones@vallecentral.cl` | `valle123` | `EN_REVISION` |
| `TRANSPORTISTA` | `juan.perez@rutanorte.cl` | `camion123` | `APROBADO` |
| `TRANSPORTISTA` | `carlos.soto@transporte.cl` | `carlos123` | `EN_REVISION` |

---

## Pruebas Automatizadas y Calidad de Código

Todos los comandos se ejecutan desde la raíz `Camiones_contratos/` con el entorno virtual `venv` activado.

### Suite principal con medición de cobertura (`run_tests.py`)

```bash
# Ejecutar toda la suite unittest y ver cobertura en consola
python run_tests.py

# Generar reporte interactivo HTML (queda en htmlcov/index.html)
python run_tests.py --html

# Limpiar archivos temporales de cobertura (.coverage, htmlcov/, *.cover)
python run_tests.py --clean
```

### Ejecución con `pytest` (flujo del CI en GitHub Actions)

Si prefieres correr los tests con `pytest` (como en [`.github/workflows/tests.yml`](.github/workflows/tests.yml)):

```bash
pip install pytest httpx
coverage run -m pytest
coverage report -m
```

### Linter y verificación de tipos

```bash
# Linter del backend (configurado en pyproject.toml)
ruff check .

# Chequeo de tipos TypeScript del frontend
cd frontend
npx tsc --noEmit
```

### Verificación del flujo integrado

```bash
python scripts/verificar_flujo_integrado.py
```

Ejecuta tres casos (datos válidos, datos inválidos y recurso ausente) sobre la API real y una base temporal. Los resultados esperados y obtenidos están en [`CHANGELOG.md`](CHANGELOG.md).

Para más detalle sobre filtros por módulo y estructura de pruebas, consulta [`backend/tests/README.md`](backend/tests/README.md).

---

## Cómo extender el proyecto

Para agregar una capacidad nueva (por ejemplo, un endpoint o una entidad) sigue el mismo recorrido de capas:

1. **Modelos (`modules/<dominio>/models.py`):** define el modelo Pydantic y sus validadores. Si cambia el ciclo de vida de un contrato, agrega el estado y las transiciones en `maquina_estados.py`.
2. **Esquema (`backend/app/db/schema.sql`):** agrega la tabla o columna de forma idempotente (`CREATE TABLE IF NOT EXISTS`). Para columnas en una base ya instalada, sigue el patrón de `_asegurar_esquema` en `backend/app/db/conexion.py`.
3. **DAO (`modules/<dominio>/dao.py`):** crea una clase que herede de `BaseDAO` con el SQL de la entidad.
4. **Servicio (`modules/<dominio>/service.py`):** escribe la regla de negocio recibiendo el DAO por inyección (`backend/app/core/dependencies.py`) y documenta Precondiciones, Postcondiciones e Invariantes en el docstring.
5. **Router (`modules/<dominio>/router.py`):** expón el endpoint, protégelo con las dependencias de `backend/app/modules/usuarios/sesion.py` y registra el router en `backend/app/main.py`.
6. **Pruebas (`backend/tests/<dominio>/`):** agrega pruebas en la carpeta del módulo, ejecuta `python run_tests.py` y `ruff check .`.
7. **Verificación del flujo:** si el cambio afecta el flujo principal, extiende los casos de `scripts/verificar_flujo_integrado.py` y registra el resultado en [`CHANGELOG.md`](CHANGELOG.md).

---

## Arquitectura del Sistema

El backend se organiza **por dominio** (`backend/app/modules/<dominio>/`). Dentro de cada módulo se conserva la separación en capas `router → service → dao → modelos`, y lo transversal vive en `core/` y `db/`:

```text
Camiones_contratos/
├── backend/
│   ├── app/
│   │   ├── main.py                   # Punto de entrada FastAPI y montaje de routers
│   │   ├── core/                     # Transversal: security.py (hash/JWT), dependencies.py (instancias compartidas), http.py (errores HTTP)
│   │   ├── db/                       # conexion.py (SQLite, esquema, semilla), schema.sql y base_dao.py
│   │   └── modules/
│   │       ├── usuarios/             # router, service, dao, models, models_login, respuesta_login, sesion
│   │       ├── contratos/            # router, service, dao, models, maquina_estados
│   │       ├── onboarding/           # router, service, dao, models
│   │       ├── subastas/             # router, service, dao, models (postulaciones)
│   │       ├── configuracion/        # router, reglas (ReglasNegocio)
│   │       └── admin/                # router, service
│   └── tests/                        # Suite por módulo (admin, usuarios, contratos, ...)
├── frontend/                         # Cliente de escritorio Electron + TypeScript
│   ├── electron/                     # Proceso principal de Electron (main.ts)
│   ├── src/
│   │   ├── paginas/                  # login, registro, catalogo-contratos, crear-contrato, panel (+ vistas/<rol>/)
│   │   ├── compartido/               # css/tema.css, js/{iconos,sesion,api}.js
│   │   └── recursos/imagenes/
│   ├── tests/e2e/                    # Pruebas end-to-end del panel
│   ├── package.json
│   └── tsconfig.json
├── api/index.py                      # Entrypoint para Vercel
├── docs/                             # Diagramas UML y documentación de modelado
├── scripts/                          # Utilidades de desarrollo y verificación
├── run_tests.py                      # Runner oficial de pruebas y cobertura
├── pyproject.toml                    # Ruff, pytest y herramientas Python
└── requirements.txt                  # Dependencias del backend
```

### Descripción de Módulos y Capas

Cada módulo de `backend/app/modules/` agrupa sus capas:

* **Modelos (`models.py`):** entidades Pydantic y validadores. `contratos/models.py` (`ContratoBase`, `ContratoCrear`, `ContratoModelo`, `TipoCarga`, `Moneda`), `usuarios/models.py` (`UsuarioModelo`, `RolUsuario`, `EstadoUsuario`), `usuarios/models_login.py` (`CredencialesLogin`, `RespuestaLogin`), `onboarding/models.py` (`DadorCarga`, `DocumentoTransportista`, `TipoDocumento`, `EstadoValidacion`) y `subastas/models.py` (`PostulacionModelo`, `EstadoPostulacion`, `MaquinaEstadoPostulacion`).
* **Reglas y estados:** `core/maquina_estados.py` (`MaquinaEstadosBase` genérica) y `contratos/maquina_estados.py` (`EstadoContrato` y `MaquinaEstadosContrato`) y `configuracion/reglas.py` (singleton `ReglasNegocio` con `IVA_PORCENTAJE`, `TOLERANCIA_MAX`, `ANTICIPACION_MIN_H`).
* **DAO (`dao.py`):** `db/base_dao.py` define `BaseDAO`; cada módulo concentra el SQL de su entidad y recibe una conexión abierta, de modo que un servicio puede combinar varios DAO en una sola transacción.
* **Servicios (`service.py`):** `usuarios` (registro, hash SHA-256, autenticación, emisión de JWT), `onboarding` (carga documental, perfil tributario, aprobación/rechazo), `contratos` (creación, lectura y transiciones), `subastas` (exploración, postulaciones y adjudicación atómica "todo o nada") y `admin` (consultas administrativas, resúmenes y bajas lógicas).
* **Routers (`router.py`):** exponen los endpoints HTTP de cada módulo. `usuarios/sesion.py` es la guardia Bearer con revocación de sesión.
* **Base de datos (`db/`):** `conexion.py` gestiona conexiones y transacciones exclusivas (`obtener_conexion`, `transaccion_exclusiva`), inicializa el esquema y carga los datos semilla; `schema.sql` define tablas e índices de forma idempotente.
* **Núcleo (`core/`):** `maquina_estados.py` (base genérica), `security.py` (tokens JWT Bearer `HS256`), `dependencies.py` (instancias compartidas e inyección) y `http.py` (manejo uniforme de errores HTTP).
* **Capa de Frontend (`frontend/`):**
  * `electron/main.ts`: Proceso principal de Electron que inicia la ventana y carga `src/paginas/login/login.html`.
  * `src/paginas/`: Una carpeta por pantalla (HTML/CSS/JS) para login, registro, catálogo de contratos, creación de contratos y panel por rol.
  * `src/compartido/`: Tema CSS, íconos, sesión (`sesion.js`) y cliente de la API (`api.js`) usados por todas las páginas. Todo el JS son **módulos ES** (`<script type="module">`): cada página importa `MVApi`, `MVSesion` y `MVIconos` en lugar de usar globales de `window`. En el panel, `estado.js` guarda el usuario y `ui.js` las utilidades de interfaz; cada rol tiene su carpeta en `vistas/` con un `index.js` enrutador y un archivo por pantalla.

### Ciclo de Vida del Contrato (Máquina de Estados)

Las transiciones son validadas por `app.modules.contratos.maquina_estados.MaquinaEstadosContrato`:

* Flujo principal: `BORRADOR` ➔ `PUBLICADO` / `EN_SUBASTA` ➔ `EN_POSTULACION` ➔ `ADJUDICADO` ➔ `EN_TRANSITO` ➔ `ENTREGADO` ➔ `FINALIZADO`
* Flujos alternativos:
  * Desde estados previos a `EN_TRANSITO` puede transicionar a `CANCELADO` (estado terminal).
  * Desde `EN_TRANSITO` o `ENTREGADO` puede pasar a `EN_DISPUTA`, y desde allí resolverse hacia `FINALIZADO` o `CANCELADO`.

### Diagrama de Arquitectura en Capas

```mermaid
flowchart TD
    subgraph UI["Capa de Presentación"]
        A["Usuario"] --> B["Frontend Desktop<br/>Electron + TypeScript (frontend/)"]
        A --> C["Swagger UI / Cliente HTTP<br/>http://127.0.0.1:8000/docs"]
    end

    subgraph API["Capa de Enrutamiento (FastAPI)"]
        B & C --> D["backend/app/main.py (FastAPI App)"]
        D --> SSEC["backend/app/modules/usuarios/sesion.py (JWT Bearer)"]
        D --> R1["backend/app/modules/usuarios/router.py"]
        D --> R2["backend/app/modules/admin/router.py"]
        D --> R3["backend/app/modules/contratos/router.py"]
        D --> R4["backend/app/modules/subastas/router.py"]
        D --> R5["backend/app/modules/onboarding/router.py"]
        D --> R6["backend/app/modules/configuracion/router.py"]
    end

    subgraph SERVICES["Capa de Servicios de Negocio"]
        R1 & SSEC --> S1["backend/app/modules/usuarios/service.py & security.py"]
        R2 --> S5["backend/app/modules/admin/service.py"]
        R3 --> S2["backend/app/modules/contratos/service.py"]
        R4 --> S3["backend/app/modules/subastas/service.py"]
        R5 --> S4["backend/app/modules/onboarding/service.py"]
    end

    subgraph DOMAIN["Capa de Dominio & Reglas"]
        R6 --> M3["backend/app/modules/configuracion/reglas.py (ReglasNegocio)"]
        S2 & S3 --> M1["backend/app/modules/contratos/maquina_estados.py"]
        S1 & S2 & S3 & S4 --> M2["modules/*/models.py"]
        M2 --> M3
    end

    subgraph PERSISTENCE["Capa de Persistencia (SQLite)"]
        S1 & S2 & S3 & S4 & S5 --> DBCON["backend/app/db/conexion.py"]
        DBCON --> SQLITE[("camiones.db<br/>backend/app/db/schema.sql")]
    end
```

---

## Contratos de Diseño: Precondiciones, Postcondiciones e Invariantes

Las reglas de uso de las operaciones principales están documentadas en el docstring de cada función bajo los encabezados **Precondiciones**, **Postcondiciones** e **Invariantes**. Cuando se viola una precondición, la operación falla con una excepción explícita (`ValueError`, `PermissionError` o `HTTPException`) y **no modifica el estado**.

| Operación | Dónde está el contrato | Endpoint para probarlo | Qué se puede mostrar |
|---|---|---|---|
| Cambio de estado de contrato (máquina de estados) | [`backend/app/modules/contratos/maquina_estados.py`](backend/app/modules/contratos/maquina_estados.py) · `MaquinaEstadosContrato.cambiar_estado` (línea 100) | `PATCH /contratos/{contrato_id}/estado` | Pre: transición permitida y `id_transportista` al adjudicar. Post: `estado` actualizado. Inv: `CANCELADO`/`FINALIZADO` son terminales. |
| Validación de un contrato | [`backend/app/modules/contratos/models.py`](backend/app/modules/contratos/models.py) · `ContratoBase.validar_reglas_de_negocio` (línea 209) | `POST /contratos` | Invariantes: fechas, capacidad del camión, requisitos por tipo de carga, coherencia neto + IVA = total. |
| Creación de contrato | [`backend/app/modules/contratos/service.py`](backend/app/modules/contratos/service.py) · `crear_contrato` (línea 209) | `POST /contratos` | Pre: dador de carga con KYC `APROBADO`. Post: contrato persistido en `BORRADOR`. |
| Postulación a una carga | [`backend/app/modules/subastas/service.py`](backend/app/modules/subastas/service.py) · `postular_a_carga` (línea 233) | `POST /subastas/postular` | Pre: onboarding aprobado, carga existente y en estado disponible. Post: postulación `POSTULADA` y contrato en `EN_POSTULACION`. |
| Adjudicación de subasta | [`backend/app/modules/subastas/service.py`](backend/app/modules/subastas/service.py) · `adjudicar_subasta` (línea 296) | `POST /subastas/adjudicar` | Post "todo o nada": una oferta `SELECCIONADA`, las demás `RECHAZADA`, contrato `ADJUDICADO`. Si falla, nada cambia. |
| Validación de documentos KYC | [`backend/app/modules/onboarding/service.py`](backend/app/modules/onboarding/service.py) · `validar_documento` (línea 356) | `PATCH /onboarding/admin/documentos/{documento_id}/validar` | Pre: documento existente y estado `APROBADO` o `RECHAZADO`. Post: estado persistido. |
| Registro de usuario | [`backend/app/modules/usuarios/service.py`](backend/app/modules/usuarios/service.py) · `registrar_usuario` (línea 98) | `POST /auth/registro` | Pre: email único, password de al menos 6 caracteres. Post: se guarda el hash, nunca la clave en claro. |
| Configuración de reglas de negocio | [`backend/app/modules/configuracion/reglas.py`](backend/app/modules/configuracion/reglas.py) · `ReglasNegocio.actualizar_configuracion` (línea 48) | `PATCH /configuracion` | Pre: IVA entre 0 y 1, tolerancia y anticipación no negativas. Post: configuración vigente retornada. |

Las pruebas que verifican estos contratos están en `backend/tests/contratos/`, `backend/tests/subastas/`, `backend/tests/onboarding/`, `backend/tests/usuarios/` y `backend/tests/configuracion/`. Las pruebas de regresión de la adjudicación son `test_regresion_adjudicar_con_transicion_invalida_no_deja_estado_a_medias` ([`backend/tests/subastas/test_adjudicar_subasta.py`](backend/tests/subastas/test_adjudicar_subasta.py)) y `test_rechazo_carga_en_borrador` ([`backend/tests/subastas/test_postular_a_carga.py`](backend/tests/subastas/test_postular_a_carga.py)).
