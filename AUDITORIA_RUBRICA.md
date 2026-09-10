# Auditoría del Repositorio — Rúbrica Hito 1

> Fecha de auditoría: 2026-09-08
> Repositorio: `Camiones_contratos`

Este documento diagnostica el estado actual del repositorio contrastando cada criterio de la [rúbrica](file:///home/f4cks/Escritorio/Ing/camiones/RUBRICA.md) con las evidencias encontradas. Se identifican las **cosas que faltan** y las **oportunidades de mejora** para cada punto.

---

## Resumen Ejecutivo

| Criterio | Puntaje Estimado | Estado |
|:---|:---:|:---|
| 1. Repositorio, ramas y protección | **0,00** | 🔴 Falta crítica |
| 2. Flujo colaborativo y trazabilidad | **0,00** | 🔴 Falta crítica |
| 3. Calidad del historial y uso de Git | **0,50** | 🟡 Parcial |
| 4. Construcción y reproducibilidad | **0,25** | 🔴 Falta crítica |
| 5. Calidad de código y análisis estático | **0,25** | 🔴 Falta crítica |
| 6. Documentación técnica y revisión de código | **0,50** | 🟡 Parcial |
| 7. Demostración funcional y dominio individual | **0,00** | 🔴 Falta crítica |
| **TOTAL ESTIMADO** | **1,50 / 7,00** | |

> [!CAUTION]
> El proyecto **no puede ejecutarse** debido a múltiples errores de importación en el código Python. Además, los criterios 1 y 2 (repositorio/ramas y flujo colaborativo) carecen de toda evidencia. Estos problemas representan más del 70% de la nota.

---

## ⛔ Hallazgo Crítico: Errores Fatales que Impiden la Ejecución

> [!CAUTION]
> La aplicación backend **crashea al iniciar** debido a múltiples `NameError` e `ImportError` en archivos clave. Esto invalida la demostración funcional (Criterio 7) y la reproducibilidad (Criterio 4).

### Errores detectados:

| Archivo | Error | Detalle |
|:---|:---|:---|
| [main.py](file:///home/f4cks/Escritorio/Ing/camiones/Camiones_contratos/main.py) | `NameError` | `crear_login_router` y `ValidadorUsuario` se usan pero nunca se importan. `subasta_router` se incluye sin importar. Import duplicado de `auth_router`. |
| [domain/modelos.py](file:///home/f4cks/Escritorio/Ing/camiones/Camiones_contratos/domain/modelos.py) | `NameError` | Se usa `re.compile(...)` pero falta `import re`. |
| [dao/onboarding_dao.py](file:///home/f4cks/Escritorio/Ing/camiones/Camiones_contratos/dao/onboarding_dao.py) | `ImportError` | Importa `BD_DAO` de `dao.base_dao`, pero la clase se llama `BaseDAO`. |
| [dao/usuario_dao.py](file:///home/f4cks/Escritorio/Ing/camiones/Camiones_contratos/dao/usuario_dao.py) | `ImportError` + clase duplicada | Importa `BD_DAO` (no existe). Define `UsuarioDAO` dos veces. |
| [services/contrato_service.py](file:///home/f4cks/Escritorio/Ing/camiones/Camiones_contratos/services/contrato_service.py) | `NameError` | Referencia `BD_DAO` que no existe. Docstrings duplicados. |
| [routers/config_router.py](file:///home/f4cks/Escritorio/Ing/camiones/Camiones_contratos/routers/config_router.py) | `NameError` | Usa `Field`, `ConfigDict`, `Dict`, `Any` sin importarlos. |
| [routers/contratos_router.py](file:///home/f4cks/Escritorio/Ing/camiones/Camiones_contratos/routers/contratos_router.py) | `NameError` | Usa `HTTPException` y `ValidationError` sin importarlos. |

### Otros problemas de código:
- **Seguridad:** El hashing de contraseñas en `UsuarioService` usa SHA-256 sin salt (`hashlib.sha256`). Esto es vulnerable a ataques de rainbow table. Se debe usar `bcrypt` o `argon2`.
- **Inconsistencia de idioma:** Mezcla de español e inglés en nombres de métodos (`obt_por_id` vs `get_by_email`, `vali_transicion` vs `save`).
- **Abreviaciones no estándar:** Métodos como `vali_transicion`, `obt_estados`, `act_configuracion` usan abreviaciones que dificultan la legibilidad.
- **Lógica incorrecta en subastas:** `subasta_service.py` compara peso del camión × 0.1 contra distancia en km, lo cual es semánticamente incorrecto.
- **README con rutas incorrectas:** Instrucción `cd backend` apunta a un directorio que no existe. El archivo `principal.py` referenciado tampoco existe (el entry point es `main.py`).

---

## Criterio 1: Repositorio, ramas y protección (Est. 0,25/1,0)

### ✅ Lo que está bien
- El repositorio existe y es accesible.
- El `.gitignore` es adecuado: cubre `__pycache__/`, `*.py[cod]`, `.env`, `node_modules/`, `venv/`, archivos de IDE (`.vscode/`, `.idea/`), y archivos de SO (`.DS_Store`).
- No se encontraron secretos, tokens ni contraseñas en el código fuente.

### ❌ Lo que falta

1. **No hay estrategia de ramas:** Solo existe la rama `main`. No hay ramas de feature, desarrollo ni ninguna otra. El comando `git branch -a` solo muestra:
   ```
   * main
     remotes/origin/HEAD -> origin/main
     remotes/origin/main
   ```

2. **No hay protección de rama principal:** No hay evidencia de reglas de protección en `main`. El historial lineal sugiere que todo se commitea directamente a `main`.

3. **No hay convención de nombres de ramas:** Al no existir ramas, no hay convención visible.

4. **Archivo fuera de lugar:** Existe un `package-lock.json` en la raíz del proyecto sin un `package.json` correspondiente. Este archivo parece ser un duplicado del que está en `frontend/` y debería eliminarse o agregarse al `.gitignore`.

5. **🔴 `.gitignore` con errores críticos:**

   > [!CAUTION]
   > El `.gitignore` tiene reglas que excluyen código fuente y tests del repositorio, y a la vez permite versionar artefactos de build. Esto es un problema grave.

   - **Línea 10: `src/` está ignorado** — Esto impide que `frontend/src/` sea rastreado por Git. El código fuente TypeScript/React original **no está en el repositorio**. Lo que se versiona en su lugar son los archivos compilados en `frontend/dist/` (`main.js`, `main.js.map`).
   - **Línea 14: `tests/` está ignorado** — A pesar de que `pytest` está en las dependencias de desarrollo y el README y la plantilla de PR mencionan ejecutar tests, **no hay archivos de test versionados**. Toda la suite de tests quedó excluida del control de versiones.
   - **`dist/` no está en `.gitignore`** — Los artefactos de build (`frontend/dist/main.js`, `frontend/dist/main.js.map`) están versionados cuando no deberían estarlo.
   - **Imagen pesada versionada:** `frontend/paginas/imagenes/imagen_prueba.png` (~760 KB) está en el repositorio. Para assets estáticos grandes, se recomienda optimizar o usar un servicio externo.

### 📋 Acciones requeridas
- [ ] Configurar protección de rama `main` en el repositorio remoto (requerir PR con al menos 1 revisión).
- [ ] Definir y documentar una estrategia de ramas (ej: `feature/xxx`, `fix/xxx`, `docs/xxx`).
- [ ] Dejar de hacer commits directos a `main`.
- [ ] Eliminar el `package-lock.json` de la raíz.
- [ ] **URGENTE:** Eliminar `src/` del `.gitignore` y hacer commit de `frontend/src/`.
- [ ] **URGENTE:** Eliminar `tests/` del `.gitignore` y hacer commit de los archivos de test.
- [ ] Agregar `dist/` al `.gitignore` y eliminar `frontend/dist/` del repositorio (`git rm -r --cached frontend/dist`).
- [ ] Evaluar si la imagen de prueba (760 KB) debe permanecer en el repositorio.

---

## Criterio 2: Flujo colaborativo y trazabilidad (Est. 0,00/1,0)

### ❌ Lo que falta

> [!CAUTION]
> Este es el criterio con mayor deficiencia. No hay ninguna evidencia de trabajo colaborativo en el historial de Git.

1. **Solo un contribuidor:** Todos los 17 commits fueron realizados por una sola persona. La rúbrica requiere participación de cada integrante con al menos 2 Pull Requests.

2. **Cero Pull Requests:** El historial es completamente lineal (sin merge commits). No hay evidencia de que se hayan creado, revisado o integrado PRs.

3. **Sin Issues / trazabilidad:** No hay relación visible `Issue → rama → commits → PR → merge`. Aunque existe la plantilla [DESCRIPCION_PULL_REQUEST.md](file:///home/f4cks/Escritorio/Ing/camiones/Camiones_contratos/DESCRIPCION_PULL_REQUEST.md), nunca fue utilizada en la práctica.

4. **Sin revisiones de código:** No hay evidencia de revisiones entre pares.

### 📋 Acciones requeridas
- [ ] Cada integrante debe crear al menos 2 Pull Requests propios.
- [ ] Cada PR debe ser revisado por otro miembro del equipo con observaciones técnicas (no solo "aprobado").
- [ ] Crear Issues en el repositorio remoto para las tareas del backlog.
- [ ] Vincular cada PR a un Issue correspondiente.
- [ ] Utilizar la plantilla de PR ya definida en cada Pull Request.
- [ ] El flujo completo `Issue → rama → commits → PR → revisión → merge` debe ser demostrable.

---

## Criterio 3: Calidad del historial y uso de Git (Est. 0,50/1,0)

### ✅ Lo que está bien
- Los mensajes de commits son descriptivos y siguen la convención de **Conventional Commits**:
  ```
  feat(contratos): implementar servicio y router de contratos con CRUD completo
  refactor(schemas): separar esquemas de entrada/salida y agregar validaciones
  docs: agregar README con estructura del proyecto e instrucciones de instalación
  ```
- No hay commits genéricos tipo "cambios", "avance" o "update".
- Los commits tienen scope definido que ayuda a la trazabilidad.

### ⚠️ Lo que se puede mejorar

1. **Commits demasiado grandes:** Algunos commits abarcan mucho trabajo para un solo cambio (ej: `feat(contratos): implementar servicio y router de contratos con CRUD completo` incluye todo el servicio y router en un solo commit). Se recomienda dividir en commits más atómicos.

2. **Falta demostrar operaciones de recuperación:** El equipo debe poder demostrar `git restore`, `git revert` u operaciones similares vistas en clase.

3. **Solo un autor visible:** Aunque los mensajes son buenos, solo una persona ha trabajado en el historial, lo que limita la posibilidad de "leer el historial e identificar quién hizo qué".

### 📋 Acciones requeridas
- [ ] Hacer commits más pequeños y atómicos (una intención concreta por commit).
- [ ] Practicar y documentar operaciones de recuperación de Git (restore, revert, etc.).
- [ ] Asegurar que todos los integrantes tengan commits propios en el historial.

---

## Criterio 4: Construcción y reproducibilidad (Est. 0,25/1,0)

### ✅ Lo que está bien
- Las dependencias Python están declaradas con versiones fijadas en [requirements.txt](file:///home/f4cks/Escritorio/Ing/camiones/Camiones_contratos/requirements.txt).
- Las dependencias de desarrollo están separadas en [requirements-dev.txt](file:///home/f4cks/Escritorio/Ing/camiones/Camiones_contratos/requirements-dev.txt).
- El frontend usa `package.json` con dependencias declaradas.

### ❌ Lo que falta

> [!CAUTION]
> La aplicación **no se puede ejecutar**. Múltiples errores de importación en el backend causan un crash inmediato al intentar iniciar con `uvicorn main:app --reload`. Ver sección "Errores Fatales" más arriba.

1. **El backend no arranca:** `main.py` tiene imports faltantes y duplicados que producen `NameError` al iniciar.
2. **README con instrucciones incorrectas:** `cd backend` apunta a un directorio que no existe. El archivo `principal.py` referenciado no existe. Las versiones en el README (`fastapi==0.141.1`, `uvicorn==0.52.1`) no corresponden a versiones reales publicadas en PyPI.
3. **No hay `.env.example`:** El README menciona variables de entorno pero no existe una plantilla.
4. **Frontend no tiene código fuente:** Debido al `.gitignore`, `frontend/src/` no está versionado. Solo existen los archivos compilados en `dist/`.
5. **Dependencias del frontend ficticias:** `package.json` lista `electron: ^44.0.0` y `typescript: ^7.0.2`, versiones que no existen.
6. **Falta verificación desde copia limpia:** No hay CI/CD ni evidencia de que el proyecto se haya probado desde un entorno limpio.

### 📋 Acciones requeridas
- [ ] **URGENTE:** Corregir todos los errores de importación en `main.py`, `modelos.py`, DAOs, servicios y routers.
- [ ] **URGENTE:** Corregir las instrucciones del README (eliminar `cd backend`, corregir `principal.py` → `main.py`).
- [ ] **URGENTE:** Corregir las versiones de dependencias ficticias tanto en `requirements.txt` como en `package.json`.
- [ ] Crear un archivo `.env.example` con las variables necesarias (sin credenciales reales).
- [ ] Verificar que `uvicorn main:app --reload` arranca correctamente tras las correcciones.
- [ ] Probar la instalación completa desde una copia limpia siguiendo solo las instrucciones del README.

---

## Criterio 5: Calidad de código y análisis estático (Est. 0,25/1,0)

### ✅ Lo que está bien
- `ruff` está incluido como dependencia de desarrollo (`ruff==0.1.8` en `requirements-dev.txt`).
- El frontend tiene ESLint configurado (`eslint.config.js` y dependencias en `package.json`).
- El código fuente sigue un estilo relativamente consistente.

### ❌ Lo que falta

1. **No hay archivo de configuración de Ruff:** No existe `ruff.toml`, `pyproject.toml` ni `setup.cfg` con reglas de linting definidas. Sin configuración explícita, no hay "convención de estilo acordada" verificable.

2. **No hay CI/CD que ejecute linting:** No hay GitHub Actions, GitLab CI ni ninguna automatización que ejecute `ruff` o ESLint automáticamente.

3. **No se documenta la convención de estilo:** No hay un documento o sección que explique qué convenciones de estilo sigue el equipo.

### ⚠️ Lo que se puede mejorar

4. **Frontend sin `.prettierrc`:** No hay configuración de Prettier para formateo del código frontend.

5. **No hay evidencia de correcciones por análisis estático:** El equipo debe poder mostrar al menos una mejora concreta de legibilidad/calidad realizada a partir de estas herramientas.

### 📋 Acciones requeridas
- [ ] Crear un `pyproject.toml` o `ruff.toml` con la configuración de Ruff (reglas habilitadas, exclusiones, etc.).
- [ ] Documentar la convención de estilo del equipo (puede ser en el README o en un `CONTRIBUTING.md`).
- [ ] Ejecutar `ruff check .` y `ruff format .` y corregir las advertencias encontradas.
- [ ] Configurar Prettier para el frontend (`.prettierrc`).
- [ ] (Recomendado) Configurar GitHub Actions / CI que ejecute linting en cada PR.
- [ ] Documentar al menos una corrección concreta realizada gracias al análisis estático.

---

## Criterio 6: Documentación técnica y revisión de código (Est. 0,50/1,0)

### ✅ Lo que está bien
- Las funciones de la capa de **servicios** ([camion_service.py](file:///home/f4cks/Escritorio/Ing/camiones/Camiones_contratos/services/camion_service.py), [contrato_service.py](file:///home/f4cks/Escritorio/Ing/camiones/Camiones_contratos/services/contrato_service.py)) tienen **docstrings completos** con propósito, parámetros, retorno y errores.
- Los **routers** ([camion_router.py](file:///home/f4cks/Escritorio/Ing/camiones/Camiones_contratos/routers/camion_router.py), [contrato_router.py](file:///home/f4cks/Escritorio/Ing/camiones/Camiones_contratos/routers/contrato_router.py)) tienen docstrings que explican el propósito de cada endpoint.
- El README cubre los aspectos básicos de instalación y ejecución.
- Existe plantilla de PR con campos relevantes.
- Existen documentos de [épicas e historias de usuario](file:///home/f4cks/Escritorio/Ing/camiones/Camiones_contratos/EPICAS_Y_HISTORIAS_DE_USUARIO.md) y [requisitos extrafuncionales](file:///home/f4cks/Escritorio/Ing/camiones/Camiones_contratos/ReqExtrafuncionales.md) bien estructurados.

### ❌ Lo que falta

1. **DAOs sin documentación:** Las funciones en [camion_dao.py](file:///home/f4cks/Escritorio/Ing/camiones/Camiones_contratos/dao/camion_dao.py) y [contrato_dao.py](file:///home/f4cks/Escritorio/Ing/camiones/Camiones_contratos/dao/contrato_dao.py) no tienen docstrings (ni parámetros, retorno o condiciones de error).

2. **Modelos sin documentación:** [models.py](file:///home/f4cks/Escritorio/Ing/camiones/Camiones_contratos/domain/models.py) no tiene docstrings en las clases `Camion` y `Contrato`.

3. **Schemas parcialmente documentados:** [schemas.py](file:///home/f4cks/Escritorio/Ing/camiones/Camiones_contratos/domain/schemas.py) tiene `Field(description=...)` en algunos campos pero no en todos. Los schemas de respuesta (`Camion`, `Contrato`) carecen de descripciones.

4. **Frontend sin documentación:** [App.tsx](file:///home/f4cks/Escritorio/Ing/camiones/Camiones_contratos/frontend/src/App.tsx) y los componentes del frontend no tienen documentación. No hay README en el directorio `frontend/`.

5. **Sin revisiones de código verificables:** No hay PRs con observaciones técnicas entre pares.

### ⚠️ Lo que se puede mejorar

6. **Typo en archivo:** `domain/intrunsion.md` debería llamarse `intrusion.md` o `intrusión.md`.

### 📋 Acciones requeridas
- [ ] Agregar docstrings a todas las funciones de `camion_dao.py` y `contrato_dao.py`.
- [ ] Agregar docstrings a las clases en `models.py` describiendo cada modelo y sus columnas.
- [ ] Completar las descripciones de campos en `schemas.py`.
- [ ] Agregar documentación básica al frontend (JSDoc en componentes, README en `frontend/`).
- [ ] Realizar revisiones de PR con observaciones técnicas sustanciales (no solo "aprobado").
- [ ] Poder demostrar al menos una observación recibida en PR y cómo fue incorporada.
- [ ] Corregir el nombre del archivo `intrunsion.md` → `intrusion.md`.

---

## Criterio 7: Demostración funcional y dominio individual (Est. 0,00/1,0)

### ❌ Lo que falta

> [!CAUTION]
> La línea base **no se puede ejecutar**. Los errores fatales de importación impiden iniciar el servidor. Sin demostración funcional, este criterio no puede cumplirse.

1. **Backend no ejecutable:** `uvicorn main:app` crashea inmediatamente por `NameError` e `ImportError` en múltiples archivos.
2. **Frontend desconectado:** El frontend (`paginas/script.js`) solo tiene `alert()` de placeholder y no se conecta al backend.
3. **Frontend sin código fuente versionado:** El código TypeScript de Electron no está en el repositorio.
4. **Sin tests:** Aunque `pytest` está en dependencias, `tests/` está en `.gitignore` y no hay tests versionados.
5. **Sin participación individual demostrable:** Con un solo contribuidor en Git, los demás integrantes no pueden demostrar contribuciones ni revisiones.

### 📋 Acciones requeridas
- [ ] **URGENTE:** Corregir errores fatales para que el backend inicie correctamente.
- [ ] Desarrollar componentes frontend que consuman la API del backend.
- [ ] Crear al menos tests básicos con `pytest` y versionarlos.
- [ ] Cada integrante debe tener contribuciones propias verificables en Git.
- [ ] Cada integrante debe practicar operaciones básicas de Git para la evaluación.
- [ ] Preparar explicación clara de qué funcionalidad corresponde al hito y qué queda fuera del alcance.

---

## Resumen de Acciones Prioritarias

> [!IMPORTANT]
> Las siguientes acciones están ordenadas por prioridad de impacto en la nota.

### 🔴 Prioridad Crítica — Bloqueantes (impactan criterios 1, 2, 4 y 7)
1. **Corregir errores fatales de importación** en `main.py`, `modelos.py`, DAOs, servicios y routers para que la app pueda arrancar.
2. **Corregir `.gitignore`:** Eliminar `src/` y `tests/` de las exclusiones. Agregar `dist/` a las exclusiones.
3. **Corregir README:** Eliminar `cd backend`, corregir `principal.py` → `main.py`, corregir versiones ficticias.
4. **Establecer flujo colaborativo real:** Todos los integrantes deben contribuir con commits, ramas, PRs y revisiones.
5. **Configurar protección de rama `main`:** Requerir PR con revisión antes de merge.
6. **Crear Issues y vincularlos a PRs:** Demostrar trazabilidad completa.
7. **Cada integrante: mínimo 2 PRs + revisiones a compañeros.**

### 🟡 Prioridad Media (impactan criterios 3, 5 y 6)
8. Crear `.env.example` con variables de entorno.
9. Configurar `ruff` con archivo de configuración (`pyproject.toml`).
10. Agregar docstrings a DAOs y modelos.
11. Ejecutar linting y documentar correcciones realizadas.
12. Unificar idioma y convenciones de nombrado en el código.

### 🟢 Prioridad Baja (mejoras adicionales)
13. Crear tests unitarios con `pytest` y versionar `tests/`.
14. Mejorar el frontend con componentes que consuman la API.
15. Reemplazar SHA-256 por bcrypt/argon2 para hashing de contraseñas.
16. Agregar `Dockerfile` / `docker-compose.yml`.
17. Agregar README al directorio `frontend/`.
18. Eliminar `package-lock.json` de la raíz.
19. Corregir typo `intrunsion.md` → `intrusion.md` y mover a `docs/`.

---

## Archivos Auditados

| Archivo | Estado |
|:---|:---|
| [README.md](file:///home/f4cks/Escritorio/Ing/camiones/Camiones_contratos/README.md) | ❌ Rutas incorrectas (`cd backend`), versiones ficticias, falta `.env.example` |
| [.gitignore](file:///home/f4cks/Escritorio/Ing/camiones/Camiones_contratos/.gitignore) | ❌ Excluye `src/` y `tests/`, no excluye `dist/` |
| [requirements.txt](file:///home/f4cks/Escritorio/Ing/camiones/Camiones_contratos/requirements.txt) | ⚠️ Versiones posiblemente ficticias |
| [requirements-dev.txt](file:///home/f4cks/Escritorio/Ing/camiones/Camiones_contratos/requirements-dev.txt) | ✅ Separado correctamente |
| [main.py](file:///home/f4cks/Escritorio/Ing/camiones/Camiones_contratos/main.py) | ❌ No arranca — imports faltantes y duplicados |
| [domain/modelos.py](file:///home/f4cks/Escritorio/Ing/camiones/Camiones_contratos/domain/modelos.py) | ❌ Falta `import re` |
| [dao/onboarding_dao.py](file:///home/f4cks/Escritorio/Ing/camiones/Camiones_contratos/dao/onboarding_dao.py) | ❌ Importa `BD_DAO` inexistente |
| [dao/usuario_dao.py](file:///home/f4cks/Escritorio/Ing/camiones/Camiones_contratos/dao/usuario_dao.py) | ❌ Importa `BD_DAO` inexistente, clase duplicada |
| [dao/base_dao.py](file:///home/f4cks/Escritorio/Ing/camiones/Camiones_contratos/dao/base_dao.py) | ✅ Clase `BaseDAO` correcta |
| [dao/database.py](file:///home/f4cks/Escritorio/Ing/camiones/Camiones_contratos/dao/database.py) | ✅ Documentado |
| [domain/schemas.py](file:///home/f4cks/Escritorio/Ing/camiones/Camiones_contratos/domain/schemas.py) | ⚠️ Parcialmente documentado |
| [domain/intrunsion.md](file:///home/f4cks/Escritorio/Ing/camiones/Camiones_contratos/domain/intrunsion.md) | ⚠️ Buen contenido, nombre con typo, mal ubicado |
| [services/contrato_service.py](file:///home/f4cks/Escritorio/Ing/camiones/Camiones_contratos/services/contrato_service.py) | ❌ Referencia `BD_DAO` inexistente, docstrings duplicados |
| [routers/config_router.py](file:///home/f4cks/Escritorio/Ing/camiones/Camiones_contratos/routers/config_router.py) | ❌ Imports faltantes (`Field`, `ConfigDict`, `Dict`, `Any`) |
| [routers/contratos_router.py](file:///home/f4cks/Escritorio/Ing/camiones/Camiones_contratos/routers/contratos_router.py) | ❌ Imports faltantes (`HTTPException`, `ValidationError`) |
| [services/usuario_service.py](file:///home/f4cks/Escritorio/Ing/camiones/Camiones_contratos/services/usuario_service.py) | ⚠️ Hashing inseguro (SHA-256 sin salt) |
| [EPICAS_Y_HISTORIAS_DE_USUARIO.md](file:///home/f4cks/Escritorio/Ing/camiones/Camiones_contratos/EPICAS_Y_HISTORIAS_DE_USUARIO.md) | ✅ Completo y bien estructurado |
| [DESCRIPCION_PULL_REQUEST.md](file:///home/f4cks/Escritorio/Ing/camiones/Camiones_contratos/DESCRIPCION_PULL_REQUEST.md) | ⚠️ Es un borrador de un PR específico, no una plantilla reutilizable |
| [ReqExtrafuncionales.md](file:///home/f4cks/Escritorio/Ing/camiones/Camiones_contratos/ReqExtrafuncionales.md) | ✅ Completo |
| [frontend/](file:///home/f4cks/Escritorio/Ing/camiones/Camiones_contratos/frontend/) | ❌ Sin código fuente versionado, funcionalidad mínima, sin docs |
| Historial Git | ❌ Un solo autor, sin ramas, sin PRs, sin Issues |
