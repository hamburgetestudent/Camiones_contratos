# Modularización de la estructura y las responsabilidades (Hito 3 · Criterio 3)

**Proyecto:** MansoViaje — Camiones Contratos  
**Asignatura / Unidad:** Taller de Programación Avanzada ISF224 · Unidad 3 (Hito 3)  
**Criterio evaluado:** Criterio 3 — Modularización de la estructura y las responsabilidades  
**Rama de trabajo:** `feat/criterio3-modularizacion`  
**Base de comparación:** [`7a34c32`](https://github.com/hamburgetestudent/Camiones_contratos/commit/7a34c32) (`origin/Dev`)  

---

## 1. Alcance y método de modularización elegido

La solución completa reside en un único repositorio propio (`Camiones_contratos`) que agrupa los dos subsistemas de la plataforma: el **Backend** (API REST en FastAPI/Python con SQLite) y el **Frontend** (cliente de escritorio Electron + HTML/CSS/JS/TypeScript). Se revisaron los límites de ambos subsistemas y se aplicó el criterio más adecuado a cada tecnología:

| Subsistema | Método elegido | Justificación |
|---|---|---|
| **Backend** (`routers/`, `services/`, `domain/`, `dao/`, `database/`) | **Por capas** | Separa explícitamente el transporte HTTP (`routers/`), la orquestación de casos de uso (`services/`), las reglas puras del negocio y máquinas de estado (`domain/`), las consultas SQL por entidad (`dao/`) y la conexión/esquema SQLite (`database/`). Permite probar reglas de dominio sin levantar FastAPI ni BD, evita filtrar SQL en endpoints o servicios y mantiene un punto único de inyección de dependencias en `services/dependencies.py`. |
| **Frontend** (`frontend/codigos/`) | **Combinado (por funcionalidades/vistas + módulo compartido `paginas/comun/`)** | Agrupa la vista, estilos y controlador de cada flujo de usuario en su propia carpeta (`Login/`, `Registrar_nuevoUsuario/`, `Principal/`, `Crear_contrato/` y `panel/`, subdividido internamente por rol en `administracion.js`, `dador.js`, `transportista.js` y `roles.js`), mientras centraliza el código transversal (`tema.css`, `iconos.js` y `api.js`) en `paginas/comun/`. Facilita modificar una pantalla sin afectar al resto y cambia la comunicación HTTP o el manejo de sesión en un solo archivo. |

---

## 2. Estructura antes y después

### Árbol breve de las áreas intervenidas

**Antes (`7a34c32` — `Dev`):**

```text
Camiones_contratos/
├── 2.ts                                 # Ejercicio ajeno al proyecto (Unidad 2.1)
├── routers/
│   └── sesion.py                        # Dependencias Bearer + 3 consultas SQL directas
├── services/
│   ├── admin_service.py                 # Reglas administrativas + 9 consultas SQL directas
│   ├── dependencies.py                  # Sin DAO de sesiones ni de administración
│   └── security.py                      # (sin sesion_service.py)
├── dao/
│   ├── base_dao.py
│   ├── contrato_dao.py
│   ├── onboarding_dao.py
│   ├── postulacion_dao.py
│   └── usuario_dao.py                   # (sin sesion_dao.py ni admin_dao.py)
└── frontend/codigos/
    ├── paginas/
    │   ├── comun/
    │   │   ├── iconos.js
    │   │   └── tema.css                 # (sin cliente HTTP/sesión compartido)
    │   ├── Login/script.js              # Define API_BASE_URL, fetch y localStorage propios
    │   ├── Registrar_nuevoUsuario/registro.js  # Define API_BASE_URL y extraerMensajeError propios
    │   ├── Principal/principal.js       # Define API_BASE_URL, volverLogin y solicitarApi propios
    │   ├── Crear_contrato/crear_contrato.js    # Define API_BASE_URL, volverALogin y solicitarApi propios
    │   ├── panel/panel.js               # Define API, volverLogin, extraerDetalleError y api propios
    │   └── panel_funciones/             # Vista obsoleta sin referencias activas
    └── prueba_coneccion/                # Prueba manual obsoleta sin referencias activas
```

**Después (`feat/criterio3-modularizacion`):**

```text
Camiones_contratos/
├── routers/
│   └── sesion.py                        # Solo HTTPBearer, errores 401/403 y delegación al servicio
├── services/
│   ├── admin_service.py                 # Solo reglas administrativas, auditoría y máquina de estados
│   ├── dependencies.py                  # Inyecta todos los DAO (incluidos sesion_dao y admin_dao)
│   ├── security.py
│   └── sesion_service.py                # [NUEVO] Vigencia y revocación de sesiones JWT
├── dao/
│   ├── admin_dao.py                     # [NUEVO] Consultas administrativas y tabla acciones_admin
│   ├── base_dao.py
│   ├── contrato_dao.py
│   ├── onboarding_dao.py
│   ├── postulacion_dao.py
│   ├── sesion_dao.py                    # [NUEVO] Consultas de tabla sesiones_cerradas
│   └── usuario_dao.py
└── frontend/codigos/
    └── paginas/
        ├── comun/
        │   ├── api.js                   # [NUEVO] Cliente HTTP, URL base, errores y sesión (window.MVApi)
        │   ├── iconos.js
        │   └── tema.css
        ├── Login/script.js              # Delega HTTP y sesión en window.MVApi
        ├── Registrar_nuevoUsuario/registro.js  # Delega HTTP y errores en window.MVApi
        ├── Principal/principal.js       # Delega HTTP y sesión en window.MVApi
        ├── Crear_contrato/crear_contrato.js    # Delega HTTP y sesión en window.MVApi
        └── panel/panel.js               # Delega en window.MVApi conservando firma api() para roles
```

---

## 3. Ubicación de responsabilidades, operaciones públicas y dependencias

| Capa / Módulo | Propósito y ubicación de responsabilidades | Operaciones públicas principales | Dependencias |
|---|---|---|---|
| **Presentación Frontend — Vistas** (`frontend/codigos/paginas/{Login,Registrar_nuevoUsuario,Principal,Crear_contrato,panel}/`) | Presentación HTML/CSS, validación de formularios, interacción DOM y navegación por rol (`administracion.js`, `dador.js`, `transportista.js`, `roles.js`). | Eventos de pantalla, `vistaAdmin`, `vistaDador`, `vistaTransportista`, `api()` en `panel.js`. | `comun/api.js` (`window.MVApi`), `comun/iconos.js`, `comun/tema.css`. |
| **Código compartido Frontend** (`frontend/codigos/paginas/comun/api.js`) | Resolución única de URL del backend (Electron `file://` y modo web HTTP), almacenamiento de sesión en `localStorage`, parseo de errores FastAPI y envío de solicitudes autenticadas con manejo de `401`. | `window.MVApi`: `obtenerBaseUrl`, `obtenerToken`, `guardarSesion`, `limpiarSesion`, `volverALogin`, `extraerMensajeError`, `solicitarPublica`, `solicitar`, `cerrarSesionEnServidor`. | APIs estándar del navegador (`fetch`, `localStorage`, `window.location`). |
| **Presentación HTTP Backend** (`routers/`) | Endpoints FastAPI, traducción de excepciones (`routers/comun.py`) y guardias de autenticación/rol (`routers/sesion.py`). Sin SQL. | `usuario_actual`, `administrador_actual`, `cerrar_sesion` (`routers/sesion.py`) y los 6 routers montados en `main.py`. | `fastapi`, `domain/`, `services/`. |
| **Servicios de aplicación** (`services/`) | Orquestación de casos de uso, seguridad JWT (`security.py`), construcción de respuesta de login (`respuesta_login.py`), vigencia/revocación de sesiones (`sesion_service.py`) y reglas administrativas (`admin_service.py`). Sin SQL directo. | `resolver_usuario_desde_token`, `revocar_token_sesion`, `huella_token` (`sesion_service.py`); `listar_elementos`, `eliminar`, `cancelar_contrato`, `historial`, `resumen` (`admin_service.py`). | `domain/`, `dao/`, `services/security.py`, `services/dependencies.py`. |
| **Reglas de negocio / Dominio** (`domain/`) | Entidades Pydantic, validadores de negocio, máquina de estados (`maquina_estados.py`, `postulacion.py`) y parámetros globales (`reglas.py`). Sin SQL ni FastAPI. | `MaquinaEstadosContrato`, `MaquinaEstadoPostulacion`, `ReglasNegocio`, modelos `Contrato*`, `Usuario*`, `Postulacion*`. | Solo librería estándar y `pydantic`. |
| **Acceso a datos** (`dao/` y `database/`) | Todo el SQL del proyecto encapsulado por entidad/área (`usuario_dao`, `contrato_dao`, `postulacion_dao`, `onboarding_dao`, `sesion_dao`, `admin_dao`) más gestión de conexiones/transacciones y esquema (`database/conexion.py`, `database/schema.sql`). | `SesionDAO` (`esta_revocada`, `revocar_y_purgar`), `AdminDAO` (`listar_elementos`, `obtener_actor_vigente`, `obtener_elemento_por_id`, `marcar_eliminado`, `registrar_accion`, `listar_historial`, `obtener_resumen`). | `sqlite3`, `database/conexion.py`, `domain/`. |

---

## 4. Código que cambió de ubicación (mejoras aplicadas)

1. **Sesiones JWT (`routers/sesion.py` ➔ `services/sesion_service.py` + `dao/sesion_dao.py`):**
   * **Antes:** `routers/sesion.py` importaba `database.conexion.obtener_conexion` y ejecutaba 3 sentencias SQL sobre `sesiones_cerradas` dentro de la capa HTTP.
   * **Después:** [`dao/sesion_dao.py`](../dao/sesion_dao.py) encapsula las consultas sobre `sesiones_cerradas`, [`services/sesion_service.py`](../services/sesion_service.py) coordina la decodificación JWT y verificación de vigencia/revocación, y [`routers/sesion.py`](../routers/sesion.py) solo procesa `HTTPBearer` y traduce fallos a HTTP `401`/`403`.
2. **Administración y auditoría (`services/admin_service.py` ➔ `dao/admin_dao.py`):**
   * **Antes:** Tras la migración a la capa DAO del resto de servicios, `services/admin_service.py` era el único servicio que mantenía 9 consultas SQL directas mezcladas con reglas administrativas.
   * **Después:** [`dao/admin_dao.py`](../dao/admin_dao.py) concentra las consultas de listado, actor vigente, bajas lógicas, inserción/consulta de `acciones_admin` y resumen transaccional. [`services/admin_service.py`](../services/admin_service.py) conserva sus reglas y exactamente las mismas operaciones públicas, logrando **0 consultas SQL fuera de `dao/` y `database/`**.
3. **Cliente HTTP y sesión compartidos en Frontend (`5` vistas ➔ `frontend/codigos/paginas/comun/api.js`):**
   * **Antes:** La resolución de `API_BASE_URL`, el borrado de claves de `localStorage`, el parseo del campo `detail` de FastAPI y los envoltorios `fetch` con `Authorization: Bearer` estaban duplicados en `Login/script.js`, `Registrar_nuevoUsuario/registro.js`, `Principal/principal.js`, `Crear_contrato/crear_contrato.js` y `panel/panel.js`.
   * **Después:** [`frontend/codigos/paginas/comun/api.js`](../frontend/codigos/paginas/comun/api.js) expone `window.MVApi` y preserva la resolución automática tanto en Electron (`file://` ➔ `http://127.0.0.1:8000`) como servido por FastAPI (`window.location.origin`) o sobrescrito en pruebas (`window.API_BASE_URL`). Las 5 vistas cargan `../comun/api.js` y delegan en él.
4. **Desacoplamiento de errores HTTP en `UsuarioService` (`services/usuario_service.py` ➔ `routers/auth_router.py`):**
   * **Antes:** `UsuarioService` importaba `fastapi.HTTPException` y decidía directamente los códigos HTTP (`400`, `401`, `404`) ante correo duplicado, credenciales inválidas, campos vacíos o usuario inexistente.
   * **Después:** `UsuarioService` comunica errores puros de negocio (`CorreoYaRegistradoError`, `CredencialesInvalidasError`, `UsuarioNoEncontradoError`, `ValueError`) sin importar `fastapi`, y [`routers/auth_router.py`](../routers/auth_router.py) los traduce mediante `_ejecutar_usuario_http` conservando exactamente los mismos códigos y mensajes HTTP (verificado en pruebas del servicio y del endpoint en [`tests/usuarios/test_router_auth.py`](../tests/usuarios/test_router_auth.py)).
5. **Limpieza estructural (`454781b`):**
   * Se retiraron `2.ts` (ejercicio académico ajeno a la plataforma), `frontend/codigos/paginas/panel_funciones/` (vista reemplazada por `panel/` sin referencias) y `frontend/codigos/prueba_coneccion/` (script exploratorio obsoleto).

---

## 5. Comprobación antes y después

### Caso representativo y comandos ejecutados

El caso representativo elegido recorre **autenticación Bearer, revocación de sesión, reglas administrativas, baja lógica/cancelación y auditoría** (`tests/test_panel_admin.py` + `tests/seguridad/test_sesion_service.py`), junto con la suite completa del backend, el linter y la verificación estática del frontend:

```bash
# 1. Caso representativo (panel administrativo, permisos HTTP y revocación de sesiones)
python -m unittest tests.test_panel_admin tests.seguridad.test_sesion_service -v

# 2. Suite completa del backend
python -m unittest discover -s tests -t .

# 3. Linter backend
ruff check .

# 4. Verificación de sintaxis, formato y tipos en frontend
node --check frontend/codigos/paginas/comun/api.js frontend/codigos/paginas/Login/script.js frontend/codigos/paginas/Registrar_nuevoUsuario/registro.js frontend/codigos/paginas/Principal/principal.js frontend/codigos/paginas/Crear_contrato/crear_contrato.js frontend/codigos/paginas/panel/panel.js
cd frontend && npx tsc --noEmit
```

### Resultados comparados

| Indicador / Verificación | Antes (`7a34c32`, `Dev`) | Después (`feat/criterio3-modularizacion`) |
|---|---:|---:|
| Consultas SQL directas (`conn.execute` / `obtener_conexion`) en `routers/` | `3` (`routers/sesion.py`) | `0` |
| Consultas SQL directas (`conn.execute` / `obtener_conexion` / `transaccion_exclusiva`) en `services/` | `9` (`services/admin_service.py`) | `0` |
| Consultas SQL directas en `domain/` | `0` | `0` |
| Dependencias/lanzamientos de `HTTPException` (`fastapi`) en `services/` | `7` (`services/usuario_service.py`) | `0` |
| Definiciones duplicadas de URL base (`http://127.0.0.1:8000`) en `frontend/codigos/paginas/` | `5` (una por vista) | `1` (`paginas/comun/api.js`) |
| Archivos ajenos o carpetas de vistas obsoletas (`2.ts`, `panel_funciones/`, `prueba_coneccion/`) | `3` | `0` |
| Caso representativo (`tests.test_panel_admin` + `tests.seguridad.test_sesion_service`) | `10` OK (`2.115s`) *(sin pruebas unitarias aisladas de sesión)* | `15` OK (`2.471s`) *(10 de panel/HTTP + 5 nuevas de `sesion_service`)* |
| Suite completa backend (`unittest discover`) | `222` de `222` OK (`18.850s`) | `231` de `231` OK (`21.832s`) |
| Linter backend (`ruff check .`) | `All checks passed!` | `All checks passed!` |
| Frontend (`npx tsc --noEmit` y `node --check`) | `0` errores | `0` errores |

---

## 6. Cambios realizados (trazabilidad de commits)

Todos los cambios se aplicaron en pasos pequeños sobre la rama `feat/criterio3-modularizacion` creada desde `Dev` (`7a34c32`), ejecutando las pruebas tras cada transformación:

| Commit | Mensaje | Alcance |
|---|---|---|
| `5c8a303` | `feat(sesiones): crear SesionDAO, servicio de sesiones JWT y pruebas unitarias` | Crea `dao/sesion_dao.py`, `services/sesion_service.py` y `tests/seguridad/test_sesion_service.py`; registra `SesionDAO` en `dao/__init__.py` y `services/dependencies.py`. |
| `585c3c5` | `refactor(routers): delegar validación y cierre de sesión desde routers/sesion.py al servicio` | Elimina las 3 consultas SQL directas y el import de `database.conexion` en `routers/sesion.py`, delegando en `services/sesion_service.py`. |
| `fd24ee5` | `refactor(admin): extraer consultas SQL de admin_service hacia dao/admin_dao` | Crea `dao/admin_dao.py`, delega el SQL desde `services/admin_service.py` y registra `AdminDAO` en `dao/__init__.py` y `services/dependencies.py`. |
| `dd78243` | `feat(frontend): incorporar cliente HTTP y gestión de sesión compartidos en comun/api.js` | Crea `frontend/codigos/paginas/comun/api.js` (`window.MVApi`). |
| `4ea0782` | `refactor(frontend-auth): conectar vistas de Login y Registro al módulo comun/api.js` | Conecta `Login/` y `Registrar_nuevoUsuario/` al cliente compartido `window.MVApi`. |
| `8c8a7b3` | `refactor(frontend-vistas): centralizar llamadas autenticadas de Catálogo, Crear contrato y Panel en comun/api.js` | Conecta `Principal/`, `Crear_contrato/` y `panel/` a `window.MVApi`. |
| `454781b` | `chore(limpieza): eliminar archivo de ejercicio 2.ts y vistas obsoletas del frontend` | Elimina `2.ts`, `frontend/codigos/paginas/panel_funciones/` y `frontend/codigos/prueba_coneccion/`. |
| `9ffd1fa` | `docs(criterio-3): registrar modularización de estructura, responsabilidades y trazabilidad en docs y README` | Agrega este documento y actualiza la arquitectura y enlaces del Hito 3 en [`README.md`](../README.md). |
| `refactor(usuarios)` | `refactor(usuarios): desacoplar errores de negocio de UsuarioService de las respuestas HTTP en auth_router` | Elimina `HTTPException` de `services/usuario_service.py`, traduce errores en `routers/auth_router.py` y verifica servicio + endpoints HTTP. |
| Commit de documentación | `docs(usuarios): actualizar contrato de UsuarioService y evidencias de modularización` | Actualiza `docs/contrato-usuario-service.md` y este registro de modularización. |
