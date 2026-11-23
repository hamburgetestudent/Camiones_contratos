# Diagrama de Casos de Uso · Camiones Contratos (MansoViaje)

> **Archivo editable del diagrama:** [`1-casos-de-uso.xml`](1-casos-de-uso.xml) *(formato nativo `<mxfile>` de diagrams.net / draw.io)*  
> **Exportación sugerida para entrega:** abrir [`1-casos-de-uso.xml`](1-casos-de-uso.xml) en [app.diagrams.net](https://app.diagrams.net/) o con la extensión Draw.io de VS Code y exportar la imagen como `1-casos-de-uso.png` junto a este documento.

---

## 1. Nota de lectura

> *Párrafo breve centrado en las decisiones de modelado (entre 5 y 10 líneas), listo para la evaluación:*

El diagrama delimita exclusivamente las capacidades implementadas en los seis routers activos de FastAPI y la base SQLite del proyecto, dejando fuera funciones planificadas pero inexistentes (pagos en custodia, notificaciones por correo o gestión de flota de camiones). Separamos tres actores humanos primarios (`Dador de carga`, `Transportista` y `Administrador Backoffice`) porque cada rol accede a flujos distintos y el autorregistro impide crear cuentas administrativas, manteniendo como actor externo al `Motor SQLite` para explicitar qué operaciones persisten estado en `camiones.db` frente a la configuración en memoria de `ReglasNegocio`. Usamos `«include»` en subprocesos obligatorios que el caso base ejecuta siempre en la misma transacción —como verificar KYC aprobado antes de crear un contrato, rechazar competidores al adjudicar, evaluar el cierre temporal al postular o auditar cada baja y cancelación administrativa— y reservamos `«extend»` para comportamientos opcionales o condicionales como adjuntar datos de onboarding al registrarse, filtrar el catálogo de cargas o declarar desierta una subasta expirada sin ofertas.

---

## 2. Actores del sistema

La rúbrica exige incluir todos los usuarios del sistema y representar explícitamente los sistemas externos como actores:

| Actor | Tipo UML | Rol / Evidencia en código | Coherencia con los otros diagramas |
|---|---|---|---|
| **Dador de carga** | Actor primario humano | `RolUsuario.DADOR_CARGA` ([`domain/modelos_usuario.py`](../../domain/modelos_usuario.py)), autenticado por JWT ([`routers/sesion.py`](../../routers/sesion.py)) | Mismo nombre exacto que en [`3-secuencia.md`](3-secuencia.md) (`actor D as Dador de carga`). |
| **Transportista** | Actor primario humano | `RolUsuario.TRANSPORTISTA` ([`domain/modelos_usuario.py`](../../domain/modelos_usuario.py)) | Participa en creación de oferta, KYC documental y transiciones de carga (`UsuarioModelo` en [`diagrama_clases.xml`](diagrama_clases.xml)). |
| **Administrador Backoffice** | Actor primario humano | `RolUsuario.ADMIN_BACKOFFICE` verificado mediante `administrador_actual` ([`routers/sesion.py`](../../routers/sesion.py)) | Consume [`routers/admin_router.py`](../../routers/admin_router.py) y rutas `/onboarding/admin/*`. |
| **Motor SQLite** | Actor externo (`«system»`) | Persistencia en `camiones.db` mediante [`database/conexion.py`](../../database/conexion.py) y [`database/schema.sql`](../../database/schema.sql) | Mismo nombre que `«external» Motor SQLite` en [`4-componentes.drawio`](4-componentes.drawio) y `SQLite` en [`3-secuencia.md`](3-secuencia.md). |

> **Por qué no aparecen servicios de correo, SII, OAuth ni pasarela de pagos como actores externos:** tras revisar `services/`, `routers/` y `domain/`, el sistema actual no realiza llamadas HTTP/SMTP externas ni integra proveedores de pago o validación tributaria remota; toda validación de RUT (dígito verificador módulo 11) y emisión de JWT (`HS256`) se ejecuta localmente dentro del backend.

---

## 3. Catálogo de casos de uso y trazabilidad al código

El diagrama agrupa **23 casos de uso** en 4 bandas funcionales que cubren el 100 % de los endpoints montados en [`main.py`](../../main.py):

### Banda 1 · Identidad, Registro y Sesión (`auth_router.py` + `sesion.py`)

| ID | Caso de uso en el diagrama | Actores | Endpoint(s) HTTP | Implementación en servicio |
|---|---|---|---|---|
| **CU-01** | **Registrarse en la plataforma** | `Dador de carga`, `Transportista`, `Motor SQLite` | `POST /auth/registro` | [`UsuarioService.registrar_usuario`](../../services/usuario_service.py) |
| **CU-02** | **Adjuntar datos de onboarding al registro** | *(extiende a CU-01)*, `Motor SQLite` | `POST /auth/registro` (`documentos`, `perfil_tributario`) | [`UsuarioService.registrar_usuario`](../../services/usuario_service.py) ➔ [`OnboardingService`](../../services/onboarding_service.py) |
| **CU-03** | **Gestionar sesión (Login / Sesión / Logout)** | Todos los actores humanos, `Motor SQLite` | `POST /auth/login`, `GET /auth/sesion`, `POST /auth/logout` | [`UsuarioService.iniciar_sesion`](../../services/usuario_service.py), [`cerrar_sesion`](../../routers/sesion.py) (`sesiones_cerradas`) |

### Banda 2 · Onboarding Dador, Contratos y Adjudicación (`onboarding_router.py` + `contratos_router.py` + `subasta_router.py`)

| ID | Caso de uso en el diagrama | Actores | Endpoint(s) HTTP | Implementación en servicio |
|---|---|---|---|---|
| **CU-04** | **Gestionar perfil tributario** | `Dador de carga`, `Motor SQLite` | `POST /onboarding/dador/perfil`, `GET /onboarding/dador/perfil` | [`OnboardingService.registrar_o_actualizar_perfil_dador`](../../services/onboarding_service.py) |
| **CU-05** | **Crear contrato en borrador** *(resaltado)* | `Dador de carga`, `Motor SQLite` | `POST /contratos` | [`ServicioContrato.crear_contrato`](../../services/contrato_service.py) (**mismo nombre que [`3-secuencia.md`](3-secuencia.md)**) |
| **CU-06** | **Verificar KYC de dador aprobado** | *(incluido por CU-05)*, `Motor SQLite` | — *(regla interna)* | [`OnboardingService.es_dador_aprobado`](../../services/onboarding_service.py) |
| **CU-07** | **Revisar postulaciones y adjudicar subasta** | `Dador de carga`, `Motor SQLite` | `GET /subastas/cargas/{carga_id}/postulaciones`, `POST /subastas/adjudicar` | [`ServicioSubasta.listar_postulaciones_carga`](../../services/subasta_service.py), [`ServicioSubasta.adjudicar_subasta`](../../services/subasta_service.py) |
| **CU-08** | **Rechazar ofertas competidoras** | *(incluido por CU-07)*, `Motor SQLite` | — *(atómico en transacción)* | [`_rechazar_postulaciones_competidoras`](../../services/subasta_service.py) |
| **CU-09** | **Cambiar estado de contrato** | `Dador de carga`, `Transportista`, *(incluido por CU-07)*, `Motor SQLite` | `PATCH /contratos/{contrato_id}/estado` | [`ServicioContrato.cambiar_estado`](../../services/contrato_service.py) ➔ [`MaquinaEstadosContrato`](../../domain/maquina_estados.py) |
| **CU-10** | **Consultar contratos** | `Dador de carga`, `Transportista`, `Motor SQLite` | `GET /contratos`, `GET /contratos/{contrato_id}` | [`ServicioContrato.listar_contratos`](../../services/contrato_service.py), [`obtener_contrato`](../../services/contrato_service.py) |

### Banda 3 · Onboarding Transportista y Subastas (`onboarding_router.py` + `subasta_router.py`)

| ID | Caso de uso en el diagrama | Actores | Endpoint(s) HTTP | Implementación en servicio |
|---|---|---|---|---|
| **CU-11** | **Cargar documentos y consultar estado KYC** | `Transportista`, `Motor SQLite` | `POST /onboarding/transportista/documentos`, `GET /onboarding/transportista/documentos`, `GET /onboarding/transportista/estado` | [`OnboardingService.cargar_documento`](../../services/onboarding_service.py), [`obtener_estado_transportista`](../../services/onboarding_service.py) |
| **CU-12** | **Explorar cargas disponibles** | `Transportista`, `Motor SQLite` | `GET /subastas/cargas` | [`ServicioSubasta.explorar_cargas`](../../services/subasta_service.py) |
| **CU-13** | **Filtrar cargas por criterios** | *(extiende a CU-12)* | `GET /subastas/cargas?region=...&tipo_carroceria=...&distancia_max_km=...` | [`ServicioSubasta.explorar_cargas`](../../services/subasta_service.py) |
| **CU-14** | **Postular a carga** | `Transportista`, `Motor SQLite` | `POST /subastas/postular` | [`ServicioSubasta.postular_a_carga`](../../services/subasta_service.py) |
| **CU-15** | **Evaluar plazo de cierre de subasta** | *(incluido por CU-14)*, `Motor SQLite` | — *(regla interna)* | [`ServicioSubasta._evaluar_plazo`](../../services/subasta_service.py) |
| **CU-16** | **Declarar subasta desierta** | *(extiende a CU-15)*, `Motor SQLite` | — *(transición automática a `CANCELADO`)* | [`ServicioSubasta._evaluar_plazo`](../../services/subasta_service.py) |

### Banda 4 · Backoffice, Panel Administrativo y Reglas (`onboarding_router.py` + `admin_router.py` + `config_router.py`)

| ID | Caso de uso en el diagrama | Actores | Endpoint(s) HTTP | Implementación en servicio |
|---|---|---|---|---|
| **CU-17** | **Validar documentos y perfiles KYC** | `Administrador Backoffice`, `Motor SQLite` | `GET /onboarding/admin/documentos`, `PATCH /onboarding/admin/documentos/{id}/validar`, `GET /onboarding/admin/dadores`, `PATCH /onboarding/admin/dadores/{id}/validar` | [`OnboardingService.validar_documento`](../../services/onboarding_service.py), [`validar_dador`](../../services/onboarding_service.py) |
| **CU-18** | **Consultar panel de resumen, cuentas y contratos** | `Administrador Backoffice`, `Motor SQLite` | `GET /admin/resumen`, `GET /admin/elementos/{tipo}`, `GET /auth/usuarios`, `GET /auth/usuarios/{usuario_id}` | [`admin_service.resumen`](../../services/admin_service.py), [`listar_elementos`](../../services/admin_service.py), [`UsuarioService`](../../services/usuario_service.py) |
| **CU-19** | **Dar de baja lógica contrato o cuenta** | `Administrador Backoffice`, `Motor SQLite` | `POST /admin/elementos/{tipo}/{elemento_id}/eliminar` | [`admin_service.eliminar`](../../services/admin_service.py) |
| **CU-20** | **Cancelar contrato administrativamente** | `Administrador Backoffice`, `Motor SQLite` | `POST /admin/elementos/contrato/{contrato_id}/cancelar`, `PATCH /contratos/{id}/estado` *(rol admin)* | [`admin_service.cancelar_contrato`](../../services/admin_service.py) |
| **CU-21** | **Registrar acción en historial de auditoría** | *(incluido por CU-19 y CU-20)*, `Motor SQLite` | — *(atómico en transacción)* | [`admin_service._operar`](../../services/admin_service.py) (tabla `acciones_admin`) |
| **CU-22** | **Consultar historial de auditoría** | `Administrador Backoffice`, `Motor SQLite` | `GET /admin/historial` | [`admin_service.historial`](../../services/admin_service.py) |
| **CU-23** | **Consultar y modificar reglas de negocio** | `Administrador Backoffice` *(sin `Motor SQLite`)* | `GET /configuracion`, `PATCH /configuracion` | [`ReglasNegocio`](../../domain/reglas.py) (en memoria) |

---

## 4. Justificación de relaciones `«include»` y `«extend»`

En UML 2.5, la dirección de las flechas distingue el sentido de dependencia entre los casos de uso:
* **`«include»` (Base ┄┄> Incluido):** el caso base **siempre** ejecuta obligatoriamente al caso incluido para poder completarse.
* **`«extend»` (Extensor ┄┄> Base):** el caso extensor agrega comportamiento **opcional o condicional** al caso base, sin ser necesario para su flujo normal.

| Relación | Origen ➔ Destino | Condición / Justificación en el código |
|---|---|---|
| `«include»` | `CU-05 (Crear contrato en borrador)` ➔ `CU-06 (Verificar KYC de dador aprobado)` | [`ServicioContrato.crear_contrato`](../../services/contrato_service.py) invoca siempre `onboarding_service.es_dador_aprobado(...)` antes de persistir el contrato; sin KYC `APROBADO` lanza `PermissionError` (HTTP `403`). |
| `«include»` | `CU-07 (Revisar postulaciones y adjudicar subasta)` ➔ `CU-08 (Rechazar ofertas competidoras)` | [`ServicioSubasta.adjudicar_subasta`](../../services/subasta_service.py) ejecuta siempre `_rechazar_postulaciones_competidoras(...)` dentro de la misma `transaccion_exclusiva`. |
| `«include»` | `CU-07 (Revisar postulaciones y adjudicar subasta)` ➔ `CU-09 (Cambiar estado de contrato)` | La adjudicación siempre transiciona el contrato a `ADJUDICADO` mediante `MaquinaEstadosContrato.cambiar_estado(...)` dentro de la misma transacción "todo o nada". |
| `«include»` | `CU-14 (Postular a carga)` ➔ `CU-15 (Evaluar plazo de cierre de subasta)` | [`ServicioSubasta.postular_a_carga`](../../services/subasta_service.py) llama obligatoriamente a `_evaluar_plazo(conn, contrato)` frente a `f_cierre_postulaciones` antes de aceptar la oferta. |
| `«include»` | `CU-19 (Dar de baja lógica contrato o cuenta)` ➔ `CU-21 (Registrar acción en historial de auditoría)` | [`admin_service.eliminar`](../../services/admin_service.py) delega en `_operar(...)`, que siempre inserta el registro en `acciones_admin` (tanto `Completado` como `Rechazado`). |
| `«include»` | `CU-20 (Cancelar contrato administrativamente)` ➔ `CU-21 (Registrar acción en historial de auditoría)` | [`admin_service.cancelar_contrato`](../../services/admin_service.py) comparte `_operar(...)`, garantizando trazabilidad obligatoria de toda cancelación administrativa en `acciones_admin`. |
| `«extend»` | `CU-02 (Adjuntar datos de onboarding al registro)` ➔ `CU-01 (Registrarse en la plataforma)` | Condición `[envía docs o perfil]`: [`UsuarioService.registrar_usuario`](../../services/usuario_service.py) solo invoca `cargar_documento` o `registrar_o_actualizar_perfil_dador` si `documentos` o `perfil_tributario` fueron enviados en el payload. |
| `«extend»` | `CU-13 (Filtrar cargas por criterios)` ➔ `CU-12 (Explorar cargas disponibles)` | Condición `[aplica filtros opcionales]`: [`ServicioSubasta.explorar_cargas`](../../services/subasta_service.py) devuelve todas las cargas disponibles por defecto y solo filtra si llegan `region`, `tipo_carroceria` o `distancia_max_km`. |
| `«extend»` | `CU-16 (Declarar subasta desierta)` ➔ `CU-15 (Evaluar plazo de cierre de subasta)` | Condición `[plazo vencido sin ofertas]`: en [`ServicioSubasta._evaluar_plazo`](../../services/subasta_service.py), solo cuando `f_cierre_postulaciones` expiró y no existe ninguna fila en `postulaciones`, el contrato pasa a `CANCELADO` (`DESIERTA`). |

---

## 5. Decisiones de alcance y observaciones honestas sobre el código

1. **Exclusión de funcionalidades no construidas:** En las historias iniciales (Hito 1) se mencionaban pagos en custodia (*Escrow*), notificaciones externas, gestión de flota de camiones o integración con SII. Al inspeccionar el repositorio completo, **ninguno de esos módulos está implementado**; incluirlos violaría la regla central de la Entrega 3 (*"describir el sistema que realmente construyeron"*).
2. **`CU-23` sin conexión a `Motor SQLite`:** [`routers/config_router.py`](../../routers/config_router.py) lee y actualiza atributos en memoria sobre el singleton [`ReglasNegocio`](../../domain/reglas.py) y no abre conexión a `camiones.db`. Por eso se resalta en verde y no tiene asociación hacia `Motor SQLite`.
3. **`Administrador Backoffice` excluido de `CU-01`:** [`UsuarioCrear.validar_rol`](../../domain/modelos_usuario.py) rechaza explícitamente cualquier rol distinto de `TRANSPORTISTA` o `DADOR_CARGA` al registrarse; las cuentas `ADMIN_BACKOFFICE` existen como cuentas semilla o internas ([`docs/panel-administracion.md`](../panel-administracion.md)).
4. **Observaciones reales de autorización en endpoints existentes:**
   * En [`main.py`](../../main.py), `config_router` exige sesión válida (`Depends(usuario_actual)`), pero aún no restringe `PATCH /configuracion` exclusivamente al rol `ADMIN_BACKOFFICE` mediante `administrador_actual`; el diagrama asigna `CU-23` al `Administrador Backoffice` porque es su actor funcional previsto.
   * En [`routers/onboarding_router.py`](../../routers/onboarding_router.py), los endpoints de dador y transportista toman `X-User-Id` por header tras validar la sesión JWT general, mientras que los endpoints `/onboarding/admin/*` sí exigen `administrador_actual`.
   * En [`routers/contratos_router.py`](../../routers/contratos_router.py), la cancelación por `PATCH /contratos/{contrato_id}/estado` cuando el actor es `ADMIN_BACKOFFICE` redirige internamente a `admin_service.cancelar_contrato`, manteniendo la consistencia con `CU-20` y `CU-21`.

---

## 6. Prueba de coherencia entre los cuatro diagramas

Siguiendo la **Prueba de Coherencia** de la rúbrica sobre el concepto central **`ContratoModelo`** y el caso de uso **`Crear contrato en borrador`**:

* **Casos de uso (`1-casos-de-uso.xml`):** el actor `Dador de carga` ejecuta **`Crear contrato en borrador`**, el cual incluye `Verificar KYC de dador aprobado` y persiste en el actor externo `Motor SQLite`.
* **Secuencia ([`3-secuencia.md`](3-secuencia.md)):** modela exactamente el caso de uso **`Crear contrato en borrador`** con los participantes `Dador de carga`, `contratos_router`, `ServicioContrato`, `OnboardingService` (`es_dador_aprobado`) y `SQLite`.
* **Componentes ([`4-componentes.md`](4-componentes.md)):** muestra la ruta `Cliente web / Electron` ➔ `API FastAPI` ➔ `Servicios de negocio` (`ServicioContrato.crear_contrato`) ➔ `Dominio de contratos` (`ContratoModelo`, `MaquinaEstadosContrato`) ➔ `Acceso a SQLite` ➔ `«external» Motor SQLite` (`camiones.db`).
* **Clases ([`diagrama_clases.xml`](diagrama_clases.xml)):** define `UsuarioModelo`, `DadorCarga` (con `estado_validacion`), `ContratoCrear`, `ContratoModelo` (estado inicial `BORRADOR`), `ContratoBase` y `MaquinaEstadosContrato` con los nombres exactos de Python.

---

## 7. Cumplimiento de la rúbrica (Entrega 3 · Criterio "Casos de uso")

| Requisito de la rúbrica | Mínimo exigido | Implementación en `1-casos-de-uso.xml` | Estado |
|---|---|---|---|
| **Actores** | Al menos 2 actores | **4 actores**: 3 primarios (`Dador de carga`, `Transportista`, `Administrador Backoffice`) + 1 sistema externo (`Motor SQLite`) | Cumplido |
| **Casos de uso y alcance** | Al menos 5 casos de uso cubriendo todo lo implementado | **23 casos de uso** cubriendo los 6 routers reales (`/auth`, `/onboarding`, `/contratos`, `/subastas`, `/admin`, `/configuracion`) | Cumplido |
| **Frontera del sistema** | Frontera dibujada | Marco `«system» Camiones Contratos (MansoViaje)` conteniendo los 23 casos de uso y dejando los 4 actores fuera | Cumplido |
| **`«include»` / `«extend»` orientados** | Al menos una relación correctamente orientada | **6 `«include»`** (Base ➔ Incluido) y **3 `«extend»`** (Extensor ➔ Base con condición entre corchetes) | Cumplido |
| **Sistemas externos como actores** | Sistemas externos representados como actores | `Motor SQLite (camiones.db)` fuera de la frontera como actor externo `«system»` | Cumplido |
| **Fuente editable y nota de lectura** | Archivo editable (`.xml`/`.drawio`) + nota de 5–10 líneas | [`1-casos-de-uso.xml`](1-casos-de-uso.xml) + Nota de lectura (Sección 1) + explicación integral | Cumplido |
