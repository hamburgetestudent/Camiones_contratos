# MansoViaje — Camiones Contratos

Plataforma integral multiplataforma orientada a la centralización y digitalización de contratos de transporte terrestre de carga. Conecta a empresas generadoras de carga (**Dadores de Carga**) con **Transportistas** independientes o flotas de camioneros, cubriendo el registro y verificación documental (KYC), publicación de cargas, subastas/postulaciones, adjudicación y seguimiento del ciclo de vida del contrato.

La arquitectura separa claramente las responsabilidades entre cliente y servidor:

* **Frontend (`frontend/`):** Aplicación de escritorio desarrollada con **Electron** y **TypeScript**, con vistas por rol para autenticación, registro y operación comercial.
* **Backend (`main.py`, `routers/`, `services/`, `domain/`, `database/`):** API REST modular construida con **FastAPI** y **Pydantic**, lógica de negocio gobernada por una máquina de estados finitos y persistencia directa en **SQLite** (`camiones.db`).

### Enlaces Rápidos

* **Modelado UML (Entrega 3):** [`docs/modelado/`](docs/modelado/) *(y carpeta de trabajo del equipo [`docs/modelados/`](docs/modelados/))*
* **Panel de administración:** [Panel de administración: navegación, bajas lógicas, auditoría y pruebas](docs/panel-administracion.md)
* **Reglas de Negocio:** [`REGLAS_DE_NEGOCIO.md`](REGLAS_DE_NEGOCIO.md)
* **Documento de Arquitectura:** [`docs_clases/Arquitectura.md`](docs_clases/Arquitectura.md)
* **Guía de Pruebas y Cobertura:** [`tests/README.md`](tests/README.md)
* **Prototipo UI (Figma):** [Contratos camioneros centralizados](https://www.figma.com/design/leoA2Ejoi6cJi13esWBsXQ/Contratos_camioneros_centralizados?node-id=0-1&t=v76XFzFL7hSGl8TY-1)
* **Cronología de cambios e informes:** [Documento en Google Docs](https://docs.google.com/document/d/1p95pKZ2zpQuFnw19-MtfZ5WIhdKAEz30nYLUg9G9B-U/edit?tab=t.0)

---

## Requisitos Previos

Antes de descargar y ejecutar el proyecto, asegúrate de contar con:

* **Git**
* **Python:** `3.10` o superior *(probado en CI con Python `3.12`)*
* **Node.js:** `v20+` *(recomendado `v24` LTS, versión usada en GitHub Actions)* y **npm** `v10+`

---

## Descarga, Instalación y Ejecución (Paso a Paso)

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
   uvicorn main:app --reload --host 127.0.0.1 --port 8000

   # Alternativa directa:
   python main.py
   ```

> Al arrancar por primera vez, el servidor crea e inicializa automáticamente `camiones.db` usando [`database/schema.sql`](database/schema.sql) y carga las cuentas semilla iniciales. La documentación interactiva queda disponible en `http://127.0.0.1:8000/docs`.

### Paso 3 — Instalar e iniciar el Frontend de Escritorio (Terminal 2)

Con el backend ya corriendo en la Terminal 1, abre **una nueva terminal** en la carpeta `Camiones_contratos/` y ejecuta:

```bash
cd frontend
npm install
npm start
```

* `npm start` compila el código TypeScript (`codigos/` ➔ `dist/`), copia las vistas e imágenes y abre la ventana de **Electron** conectada a `http://127.0.0.1:8000`.
* Para desarrollo continuo del archivo principal de Electron puedes ejecutar `npm run dev` (`tsc --watch`).

### Paso 4 — Verificar la instalación y cuentas de prueba

1. Abre `http://127.0.0.1:8000/docs` en tu navegador y confirma los **6 routers activos** cargados por [`main.py`](main.py):
   * `/auth`: Registro, inicio de sesión y consulta de usuarios.
   * `/admin`: Panel administrativo, resumen y bajas lógicas.
   * `/configuracion`: Consulta y actualización de reglas de negocio globales.
   * `/contratos`: Creación, listado y transiciones de estado de contratos.
   * `/onboarding`: Carga documental de transportistas, perfil tributario de dadores y validación KYC.
   * `/subastas`: Exploración de cargas, postulación y adjudicación de ofertas.
2. Las rutas de negocio (`/configuracion`, `/contratos`, `/onboarding`, `/subastas`) y las rutas de `/admin` están protegidas mediante token **JWT Bearer** validado en [`routers/sesion.py`](routers/sesion.py):
   * Para probarlas en **Swagger UI**, ejecuta primero `POST /auth/login` con una cuenta válida, copia el campo `access_token` de la respuesta y pégalo en el botón **Authorize** de Swagger.
   * Desde la aplicación de **Electron**, basta con iniciar sesión en la pantalla de Login.
3. **Cuentas semilla precargadas** (definidas en [`database/conexion.py`](database/conexion.py)):

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

# En Windows PowerShell también puedes usar:
.\run_tests.ps1

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

Para más detalle sobre filtros por módulo y estructura de pruebas, consulta [`tests/README.md`](tests/README.md).

---

## Arquitectura del Sistema

El backend sigue una arquitectura en capas con persistencia directa en SQLite (sin capa DAO intermedia):

```text
Camiones_contratos/
├── domain/                       # Entidades Pydantic, validadores, máquina de estados y reglas
│   ├── maquina_estados.py
│   ├── modelos.py
│   ├── modelos_login.py
│   ├── modelos_onboarding.py
│   ├── modelos_usuario.py
│   ├── postulacion.py
│   └── reglas.py
├── database/                     # Conexión SQLite, esquema idempotente y datos semilla
│   ├── conexion.py
│   └── schema.sql
├── services/                     # Lógica de negocio y transacciones SQLite
│   ├── admin_service.py
│   ├── contrato_service.py
│   ├── dependencies.py
│   ├── onboarding_service.py
│   ├── security.py
│   ├── subasta_service.py
│   └── usuario_service.py
├── routers/                      # Endpoints HTTP FastAPI y validación de sesión JWT
│   ├── admin_router.py
│   ├── auth_router.py
│   ├── comun.py
│   ├── config_router.py
│   ├── contratos_router.py
│   ├── onboarding_router.py
│   ├── sesion.py
│   └── subasta_router.py
├── frontend/                     # Cliente de escritorio Electron + TypeScript
│   ├── codigos/
│   │   ├── main.ts
│   │   ├── imagenes/
│   │   ├── paginas/
│   │   │   ├── Login/
│   │   │   ├── Principal/
│   │   │   ├── Registrar_nuevoUsuario/
│   │   │   ├── panel/
│   │   │   └── panel_funciones/
│   │   └── prueba_coneccion/
│   ├── package.json
│   └── tsconfig.json
├── tests/                        # Suite de pruebas unitarias y de integración
├── docs/                         # Diagramas UML y documentación de modelado
├── main.py                       # Punto de entrada FastAPI y montaje de routers
├── run_tests.py                  # Runner oficial de pruebas y cobertura
├── run_tests.ps1                 # Envoltorio PowerShell para run_tests.py
├── pyproject.toml                # Configuración de Ruff y herramientas Python
└── requirements.txt              # Dependencias del backend
```

### Descripción de Módulos y Capas

* **Capa de Dominio (`domain/`):**
  * `modelos.py`: Modelos Pydantic de contratos (`ContratoBase`, `ContratoCrear`, `ContratoModelo`), `TipoCarga`, `Moneda` y validadores de fechas, capacidad, requerimientos especiales y cuadratura financiera.
  * `modelos_usuario.py`: Modelos de usuarios (`UsuarioBase`, `UsuarioCrear`, `UsuarioModelo`), roles (`RolUsuario`) y estados (`EstadoUsuario`).
  * `modelos_login.py`: Esquemas HTTP de inicio de sesión (`CredencialesLogin`, `LoginEsquema`, `RespuestaLogin`).
  * `modelos_onboarding.py`: Entidades y DTOs de cumplimiento KYC (`DadorCarga`, `DatosFacturacion`, `DocumentoTransportista`, `TipoDocumento`, `EstadoValidacion`).
  * `postulacion.py`: Modelos de ofertas (`PostulacionBase`, `PostulacionCrear`, `PostulacionModelo`), `EstadoPostulacion` y `MaquinaEstadoPostulacion`.
  * `maquina_estados.py`: Clase base genérica `MaquinaEstadosBase` y `MaquinaEstadosContrato` para validar el ciclo de vida del contrato.
  * `reglas.py`: Singleton `ReglasNegocio` con parámetros globales configurables en ejecución (`IVA_PORCENTAJE`, `TOLERANCIA_MAX`, `ANTICIPACION_MIN_H`).
* **Capa de Base de Datos (`database/`):**
  * `conexion.py`: Gestiona conexiones y transacciones exclusivas (`obtener_conexion`, `transaccion_exclusiva`), inicializa el esquema y carga los datos semilla.
  * `schema.sql`: Definición idempotente de tablas e índices SQLite (`usuarios`, `dadores_carga`, `documentos_transportista`, `contratos`, `postulaciones` y tablas operativas de soporte).
* **Capa de Servicios (`services/`):**
  * `usuario_service.py`: Registro, hash SHA-256, autenticación y emisión de tokens JWT.
  * `onboarding_service.py`: Carga documental de transportistas, perfil tributario de dadores y aprobación/rechazo administrativo.
  * `contrato_service.py`: Creación, lectura y transiciones de estado de contratos en SQLite.
  * `subasta_service.py`: Exploración de cargas disponibles, postulaciones y adjudicación atómica ("todo o nada").
  * `admin_service.py`: Consultas administrativas, resúmenes y bajas lógicas.
  * `security.py`: Generación y verificación de tokens JWT Bearer (`HS256`).
  * `dependencies.py`: Instancias compartidas e inyección de dependencias de servicios.
* **Capa de Routers API REST (`routers/`):**
  * `auth_router.py`, `admin_router.py`, `config_router.py`, `contratos_router.py`, `onboarding_router.py`, `subasta_router.py`, junto con `sesion.py` (guardia Bearer y revocación de sesión) y `comun.py` (manejo uniforme de errores HTTP).
* **Capa de Frontend (`frontend/`):**
  * `codigos/main.ts`: Proceso principal de Electron que inicia la ventana y carga `codigos/paginas/Login/index.html`.
  * `codigos/paginas/`: Vistas HTML/CSS/JS para login, registro, vista principal y paneles operativos.

### Ciclo de Vida del Contrato (Máquina de Estados)

Las transiciones son validadas por `domain.maquina_estados.MaquinaEstadosContrato`:

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
        B & C --> D["main.py (FastAPI App)"]
        D --> SSEC["routers/sesion.py (JWT Bearer)"]
        D --> R1["routers/auth_router.py"]
        D --> R2["routers/admin_router.py"]
        D --> R3["routers/contratos_router.py"]
        D --> R4["routers/subasta_router.py"]
        D --> R5["routers/onboarding_router.py"]
        D --> R6["routers/config_router.py"]
    end

    subgraph SERVICES["Capa de Servicios de Negocio"]
        R1 & SSEC --> S1["services/usuario_service.py & security.py"]
        R2 --> S5["services/admin_service.py"]
        R3 --> S2["services/contrato_service.py"]
        R4 --> S3["services/subasta_service.py"]
        R5 --> S4["services/onboarding_service.py"]
    end

    subgraph DOMAIN["Capa de Dominio & Reglas"]
        R6 --> M3["domain/reglas.py (ReglasNegocio)"]
        S2 & S3 --> M1["domain/maquina_estados.py"]
        S1 & S2 & S3 & S4 --> M2["domain/modelos*.py & postulacion.py"]
        M2 --> M3
    end

    subgraph PERSISTENCE["Capa de Persistencia (SQLite)"]
        S1 & S2 & S3 & S4 & S5 --> DBCON["database/conexion.py"]
        DBCON --> SQLITE[("camiones.db<br/>database/schema.sql")]
    end
```

---

## Contratos de Diseño: Precondiciones, Postcondiciones e Invariantes

Las reglas de uso de las operaciones principales están documentadas en el docstring de cada función bajo los encabezados **Precondiciones**, **Postcondiciones** e **Invariantes**. Cuando se viola una precondición, la operación falla con una excepción explícita (`ValueError`, `PermissionError` o `HTTPException`) y **no modifica el estado**.

| Operación | Dónde está el contrato | Endpoint para probarlo | Qué se puede mostrar |
|---|---|---|---|
| Cambio de estado de contrato (máquina de estados) | [`domain/maquina_estados.py`](domain/maquina_estados.py) · `MaquinaEstadosContrato.cambiar_estado` (línea 100) | `PATCH /contratos/{contrato_id}/estado` | Pre: transición permitida y `id_transportista` al adjudicar. Post: `estado` actualizado. Inv: `CANCELADO`/`FINALIZADO` son terminales. |
| Validación de un contrato | [`domain/modelos.py`](domain/modelos.py) · `ContratoBase.validar_reglas_de_negocio` (línea 209) | `POST /contratos` | Invariantes: fechas, capacidad del camión, requisitos por tipo de carga, coherencia neto + IVA = total. |
| Creación de contrato | [`services/contrato_service.py`](services/contrato_service.py) · `crear_contrato` (línea 209) | `POST /contratos` | Pre: dador de carga con KYC `APROBADO`. Post: contrato persistido en `BORRADOR`. |
| Postulación a una carga | [`services/subasta_service.py`](services/subasta_service.py) · `postular_a_carga` (línea 233) | `POST /subastas/postular` | Pre: onboarding aprobado, carga existente y en estado disponible. Post: postulación `POSTULADA` y contrato en `EN_POSTULACION`. |
| Adjudicación de subasta | [`services/subasta_service.py`](services/subasta_service.py) · `adjudicar_subasta` (línea 296) | `POST /subastas/adjudicar` | Post "todo o nada": una oferta `SELECCIONADA`, las demás `RECHAZADA`, contrato `ADJUDICADO`. Si falla, nada cambia. |
| Validación de documentos KYC | [`services/onboarding_service.py`](services/onboarding_service.py) · `validar_documento` (línea 356) | `PATCH /onboarding/admin/documentos/{documento_id}/validar` | Pre: documento existente y estado `APROBADO` o `RECHAZADO`. Post: estado persistido. |
| Registro de usuario | [`services/usuario_service.py`](services/usuario_service.py) · `registrar_usuario` (línea 98) | `POST /auth/registro` | Pre: email único, password de al menos 6 caracteres. Post: se guarda el hash, nunca la clave en claro. |
| Configuración de reglas de negocio | [`domain/reglas.py`](domain/reglas.py) · `ReglasNegocio.actualizar_configuracion` (línea 48) | `PATCH /configuracion` | Pre: IVA entre 0 y 1, tolerancia y anticipación no negativas. Post: configuración vigente retornada. |

Las pruebas que verifican estos contratos están en `tests/contratos/`, `tests/subastas/`, `tests/onboarding/`, `tests/usuarios/` y `tests/configuracion/`. Las pruebas de regresión de la adjudicación son `test_regresion_adjudicar_con_transicion_invalida_no_deja_estado_a_medias` ([`tests/subastas/test_adjudicar_subasta.py`](tests/subastas/test_adjudicar_subasta.py)) y `test_rechazo_carga_en_borrador` ([`tests/subastas/test_postular_a_carga.py`](tests/subastas/test_postular_a_carga.py)).

---

## Contexto del Proyecto (Hito 1 y Equipo)

### Actores y Arquetipos

* **Dador de Carga (Generador/Cliente):** Empresas consolidadas, PYMEs, brokers o particulares que publican necesidades de transporte (origen, destino, tipo de carga, fechas y requerimientos técnicos), evalúan postulaciones y adjudican el contrato.
* **Transportista (Oferente):** Conductores independientes o empresas de transporte que cargan su documentación de habilitación (KYC) y postulan con tarifas competitivas a las cargas publicadas.
* **Administrador Backoffice:** Revisa y aprueba/rechaza perfiles tributarios de dadores, valida documentos de transportistas y gestiona bajas lógicas e indicadores en el panel administrativo.

### Historias de Usuario Principales

| ID | Nombre | Issue |
|---|---|---|
| `HU-IAM-01` | Registro de Usuarios por Rol | #50 |
| `HU-IAM-02` | Inicio de Sesión y Emisión de Credenciales | #51 |
| `HU-IAM-03` | Interfaz de Inicio de Sesión y Autenticación Federada (UI) | #52 |
| `HU-ONB-01` | Carga y Reemplazo de Documentos del Transportista | #53 |
| `HU-UI-01` | Configuración y Empaquetado de la Aplicación Electron | #54 |
| `HU-ONB-02` | Consulta de Estado Global de Habilitación del Transportista | #55 |
| `HU-CFG-02` | Modificación en Caliente de Políticas del Negocio | #56 |
| `HU-ONB-03` | Registro y Actualización del Perfil Tributario del Dador de Carga | #57 |
| `HU-ONB-04` | Panel Backoffice de Revisión y Validación Documental | #58 |
| `HU-CFG-01` | Consulta de Configuración de Negocio Vigente | #59 |

### Mapa de Épicas del Dominio

```mermaid
mindmap
  root((Plataforma Camiones))
    EP-01: Autenticación, Identidad y Accesos (IAM)
      Registro por rol
      Inicio de sesión y tokens
      Sesión vigente y cierre
    EP-02: Onboarding y Cumplimiento Legal (KYC & Fleet Compliance)
      Carga documental transportista
      Verificación tributaria dador
      Panel backoffice de aprobación
      Gating de seguridad y bloqueos
    EP-03: Gestión y Ciclo de Vida del Contrato de Carga
      Publicación y especificaciones
      Validación de carga y capacidades
      Cálculo financiero e IVA
      Máquina de estados del contrato
    EP-04: Motor de Postulaciones y Subasta de Fletes
      Buscador de cargas disponibles
      Postulación de transportistas
      Revisión y adjudicación
    EP-05: Seguimiento Operacional, Entrega y Disputas
      Confirmación de tránsito
      Constancia de entrega
      Gestión y resolución de disputas
    EP-06: Configuración Global y Reglas de Negocio
      Parámetros tributarios y tolerancias
      Tiempos de anticipación
      Auditoría de configuraciones
    EP-07: Experiencia de Usuario y Cliente de Escritorio (Desktop Electron)
      Interfaz Electron modular
      Dashboards por rol
      Panel administrativo
```

### Responsabilidades del Equipo

| Integrante | Rol | Ítems de la rúbrica a cargo |
|---|---|---|
| Benjamín Ponce | PM | 1.2 |
| Cristian Palma | Backend | 1.2, Issue del profesor |
| Santiago Sanchez | Backend | 1.2, 2.1, 2.2 |
| Fabian Ahumada | Backend | 1.1, 2.4 |
| Gabriel Alvares | Frontend | 2.3, 2.4 |

## Evidencia del Hito 3

- [Criterio 4: Modularización de las interfaces y dependencias](docs/criterio-4-modularizacion.md)
