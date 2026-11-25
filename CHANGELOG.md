# Changelog — MansoViaje · Camiones Contratos

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/). Este documento reúne las notas de la entrega, la verificación del flujo principal (rúbrica 6 y apartado «Integración y verificación» del punto 7) y el cierre del paquete (rúbrica 7).

## [1.0.0] — Entrega Hito 3 · 2026-11-25

### Identificación del paquete

| Campo | Valor |
|---|---|
| Producto | MansoViaje — Camiones Contratos (API FastAPI + cliente Electron) |
| Versión | `1.0.0` (`package.json` y `frontend/package.json`) |
| Rama de la entrega | `ayudante_taller` (integra `Dev`) |
| Commit de referencia | el commit que lleve la etiqueta `v1.0.0` (ver *Pendientes*) |
| Repositorio | https://github.com/hamburgetestudent/Camiones_contratos |
| Entorno verificado | Windows 11, Python 3.14.8 (CI: Python 3.12), SQLite, Node 24 en CI |

### Agregado

- Capa **DAO** SQLite (`dao/`) para usuarios, onboarding, contratos y postulaciones; los servicios la reciben por inyección ([`services/dependencies.py`](services/dependencies.py)).
- Modularización de interfaces y dependencias de autenticación ([criterio 4](docs/criterio-4-modularizacion.md)).
- Revisión de la dependencia externa `email-validator` ([informe](docs/revision-dependencia-email-validator.md)) y rango acotado en `requirements.txt` (`>=2.2.0,<3`).
- Script de verificación del flujo integrado [`scripts/verificar_flujo_integrado.py`](scripts/verificar_flujo_integrado.py) (tres casos, 18 comprobaciones).
- Rediseño del frontend de escritorio y panel de administración ([detalle](docs/panel-administracion.md)).

### Cambiado

- Tres refactorizaciones con comportamiento conservado: decisión administrativa unificada, estado y faltantes del transportista, normalización del correo ([diagnóstico y mediciones](docs/hito3-intervenciones.md)).
- Validación de correo: de una regex a `email-validator.validate_email` con `check_deliverability=False` (rechaza `a..b@x.cl` o `.a@x.cl`, que la regex aceptaba).

### Pruebas, cobertura e integración continua (esta entrega)

| Verificación | Comando | Resultado (2026-11-25) |
|---|---|---|
| Suite unittest | `python -m unittest discover -s tests -t .` | 222 pruebas, **OK** |
| Cobertura (líneas + ramas) | `coverage run -m unittest discover -s tests -t .` y `coverage report` | **93,3 %** total (`database`, `domain`, `routers`, `services`; configuración en [`.coveragerc`](.coveragerc)) |
| Linter | `ruff check .` | Sin hallazgos |
| Flujo integrado | `python scripts/verificar_flujo_integrado.py` | **18 de 18** comprobaciones OK |
| CI | [`.github/workflows/tests.yml`](.github/workflows/tests.yml) | Ejecuta ruff, pytest con cobertura (sube `coverage.xml` como artefacto) y typecheck del frontend en cada push a `main` y en cada pull request |

> El enlace a la ejecución concreta de CI de esta entrega se agrega en *Pendientes* (no pude consultarlo desde este entorno).

---

## Integración y verificación del flujo principal

### Diagrama del flujo

Flujo principal: un dador de carga publica un contrato, un transportista aprobado postula y el dador adjudica.

```mermaid
sequenceDiagram
    actor D as Dador de carga
    actor T as Transportista
    participant UI as Electron / Swagger (cliente HTTP)
    participant API as FastAPI + routers
    participant V as Pydantic + email-validator
    participant SV as Servicios + máquina de estados
    participant DAO as DAO SQLite
    participant DB as camiones.db (schema.sql)

    D->>UI: Credenciales
    UI->>API: POST /auth/login (email, password)
    API->>SV: iniciar_sesion
    SV->>DAO: buscar usuario por correo normalizado
    DAO->>DB: SELECT
    DB-->>DAO: fila o nada
    SV-->>API: JWT Bearer HS256 (o 401)
    API-->>UI: access_token, rol

    D->>UI: Datos del contrato
    UI->>API: POST /contratos (Bearer)
    API->>V: validar ContratoCrear (fechas, capacidad, IVA)
    V-->>API: modelo válido (o 422/400, sin escribir)
    API->>SV: crear_contrato
    SV->>DAO: dador APROBADO? e INSERT contrato BORRADOR
    DAO->>DB: transacción
    API-->>UI: 201 contrato BORRADOR (o 403)

    D->>UI: Publicar
    UI->>API: PATCH /contratos/{id}/estado = PUBLICADO
    API->>SV: MaquinaEstadosContrato.cambiar_estado
    SV->>DAO: UPDATE estado
    API-->>UI: 200 PUBLICADO (o 400 si la transición no existe)

    T->>UI: Explorar y ofertar
    UI->>API: GET /subastas/cargas · POST /subastas/postular
    API->>SV: postular_a_carga (onboarding aprobado, carga disponible)
    SV->>DAO: INSERT postulación y contrato → EN_POSTULACION
    API-->>UI: 201 POSTULADA (o 404/400)

    D->>UI: Elegir oferta
    UI->>API: POST /subastas/adjudicar
    API->>SV: adjudicar_subasta (todo o nada)
    SV->>DAO: una SELECCIONADA, resto RECHAZADA, contrato ADJUDICADO
    DAO->>DB: una sola transacción exclusiva
    API-->>UI: 200 SELECCIONADA
```

