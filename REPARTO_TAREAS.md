# Reparto de Tareas — Correcciones Auditoría Rúbrica Hito 1

> Basado en [AUDITORIA_RUBRICA.md](file:///home/f4cks/Escritorio/Ing/camiones/Camiones_contratos/AUDITORIA_RUBRICA.md)
> Fecha: 2026-09-08

---

## Asignación de Estudiantes

| ID | Nombre |
|:---:|:---|
| **E1** | *(completar)* |
| **E2** | *(completar)* |
| **E3** | *(completar)* |
| **E4** | *(completar)* |
| **E5** | *(completar)* |

---

## Tabla Resumen por Estudiante

| Estudiante | Secciones principales | Prioridad |
|:---:|:---|:---:|
| **E1** | Repositorio, ramas y `.gitignore` + CI/CD | 🔴 Crítica |
| **E2** | Errores fatales backend (DAOs + Domain) + Tests | 🔴 Crítica |
| **E3** | Errores fatales backend (Routers + main.py) + README | 🔴 Crítica |
| **E4** | Calidad de código, linting y documentación backend | 🟡 Media |
| **E5** | Frontend completo + documentación frontend | 🟡 Media |

> [!IMPORTANT]
> **Tarea de TODOS (Criterio 2 y 3):** Cada integrante debe crear **mínimo 2 Pull Requests propios**, revisar PRs de compañeros con observaciones técnicas, y vincular cada PR a un Issue. Esto no se puede delegar — cada persona debe demostrar participación individual.

---

## 📌 Tarea Común — TODOS los integrantes

**Criterios impactados:** 2 (Flujo colaborativo) + 3 (Historial Git) + 7 (Dominio individual)

Cada estudiante, sin excepción, debe cumplir con lo siguiente:

- [ ] Crear al menos **2 Pull Requests propios** con trabajo real
- [ ] Revisar al menos **2 PRs de compañeros** con observaciones técnicas sustanciales (no solo "aprobado" o "se ve bien")
- [ ] Vincular cada PR a un **Issue** del repositorio
- [ ] Usar la plantilla de `DESCRIPCION_PULL_REQUEST.md` en cada PR (propósito, cambios, verificación, Issue vinculado)
- [ ] Usar **ramas feature** con nombres descriptivos (ej: `feature/fix-imports-main`, `fix/gitignore-src`)
- [ ] Hacer commits **pequeños y atómicos** con mensajes descriptivos (Conventional Commits)
- [ ] Practicar al menos una operación de recuperación de Git (`git restore`, `git revert`, etc.) y poder explicarla
- [ ] Poder explicar en vivo **una contribución propia** y **una revisión realizada**

---

## 🔴 E1 — Repositorio, Ramas, `.gitignore` y CI/CD

**Criterios impactados:** 1 (Repositorio y ramas) + 5 (Análisis estático / CI)

### Sección: Criterio 1 — Repositorio, ramas y protección

- [ ] Configurar **protección de rama `main`** en GitHub (requerir PR con al menos 1 revisión aprobatoria antes de merge)
- [ ] Definir y documentar la **estrategia de ramas** del equipo (ej: `feature/xxx`, `fix/xxx`, `docs/xxx`) — puede ser en el README o en un `CONTRIBUTING.md`
- [ ] Comunicar al equipo que **no se hacen más commits directos a `main`**

### Sección: Criterio 1 — Corrección del `.gitignore`

> [!CAUTION]
> Estas tareas son **bloqueantes** para E2, E3 y E5. Hacerlas primero.

- [ ] **URGENTE:** Eliminar `src/` de la línea 10 del `.gitignore`
- [ ] **URGENTE:** Eliminar `tests/` de la línea 14 del `.gitignore`
- [ ] **URGENTE:** Eliminar `test_refactor_borrador.py` de la línea 13 del `.gitignore` (si ya no aplica)
- [ ] Agregar `dist/` al `.gitignore`
- [ ] Ejecutar `git rm -r --cached frontend/dist` para dejar de rastrear los artefactos de build
- [ ] Eliminar el `package-lock.json` huérfano de la raíz del proyecto
- [ ] Agregar al `.gitignore` las entradas faltantes: `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`, `.coverage`
- [ ] Evaluar si `frontend/paginas/imagenes/imagen_prueba.png` (~760 KB) debe permanecer o ser optimizada

### Sección: Criterio 5 — CI/CD (GitHub Actions)

- [ ] Crear `.github/workflows/ci.yml` con un pipeline básico que ejecute:
  - `ruff check .` para linting del backend
  - `ruff format --check .` para verificar formateo
  - `pytest -v` para tests del backend
- [ ] Configurar el workflow para que se ejecute en cada PR hacia `main`

### Entregables de E1
| Entregable | Archivo/Ubicación |
|:---|:---|
| `.gitignore` corregido | `.gitignore` |
| Estrategia de ramas documentada | `CONTRIBUTING.md` o sección en `README.md` |
| Protección de rama configurada | Settings del repo en GitHub |
| Pipeline CI/CD | `.github/workflows/ci.yml` |

---

## 🔴 E2 — Errores Fatales: DAOs, Domain y Tests

**Criterios impactados:** 4 (Reproducibilidad) + 6 (Documentación) + 7 (Funcionalidad)

### Sección: Errores Fatales — Capa DAO

- [ ] **URGENTE:** En `dao/onboarding_dao.py` — cambiar `from dao.base_dao import BD_DAO` → `from dao.base_dao import BaseDAO` y ajustar la herencia de la clase
- [ ] **URGENTE:** En `dao/usuario_dao.py`:
  - Cambiar `from dao.base_dao import BD_DAO` → `from dao.base_dao import BaseDAO`
  - Eliminar la definición **duplicada** de `UsuarioDAO` (queda solo una)
  - Agregar import faltante de `List` de `typing`
- [ ] Verificar que todas las clases DAO heredan correctamente de `BaseDAO`

### Sección: Errores Fatales — Capa Domain

- [ ] **URGENTE:** En `domain/modelos.py` — agregar `import re` al inicio del archivo
- [ ] Revisar y corregir la lógica del regex `ONU_REGEX` si es necesario

### Sección: Errores Fatales — Capa Services

- [ ] **URGENTE:** En `services/contrato_service.py`:
  - Cambiar referencia `BD_DAO` → `BaseDAO` (o el tipo correcto)
  - Eliminar docstrings duplicados
- [ ] En `services/usuario_service.py` — reemplazar hashing SHA-256 sin salt por `bcrypt` o `argon2` (agregar `passlib[bcrypt]` a `requirements.txt`)

### Sección: Criterio 6 — Documentación de DAOs y Domain

- [ ] Agregar docstrings a **todas** las funciones de `dao/onboarding_dao.py` y `dao/usuario_dao.py` (propósito, parámetros, retorno, errores)
- [ ] Agregar docstrings a las clases en `domain/modelos.py` describiendo cada modelo y sus columnas
- [ ] Completar las descripciones de campos faltantes en `domain/schemas.py` con `Field(description=...)`

### Sección: Criterio 7 — Tests

> [!NOTE]
> Requiere que E1 haya eliminado `tests/` del `.gitignore` primero.

- [ ] Crear directorio `tests/` con al menos tests básicos para:
  - Funciones de servicio (`services/contrato_service.py`, `services/usuario_service.py`)
  - Modelos de dominio (`domain/modelos.py`)
- [ ] Verificar que `pytest -v` ejecuta los tests correctamente
- [ ] Agregar `conftest.py` con fixtures básicos si es necesario

### Entregables de E2
| Entregable | Archivo/Ubicación |
|:---|:---|
| DAOs corregidos | `dao/onboarding_dao.py`, `dao/usuario_dao.py` |
| Domain corregido | `domain/modelos.py` |
| Servicio de contratos corregido | `services/contrato_service.py` |
| Hashing seguro | `services/usuario_service.py` |
| Docstrings en DAOs y Domain | Archivos mencionados arriba |
| Tests unitarios | `tests/` |

---

## 🔴 E3 — Errores Fatales: Routers, `main.py` y README

**Criterios impactados:** 4 (Reproducibilidad) + 7 (Funcionalidad)

### Sección: Errores Fatales — Capa Routers

- [ ] **URGENTE:** En `routers/config_router.py`:
  - Agregar `from pydantic import Field, ConfigDict`
  - Agregar `from typing import Dict, Any`
- [ ] **URGENTE:** En `routers/contratos_router.py`:
  - Agregar `from fastapi import HTTPException`
  - Agregar `from pydantic import ValidationError`
- [ ] Verificar que no hay otros imports faltantes en los routers

### Sección: Errores Fatales — `main.py`

- [ ] **URGENTE:** Corregir `main.py`:
  - Agregar import de `crear_login_router` desde `routers.login_router`
  - Agregar import de `ValidadorUsuario` desde `services.usuario_service`
  - Agregar import de `router as subasta_router` desde `routers.subasta_router`
  - Eliminar el import **duplicado** de `auth_router`
- [ ] Verificar que `uvicorn main:app --reload` arranca sin errores tras las correcciones

### Sección: Criterio 4 — README y Reproducibilidad

- [ ] **URGENTE:** Corregir el README.md:
  - Eliminar instrucción `cd backend` (el backend está en la raíz)
  - Corregir referencia `principal.py` → `main.py`
  - Corregir versiones ficticias (`fastapi==0.141.1` → versión real, `uvicorn==0.52.1` → versión real)
  - Verificar que las versiones del README coincidan con `requirements.txt`
  - Corregir versiones de Node.js y npm (actualmente dice "POR DEFINIR")
- [ ] Crear archivo `.env.example` con las variables necesarias:
  ```
  DATABASE_URL=postgresql://user:password@localhost:5432/camiones_db
  SECRET_KEY=tu_clave_secreta_aqui
  DEBUG=true
  CORS_ORIGINS=http://localhost:5173
  ```
- [ ] Agregar sección de **verificación post-instalación** al README (cómo confirmar que todo funciona)
- [ ] Corregir versiones en `requirements.txt` si contienen versiones ficticias/inexistentes
- [ ] Probar la instalación completa desde cero siguiendo solo el README

### Entregables de E3
| Entregable | Archivo/Ubicación |
|:---|:---|
| Routers corregidos | `routers/config_router.py`, `routers/contratos_router.py` |
| main.py corregido | `main.py` |
| README corregido | `README.md` |
| Variables de entorno | `.env.example` |
| Versiones corregidas | `requirements.txt` |

---

## 🟡 E4 — Calidad de Código, Linting y Documentación Backend

**Criterios impactados:** 5 (Análisis estático) + 6 (Documentación) + 3 (Historial)

### Sección: Criterio 5 — Configuración de Ruff y Convención de Estilo

- [ ] Crear `pyproject.toml` con configuración de Ruff:
  ```toml
  [tool.ruff]
  target-version = "py312"
  line-length = 120

  [tool.ruff.lint]
  select = ["E", "F", "W", "I", "N", "UP"]

  [tool.ruff.format]
  quote-style = "double"
  ```
- [ ] Ejecutar `ruff check .` sobre todo el proyecto y corregir las advertencias encontradas
- [ ] Ejecutar `ruff format .` para formatear el código de forma consistente
- [ ] Documentar la convención de estilo del equipo en un `CONTRIBUTING.md` o sección del README que explique:
  - Herramientas usadas (Ruff)
  - Cómo ejecutar el linter localmente
  - Reglas principales habilitadas
- [ ] Documentar al menos **una corrección concreta** realizada gracias al análisis estático (para mostrar en la evaluación)

### Sección: Criterio 5 — Unificación de Nombrado

- [ ] Unificar idioma en nombres de métodos de los DAOs (decidir español o inglés y aplicar consistentemente):
  - `obt_por_id` / `get_by_id`
  - `obt_todos` / `get_all`
  - `guardar` / `save`
  - etc.
- [ ] Reemplazar abreviaciones no estándar por nombres completos:
  - `vali_transicion` → `validar_transicion`
  - `obt_estados` → `obtener_estados`
  - `act_configuracion` → `actualizar_configuracion`

### Sección: Criterio 6 — Documentación de Servicios y Routers faltante

- [ ] Revisar y completar docstrings en `services/subasta_service.py` (parámetros, retorno, errores)
- [ ] Corregir la lógica incorrecta en `subasta_service.py` que compara `peso_total * 0.1` contra `distancia_max_km`
- [ ] Agregar docstrings a los modelos de request en routers (`SolicitudCambioEstado`, `LoginEsquema`, etc.)
- [ ] Renombrar `domain/intrunsion.md` → `domain/intrusion.md` (corregir typo)
- [ ] Mover `domain/intrusion.md` a una ubicación más adecuada (ej: `docs/intrusion.md`)

### Sección: Criterio 2 — Plantilla de PR

- [ ] Convertir `DESCRIPCION_PULL_REQUEST.md` en una **plantilla reutilizable** (actualmente es un borrador de un PR específico):
  - Reemplazar el contenido específico por placeholders
  - Si es GitHub: mover a `.github/PULL_REQUEST_TEMPLATE.md`

### Entregables de E4
| Entregable | Archivo/Ubicación |
|:---|:---|
| Configuración de Ruff | `pyproject.toml` |
| Código formateado y sin warnings | Todo el backend |
| Convención de estilo documentada | `CONTRIBUTING.md` |
| Nombrado unificado | DAOs, servicios |
| Plantilla de PR reutilizable | `.github/PULL_REQUEST_TEMPLATE.md` |
| Documentación de corrección por linter | En el PR correspondiente |

---

## 🟡 E5 — Frontend Completo y Documentación Frontend

**Criterios impactados:** 7 (Funcionalidad) + 6 (Documentación) + 4 (Reproducibilidad)

### Sección: Criterio 1/4 — Recuperar código fuente del frontend

> [!NOTE]
> Requiere que E1 haya corregido el `.gitignore` primero (eliminar `src/`).

- [ ] Verificar que `frontend/src/` ya no está ignorado por Git
- [ ] Hacer commit del código fuente TypeScript en `frontend/src/`
- [ ] Corregir versiones ficticias en `frontend/package.json`:
  - `electron: ^44.0.0` → versión real existente
  - `typescript: ^7.0.2` → versión real existente
- [ ] Verificar que `npm install` y `npm run dev` funcionan correctamente

### Sección: Criterio 7 — Funcionalidad del Frontend

- [ ] Desarrollar componentes/páginas frontend que **consuman la API del backend**:
  - Al menos una vista que haga `fetch`/`axios` a los endpoints de camiones o contratos
  - Mostrar datos reales del backend en la interfaz
- [ ] Reemplazar los `alert()` placeholder en `paginas/script.js` con funcionalidad real
- [ ] Verificar que la comunicación frontend ↔ backend funciona correctamente

### Sección: Criterio 5 — Linting del Frontend

- [ ] Configurar Prettier para el frontend (crear `.prettierrc`):
  ```json
  {
    "semi": true,
    "singleQuote": true,
    "tabWidth": 2,
    "trailingComma": "es5"
  }
  ```
- [ ] Verificar que ESLint está configurado correctamente en `eslint.config.js`
- [ ] Ejecutar ESLint y Prettier sobre el código frontend y corregir errores

### Sección: Criterio 6 — Documentación del Frontend

- [ ] Crear `frontend/README.md` con:
  - Descripción del frontend (tecnologías usadas)
  - Prerrequisitos (Node.js, npm)
  - Instrucciones de instalación (`npm install`)
  - Comandos disponibles (`npm run dev`, `npm start`, `npm run build`)
  - Estructura de directorios
- [ ] Agregar JSDoc/comentarios a los componentes principales (`App.tsx`, `main.tsx`, etc.)
- [ ] Documentar cómo se conecta el frontend con el backend (URL base, endpoints consumidos)

### Entregables de E5
| Entregable | Archivo/Ubicación |
|:---|:---|
| Código fuente versionado | `frontend/src/` |
| `package.json` con versiones reales | `frontend/package.json` |
| Componentes funcionales | `frontend/src/` o `frontend/paginas/` |
| Prettier configurado | `frontend/.prettierrc` |
| README del frontend | `frontend/README.md` |
| Documentación de componentes | JSDoc en archivos fuente |

---

## Diagrama de Dependencias entre Tareas

```
E1 (.gitignore + ramas + CI)
 ├──► E2 (necesita tests/ desbloqueado para crear tests)
 ├──► E5 (necesita src/ desbloqueado para versionar frontend)
 │
 ├── E3 (puede trabajar en paralelo — routers, main.py, README)
 └── E4 (puede trabajar en paralelo — linting, docs, nombrado)

Orden sugerido:
  1. E1 corrige .gitignore y configura ramas     ← PRIMERO
  2. E2, E3, E4 trabajan en paralelo             ← DESPUÉS
  3. E5 trabaja tras E1                          ← DESPUÉS DE E1
  4. TODOS hacen PRs y revisiones cruzadas        ← DURANTE TODO
```

> [!WARNING]
> **E1 es bloqueante.** Hasta que E1 no corrija el `.gitignore`, E2 no puede versionar tests y E5 no puede versionar el código fuente del frontend. E1 debe completar su tarea de `.gitignore` lo antes posible.

---

## Checklist de Revisiones Cruzadas (Criterio 2)

Para cumplir con el mínimo de 2 PRs revisados por persona, se sugiere esta rotación:

| Autor del PR | Revisores sugeridos |
|:---:|:---:|
| E1 | E2, E3 |
| E2 | E3, E4 |
| E3 | E4, E5 |
| E4 | E5, E1 |
| E5 | E1, E2 |

> [!TIP]
> Las revisiones deben incluir **observaciones técnicas reales** (sugerencias de mejora, bugs encontrados, preguntas sobre la implementación). Un comentario tipo "LGTM" o "aprobado" sin contenido **no cuenta** para la rúbrica.

---

## Resumen de Carga por Estudiante

| Estudiante | Tareas 🔴 Críticas | Tareas 🟡 Media | Tareas 🟢 Baja | Total aprox. |
|:---:|:---:|:---:|:---:|:---:|
| **E1** | 8 | 2 | 2 | ~12 |
| **E2** | 5 | 5 | 3 | ~13 |
| **E3** | 6 | 3 | 2 | ~11 |
| **E4** | 0 | 9 | 2 | ~11 |
| **E5** | 2 | 5 | 3 | ~10 |

> La carga es aproximadamente equitativa. E1, E2 y E3 tienen más tareas críticas porque son bloqueantes para el resto.