### Participantes

| Tipo | Elemento | Papel en el flujo |
|---|---|---|
| Módulos propios | `routers/`, `services/`, `domain/`, `dao/`, `database/` | Entrada HTTP, reglas de negocio, validación, acceso a datos, conexión y esquema |
| Módulo propio | `frontend/` (Electron + TypeScript) | Cliente de escritorio; consume la API por HTTP |
| Dependencias externas | FastAPI, uvicorn, Pydantic, `email-validator`, `python-dotenv` | Servidor, validación de esquemas y de correo (el detalle de `email-validator` está en su [informe](docs/revision-dependencia-email-validator.md)) |
| Recursos del entorno | `camiones.db` (o `SQLITE_DB_PATH`), `database/schema.sql`, `JWT_SECRET_KEY`, puerto 8000 | Persistencia, esquema, firma de tokens y red local |

### Datos que se intercambian

- **Cliente → API:** JSON con credenciales, contrato (`ContratoCrear`), postulación (`PostulacionCrear`) y adjudicación (`carga_id`, `postulacion_id`); token `Authorization: Bearer`.
- **API → cliente:** modelos de respuesta (`RespuestaLogin`, `ContratoModelo`, `PostulacionModelo`) o `{"detail": ...}` en errores.
- **Servicios ↔ DAO:** modelos de dominio y una conexión SQLite abierta, para combinar varios DAO en una transacción.

### Manejo de errores en las conexiones

| Conexión | Falla | Respuesta | Estado del sistema |
|---|---|---|---|
| Cliente → API | Sin token, token inválido o sesión cerrada | `401` con `WWW-Authenticate: Bearer` | Sin cambios |
| Cliente → API | Rol insuficiente o dador no aprobado | `403` | Sin cambios |
| API → Pydantic | Esquema o regla de negocio inválida | `422` / `400` con el detalle | No se escribe nada |
| API → servicios | Recurso inexistente | `404` | Sin cambios |
| API → servicios | Transición no permitida u operación inválida | `400` | Estado anterior conservado |
| Servicios → SQLite | Fallo dentro de una transacción (p. ej. adjudicación) | Excepción y *rollback* | «Todo o nada»: no queda estado a medias |
| Servicios → archivo `.db` | El archivo desaparece | `schema.sql` se reaplica al abrir la siguiente conexión (`_asegurar_esquema`) | Base nueva y vacía, el servidor sigue respondiendo |

### Los tres casos ejecutados

Entorno de todos los casos: Windows 11, Python 3.14.8, FastAPI `TestClient` sobre la aplicación real (`main.app`) y una base SQLite temporal inicializada con las cuentas semilla. No se simula ningún servicio propio ni externo. La salida completa se reproduce con `python scripts/verificar_flujo_integrado.py`.

#### Caso 1 · Datos válidos

| Paso | Esperado | Obtenido |
|---|---|---|
| 1.1 `POST /auth/registro` (`ana@empresa.cl`) | 201 | 201 ✅ |
| 1.2 `POST /auth/login` (dador aprobado) | 200 + token Bearer | token emitido ✅ |
| 1.3 `POST /contratos` | 201, `BORRADOR` | 201, `BORRADOR` ✅ |
| 1.4 `PATCH /contratos/{id}/estado` → `PUBLICADO` | 200, `PUBLICADO` | 200, `PUBLICADO` ✅ |
| 1.5 `GET /subastas/cargas` | la carga aparece | aparece ✅ |
| 1.6 `POST /subastas/postular` | 201, `POSTULADA` | 201, `POSTULADA` ✅ |
| 1.7 `POST /subastas/adjudicar` | 200, `SELECCIONADA` | 200, `SELECCIONADA` ✅ |
| 1.8 `GET /contratos/{id}` | `ADJUDICADO` | `ADJUDICADO` ✅ |

#### Caso 2 · Datos inválidos

| Paso | Esperado | Obtenido |
|---|---|---|
| 2.1 Registro con `ana@@empresa.cl` | 422 | 422 ✅ |
| 2.2 Contrato con neto + IVA ≠ total | 400 o 422 | 400/422 ✅ |
| 2.3 Contrato con peso mayor que la capacidad del camión | 400 o 422 | 400/422 ✅ |
| 2.4 Login con clave errónea | 401 | 401 ✅ |
| 2.5 Estado conservado | `usuarios=6`, `contratos=1` | `usuarios=6`, `contratos=1` ✅ |

#### Caso 3 · Recurso ausente

| Paso | Esperado | Obtenido |
|---|---|---|
| 3.1 `GET /contratos/{id inexistente}` | 404 | 404 ✅ |
| 3.2 `POST /subastas/postular` a una carga inexistente | 404 | 404 ✅ |
| 3.3 `GET /contratos` sin token | 401 o 403 | 401 ✅ |
| 3.4 Se elimina `integracion.db` en caliente y se hace login | 401, sin caída del servidor | 401 ✅ |
| 3.5 Después del paso anterior | el archivo se recrea con su esquema | existe de nuevo ✅ |

**Fallos corregidos durante la verificación:** el script se corrió varias veces hasta quedar en verde; los errores eran del propio script (conexiones de apoyo sin cerrar que en Windows impedían borrar el `.db`, y una tupla de registro mal indexada). No se encontraron fallos en el backend que bloquearan el flujo.

**Qué no se simuló y qué queda pendiente:** el cliente Electron no se ejecutó en esta verificación (solo la API, que es lo que consume). El flujo de aprobación KYC por el administrador se cubre con las cuentas semilla ya aprobadas y con las pruebas de `tests/onboarding/`, no con una llamada dentro del flujo de arriba.

---

## Paquete y cierre

### Cómo ejecutar la entrega (otro equipo)

Los pasos completos están en el [README](README.md#descarga-instalación-y-ejecución-paso-a-paso). Resumen mínimo:

```bash
git clone https://github.com/hamburgetestudent/Camiones_contratos.git
cd Camiones_contratos
git checkout v1.0.0          # cuando la etiqueta esté publicada
python -m venv .venv && .venv/Scripts/activate      # Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 127.0.0.1 --port 8000       # Terminal 1
cd frontend && npm install && npm start             # Terminal 2
python scripts/verificar_flujo_integrado.py         # comprobación rápida del flujo
```

### Cómo extenderlo

La guía está en la sección «Cómo extender el proyecto» del [README](README.md#cómo-extender-el-proyecto).

### Decisiones

| Decisión | Motivo |
|---|---|
| Capa DAO con conexión inyectada | Permite que un servicio combine varios DAO en una transacción y garantiza la adjudicación «todo o nada» |
| `email-validator` en vez de regex, con `check_deliverability=False` | Reglas reales de correo sin depender de DNS ni de red |
| Rango `>=2.2.0,<3` para `email-validator` | Excluye la 2.1.0 retirada y bloquea saltos de versión mayor sin revisión |
| SQLite con esquema idempotente | Cero configuración para quien ejecuta la entrega; el archivo se recrea si falta |
| Verificación de integración sobre la API real y una base temporal | Prueba el flujo completo sin tocar `camiones.db` ni simular servicios |

### Evidencias

- Diagnóstico, tres refactorizaciones y mediciones: [docs/hito3-intervenciones.md](docs/hito3-intervenciones.md)
- Modularización: [docs/criterio-4-modularizacion.md](docs/criterio-4-modularizacion.md)
- Dependencia externa: [docs/revision-dependencia-email-validator.md](docs/revision-dependencia-email-validator.md)
- Contratos de diseño del servicio de usuarios: [docs/contrato-usuario-service.md](docs/contrato-usuario-service.md)
- Panel de administración: [docs/panel-administracion.md](docs/panel-administracion.md)
- Modelado UML: [docs/modelados/](docs/modelados/) (secuencia de «crear contrato» en [3-secuencia.md](docs/modelados/3-secuencia.md))
- Guía de pruebas: [tests/README.md](tests/README.md)

### Pendientes

- [ ] **Crear y publicar la etiqueta `v1.0.0`** sobre el commit final (`git tag -a v1.0.0 -m "Entrega Hito 3"` y `git push origin v1.0.0`) y, si se desea, un *Release* en GitHub con estas notas.
- [ ] **Alinear la versión de la API:** `main.py` declara `version="0.1.4"` mientras los `package.json` declaran `1.0.0`.
- [ ] **Enlazar la ejecución de CI** de la rama o del pull request de la entrega (Actions → Tests).
- [ ] Ejecutar `npm start` en una máquina limpia y registrar el resultado del cliente Electron contra el backend.
- [ ] Llevar la verificación del flujo a CI (hoy solo se ejecuta a mano).

---

## Historial anterior

- **2026-11-24** — Capa DAO para contratos, subastas, usuarios y onboarding; modularización del criterio 4; informe de `email-validator`.
- **2026-11-23** — Pruebas de caracterización y las tres refactorizaciones del Hito 3.
- **2026-11-22** — Rediseño del frontend, entrega final de la tercera entrega y tabla de evaluación.
- Historial completo: `git log` (más de 270 commits en el repositorio).
