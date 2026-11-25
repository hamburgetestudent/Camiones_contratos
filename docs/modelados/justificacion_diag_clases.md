# Justificación y Decisiones de Diseño · Diagrama de Clases (`diagrama_clases.xml`)

> **Proyecto:** MansoViaje / `Camiones_contratos` — Plataforma de Centralización de Contratos de Transporte Terrestre  
> **Asignatura:** ISF 225 · Fundamentos de Ingeniería de Software · Entrega 3 (Modelamiento del sistema)  
> **Archivo editable del diagrama:** [`diagrama_clases.xml`](diagrama_clases.xml) (formato nativo `<mxfile>` de diagrams.net / draw.io)

---

## 1. Nota de lectura (resumen ejecutivo para la entrega)

> *Párrafo listo para copiar en `docs/modelado/2-clases.md` (entre 5 y 10 líneas, centrado en el **porqué** de las decisiones arquitectónicas más que en describir las cajas):*

Modelamos el dominio mediante una única entidad `UsuarioModelo` diferenciada por `RolUsuario` y enriquecida por composición con `DadorCarga` y `DocumentoTransportista`, evitando jerarquías rígidas de herencia por rol porque un usuario adquiere sus credenciales tributarias o documentales en el flujo posterior de onboarding. Las entidades persistidas (`UsuarioModelo`, `ContratoModelo`, `PostulacionModelo`, `DocumentoTransportista`) heredan sus invariantes Pydantic de clases `*Base` para reutilizar las validaciones de entrada antes de tocar SQLite. Elegimos **composición** sobre `DadorCarga` (`DatosFacturacion`), `DocumentoTransportista` (multiplicidad `0..5` acotada por `UNIQUE(user_id, tipo)` y los 5 literales de `TipoDocumento`) y `PostulacionModelo` porque la base de datos aplica `ON DELETE CASCADE` desde sus agregados raíz; en cambio, modelamos las referencias de `UsuarioModelo` hacia `ContratoModelo` (`genera` y `adjudicado a`) como **asociaciones** independientes porque los contratos no se eliminan en cascada y poseen dos roles de usuario distintos. Centralizamos el ciclo de vida en la jerarquía genérica `MaquinaEstadosBase<S>` (Patrón *State*) y las tolerancias financieras en el singleton `ReglasNegocio` para evitar condicionales dispersos en los servicios, omitiendo deliberadamente entidades no construidas como `Camion` o la antigua capa `dao/` ya eliminada del repositorio.

---

## 2. Correspondencia 1-a-1 con el código y la base de datos

La regla central de la Entrega 3 exige que **las clases del diagrama usen los mismos nombres que las entidades del código real**, sin inventar módulos planificados que no existen. El diagrama contiene **15 clases** y **8 enumeraciones** extraídas directamente de `Camiones_contratos/domain/` y contrastadas con `Camiones_contratos/backend/app/db/schema.sql`.

### 2.1 Clases del dominio y modelo de datos (15 clases)

| # | Clase en el diagrama | Estereotipo / Rol | Archivo fuente y líneas | Tabla SQLite asociada |
|---|---|---|---|---|
| 1 | `UsuarioBase` | Clase base de validación | `Camiones_contratos/backend/app/modules/usuarios/models.py` (L37–42) | — (heredada) |
| 2 | `UsuarioModelo` | Entidad persistida | `Camiones_contratos/backend/app/modules/usuarios/models.py` (L109–115) | `usuarios` (`schema.sql` L14–22) |
| 3 | `DadorCarga` | Entidad persistida (KYC) | `Camiones_contratos/backend/app/modules/onboarding/models.py` (L176–188) | `dadores_carga` (`schema.sql` L28–37) |
| 4 | `DatosFacturacion` | `«value object»` | `Camiones_contratos/backend/app/modules/onboarding/models.py` (L112–121) | Columnas en `dadores_carga` |
| 5 | `DocumentoTransportistaBase` | Clase base de validación | `Camiones_contratos/backend/app/modules/onboarding/models.py` (L37–51) | — (heredada) |
| 6 | `DocumentoTransportista` | Entidad persistida (KYC) | `Camiones_contratos/backend/app/modules/onboarding/models.py` (L81–94) | `documentos_transportista` (`schema.sql` L43–52) |
| 7 | `ContratoBase` | Clase base + invariantes | `Camiones_contratos/backend/app/modules/contratos/models.py` (L78–245) | — (heredada) |
| 8 | `ContratoCrear` | `«DTO»` de entrada | `Camiones_contratos/backend/app/modules/contratos/models.py` (L248–251) | — (payload HTTP) |
| 9 | `ContratoModelo` | Entidad persistida (raíz) | `Camiones_contratos/backend/app/modules/contratos/models.py` (L254–267) | `contratos` (`schema.sql` L58–83) |
| 10 | `PostulacionBase` | Clase base de validación | `Camiones_contratos/backend/app/modules/subastas/models.py` (L45–64) | — (heredada) |
| 11 | `PostulacionModelo` | Entidad persistida | `Camiones_contratos/backend/app/modules/subastas/models.py` (L73–84) | `postulaciones` (`schema.sql` L89–99) |
| 12 | `ReglasNegocio` | `«singleton»` de reglas | `Camiones_contratos/backend/app/modules/configuracion/reglas.py` (L10–89) | — (en memoria, thread-safe) |
| 13 | `MaquinaEstadosBase<S: StrEnum>` | `«abstract»` genérica | `Camiones_contratos/backend/app/core/maquina_estados.py` (L10–33) | — (comportamiento) |
| 14 | `MaquinaEstadosContrato` | Máquina de estados (State) | `Camiones_contratos/backend/app/modules/contratos/maquina_estados.py` (L55–150) | Gobierna `contratos.estado` |
| 15 | `MaquinaEstadoPostulacion` | Máquina de estados (State) | `Camiones_contratos/backend/app/modules/subastas/models.py` (L25–42) | Gobierna `postulaciones.estado` |

### 2.2 Enumeraciones del dominio (`StrEnum`, 8 enumeraciones)

| # | Enumeración | Valores literales en código | Archivo fuente y líneas | Almacenamiento en `schema.sql` |
|---|---|---|---|---|
| 1 | `RolUsuario` | `TRANSPORTISTA`, `DADOR_CARGA`, `ADMIN_BACKOFFICE`, `EMPRESA`, `INDEPENDIENTE` | `backend/app/modules/usuarios/models.py` (L24–29) | `usuarios.rol` (`TEXT`) |
| 2 | `EstadoUsuario` | `EN_REVISION`, `APROBADO` | `backend/app/modules/usuarios/models.py` (L32–34) | `usuarios.estado` (`TEXT`) |
| 3 | `EstadoValidacion` | `PENDIENTE`, `APROBADO`, `RECHAZADO` | `backend/app/modules/onboarding/models.py` (L18–21) | `dadores_carga.estado_validacion`, `documentos_transportista.estado` |
| 4 | `TipoDocumento` | `LICENCIA_CONDUCIR`, `PADRON_VEHICULO`, `REVISION_TECNICA`, `SEGURO_CARGA`, `ANTECEDENTES` | `backend/app/modules/onboarding/models.py` (L24–29) | `documentos_transportista.tipo` (`TEXT`) |
| 5 | `TipoCarga` | `GENERAL`, `REFRIGERADA`, `PELIGROSA`, `FRAGIL`, `GRANEL_LIQUIDO`, `GRANEL_SOLIDO`, `PERECEDERA`, `SOBREDIMENSIONADA`, `VIVA`, `VALORES`, `VEHICULAR` | `backend/app/modules/contratos/models.py` (L50–63) | `contratos.tipo_carga` (`TEXT`) |
| 6 | `Moneda` | `CLP`, `UF`, `UTM`, `USD`, `EUR`, `CNY`, `BRL` | `backend/app/modules/contratos/models.py` (L66–75) | `contratos.moneda` (`TEXT`) |
| 7 | `EstadoContrato` | `BORRADOR`, `PUBLICADO`, `EN_SUBASTA`, `EN_POSTULACION`, `ADJUDICADO`, `EN_TRANSITO`, `ENTREGADO`, `FINALIZADO`, `CANCELADO`, `EN_DISPUTA` | `backend/app/modules/contratos/maquina_estados.py` (L40–52) | `contratos.estado` (`TEXT`) |
| 8 | `EstadoPostulacion` | `BORRADOR`, `POSTULADA`, `SELECCIONADA`, `RECHAZADA` | `backend/app/modules/subastas/models.py` (L16–22) | `postulaciones.estado` (`TEXT`) |

---

## 3. Decisiones de modelado y su porqué

### D1. Usuario único con discriminador `RolUsuario` y perfiles por composición (sin herencia de roles)
- **Decisión:** Mantener `UsuarioModelo` como entidad única tipada por el atributo `rol: RolUsuario`, vinculada por composición opcional (`0..1`) a `DadorCarga` y composición múltiple (`0..5`) a `DocumentoTransportista`, en lugar de crear subclases `Transportista`, `Dador` o `Administrador` que hereden de `UsuarioModelo`.
- **Por qué en el código:** En `backend/app/modules/usuarios/models.py`, `RolUsuario` actúa como discriminador de rol (normalizando además los alias legados `"INDEPENDIENTE"` → `TRANSPORTISTA` y `"EMPRESA"` → `DADOR_CARGA` en `UsuarioCrear.normalizar_rol_entrada`). No existen clases hijas de usuario en Python ni tablas separadas para autenticarse en `schema.sql`: todos residen en `usuarios`, y la habilitación operativa KYC se construye agregando filas en `dadores_carga` o `documentos_transportista`.
- **Alternativa descartada:** Herencia de roles (`Transportista extends UsuarioModelo`), que duplicaría la lógica de autenticación/JWT (`UsuarioService`, `LoginService`) y contradeciría la estructura real de `usuarios`.

### D2. Jerarquías `*Base` → `*Modelo` e inclusión selectiva de `ContratoCrear` (`«DTO»`)
- **Decisión:** Conservar las superclases reales `UsuarioBase`, `DocumentoTransportistaBase`, `ContratoBase` y `PostulacionBase` heredadas por sus respectivos `*Modelo`, e incluir explícitamente `ContratoCrear` (estereotipado `«DTO»`), dejando fuera los DTOs HTTP transitorios de payload/respuesta.
- **Por qué:**
  1. En Pydantic v2, las superclases `*Base` encapsulan las reglas de validación reutilizables (por ejemplo, `ContratoBase` concentra los 19 atributos de especificación de carga y las 5 operaciones de invariantes de negocio: fechas, capacidad, requerimientos especiales y cuadratura financiera). Omitirlas haría perder las operaciones reales del dominio.
  2. Se incluyó `ContratoCrear` porque aparece explícitamente en los otros dos diagramas ya versionados por el equipo: en `docs/modelado/3-secuencia.md` (`origin/RamaSS`, *"solicitud que cumple el esquema `ContratoCrear`"*) y en la tabla de correspondencia de `docs/modelado/4-componentes.md` (`origin/Dev`, *"El router recibe `ContratoCrear` y delega la creación"*).
- **DTOs HTTP excluidos deliberadamente (y por qué):** Para evitar ruido visual en un diagrama de dominio, no se dibujaron esquemas estrictamente de transporte HTTP/endpoint que no definen entidades ni lógica de dominio propia:

| Esquema excluido | Archivo fuente | Razón de exclusión |
|---|---|---|
| `UsuarioCrear` | `backend/app/modules/usuarios/models.py` (L45–106) | DTO de registro HTTP que solo agrega `password` en claro y payloads anidados opcionales para despachar al onboarding. |
| `CredencialesLogin`, `LoginEsquema`, `RespuestaLogin` | `backend/app/modules/usuarios/models_login.py` (L17–89) | Contrato HTTP OAuth2 Bearer de `/auth/login`; no representa estado persistido ni entidad de negocio. |
| `CargarDocumentoDTO`, `ValidarDocumentoDTO`, `EstadoOnboardingTransportistaDTO`, `CrearPerfilDadorDTO`, `ValidarPerfilDadorDTO` | `backend/app/modules/onboarding/models.py` | Envoltorios de petición/respuesta para endpoints de carga y revisión backoffice (`backend/app/modules/onboarding/router.py`). |
| `PostulacionCrear` | `backend/app/modules/subastas/models.py` (L67–70) | Alias vacío (`pass`) de `PostulacionBase` usado solo en la firma del endpoint `/subastas/postular`. |
| `SolicitudCambioEstado`, `SolicitudAdjudicacion`, `ActualizarConfiguracionNegocio` | `backend/app/modules/contratos/router.py`, `backend/app/modules/subastas/router.py`, `backend/app/modules/configuracion/router.py` | Esquemas locales de la capa de presentación/routers (`Extra="forbid"`). |

### D3. `DatosFacturacion` como `«value object»` embebido
- **Decisión:** Modelar `DatosFacturacion` con estereotipo `«value object»` unido por composición `1` ◆── `1` a `DadorCarga`.
- **Por qué:** En `backend/app/modules/onboarding/models.py` (L176–188), `DadorCarga` declara `datos_facturacion: DatosFacturacion` como atributo obligatorio sin identidad propia (`id`), agrupando `razon_social`, `direccion` y `correo_facturacion`. Su ciclo de vida depende íntegramente del perfil `DadorCarga`, aunque en SQLite (`schema.sql` L28–37) se persista aplanado en columnas de la tabla `dadores_carga` por simplicidad relacional.

### D4. Criterio de Composición vs. Asociación y justificación de multiplicidades exactas
- **Regla UML 2.5 aplicada:** Una **composición** (`◆──`) exige dependencia existencial y un **único propietario** (*whole*). En el esquema SQLite (`Camiones_contratos/backend/app/db/schema.sql`), exactamente tres relaciones poseen `ON DELETE CASCADE` desde un padre único:
  1. `UsuarioModelo` (`1`) ◆── (`0..1`) `DadorCarga`: `dadores_carga.user_id` tiene restricción `UNIQUE` y `ON DELETE CASCADE` (`schema.sql` L30, L36). Un usuario puede no tener perfil dador (`0`, si es transportista o admin) o tener como máximo uno (`1`).
  2. `UsuarioModelo` (`1`) ◆── (`0..5`) `DocumentoTransportista`: `documentos_transportista` tiene `ON DELETE CASCADE` sobre `user_id` y restricción `UNIQUE(user_id, tipo)` (`schema.sql` L50–51). Como `TipoDocumento` (`backend/app/modules/onboarding/models.py` L24–29) define exactamente **5 tipos posibles** (`LICENCIA_CONDUCIR`, `PADRON_VEHICULO`, `REVISION_TECNICA`, `SEGURO_CARGA`, `ANTECEDENTES`), la cota superior exacta de documentos distintos por transportista es `5`, de ahí la multiplicidad **`0..5`** (en lugar de un genérico `0..*`).
  3. `ContratoModelo` (`1`) ◆── (`0..*`) `PostulacionModelo`: `postulaciones.carga_id` tiene `ON DELETE CASCADE` sobre `contratos(id)` (`schema.sql` L98). Una postulación no puede existir sin una carga/contrato (`1` en el lado del todo), y un contrato puede recibir cero o muchas ofertas (`0..*`).
- **Por qué `PostulacionModelo` ↔ `UsuarioModelo` es Asociación (`1` ← `0..*`) y no Composición:** En UML 2.5 un objeto hijo no puede ser parte compuesta de dos todos simultáneos. Como la tabla `postulaciones` cascada al borrar el contrato (`carga_id`) y no declara cascada sobre `transportista_id`, la relación desde `UsuarioModelo` (`envía`) se modela como **asociación dirigida** con multiplicidad `1` (todo ofertante es un usuario transportista) a `0..*` (un transportista puede enviar múltiples ofertas).
- **Doble asociación `UsuarioModelo` ──> `ContratoModelo`:** Un `ContratoModelo` referencia a `UsuarioModelo` en dos roles semánticamente distintos:
  - `genera (id_empresa_generadora)`: `1` (siempre existe un dador creador obligatorio en `ContratoBase`) a `0..*` (un dador puede publicar múltiples contratos).
  - `adjudicado a (id_transportista)`: `0..1` (el atributo `id_transportista: UUID | None` es nulo mientras el contrato está en `BORRADOR`, `PUBLICADO`, `EN_SUBASTA` o `EN_POSTULACION`, y toma un único transportista al pasar a `ADJUDICADO`) a `0..*` (un transportista puede adjudicarse cero o muchos contratos).

### D5. Fidelidad estricta al sistema construido: omisión de `Camion` y de la antigua capa `dao/`
- **Ausencia de clase `Camion`:** Aunque `ContratoModelo` incluye `id_camion: UUID | None` (`backend/app/modules/contratos/models.py` L264) y `contratos.id_camion` existe en `schema.sql` L81, **no existe ninguna clase, modelo Pydantic, servicio, router ni tabla SQLite `camiones` en el código actual**. Tampoco `MaquinaEstadosContrato.cambiar_estado` ni `ServicioSubasta.adjudicar_subasta` exigen `id_camion` como obligatorio. Inventar una clase `Camion` violaría la regla de la rúbrica (*"Un diagrama precioso de un sistema que no construyeron vale cero"*). Se conserva el atributo `id_camion: UUID | None` en `ContratoModelo` tal cual aparece en el código y se documenta esta brecha de alcance aquí.
- **Ausencia de capa `dao/` (`BaseDAO`, `DAOMemoria`, `ContratoDAO`, etc.):** En versiones tempranas del proyecto (reflejadas todavía en textos antiguos de `README.md` y `docs_clases/Arquitectura.md`), la persistencia usaba una capa `dao/` en memoria. Sin embargo, el historial Git muestra que los commits `27ddd4d` a `6f5063e` (*"Eliminar carpeta dao al completar migracion a SQLite"*) eliminaron completamente la carpeta `dao/`, migrando los servicios a consultas SQL directas mediante `backend/app/db/conexion.py`. Por ello el diagrama de clases **no incluye clases DAO fantasma** y refleja la arquitectura real vigente (también consistente con `docs/modelado/4-componentes.md` en `origin/Dev`).
- **Ocultamiento de capas de servicio y routers (`ServicioContrato`, `ServicioSubasta`, `OnboardingService`, `UsuarioService`, `LoginService`, `routers/*`):** Las clases de servicio y routers son objetos de coordinación/orquestación stateless que ya están representados en el **Diagrama de Componentes** (`4-componentes.drawio`) y en el **Diagrama de Secuencia** (`3-secuencia.md`). Mantener el Diagrama de Clases enfocado en los **conceptos del dominio, reglas, máquinas de estado y entidades persistidas** responde exactamente a la pregunta de la rúbrica para este artefacto: *"Qué conceptos existen en el dominio, con sus atributos, sus relaciones y sus multiplicidades"*.

### D6. Jerarquía de Máquinas de Estado (`MaquinaEstadosBase<S>` — Patrón *State*)
- **Decisión:** Modelar `MaquinaEstadosBase<S: StrEnum>` como clase base genérica (`«abstract»`) de la que heredan `MaquinaEstadosContrato` (`«bind» S = EstadoContrato`) y `MaquinaEstadoPostulacion` (`«bind» S = EstadoPostulacion`), conectadas por dependencia `«gobierna»` a `ContratoModelo` y `PostulacionModelo`.
- **Por qué:** Desacopla el grafo de transiciones permitidas (`TRANSICIONES_PERMITIDAS`) y sus invariantes (estados terminales `FINALIZADO` y `CANCELADO`, obligatoriedad de `id_transportista` al adjudicar, asignación de `fecha_publicacion`) de los servicios transaccionales (`ServicioContrato.cambiar_estado`, `ServicioSubasta.postular_a_carga`, `ServicioSubasta.adjudicar_subasta`).
- **Observación transparente sobre `MaquinaEstadoPostulacion`:** La clase `MaquinaEstadoPostulacion` existe formalmente en `backend/app/modules/subastas/models.py` (L25–42) con sus reglas de transición y está cubierta por pruebas unitarias dedicadas en `backend/tests/subastas/test_modelos_postulacion.py` (`test_transiciones_maquina_postulacion`, L40–55). Sin embargo, al revisar `backend/app/modules/subastas/service.py` (`adjudicar_subasta`, L308–318), el servicio valida la transición del contrato mediante `MaquinaEstadosContrato.validar_transicion(...)` y asigna `postulacion.estado = EstadoPostulacion.SELECCIONADA` directamente sin invocar `MaquinaEstadoPostulacion.validar_transicion(...)`. Se incluye `MaquinaEstadoPostulacion` porque forma parte real del código en `backend/app/modules/subastas/models.py` y se deja constancia explícita de este acoplamiento pendiente de reforzar en el servicio.

### D7. `ReglasNegocio` como `«singleton»` parametrizable
- **Decisión:** Modelar `ReglasNegocio` con estereotipo `«singleton»`, mostrando tanto sus atributos estáticos privados (`-_instancia`, `-_lock`) como los parámetros configurables en caliente (`IVA_PORCENTAJE`, `TOLERANCIA_MAX`, `ANTICIPACION_MIN_H`), sus valores por defecto y sus métodos de clase (`obtener_configuracion`, `actualizar_configuracion`, `reseteo_defaults`).
- **Por qué:** `ContratoBase._validar_fechas` y `ContratoBase._validar_coherencia_financiera` (`backend/app/modules/contratos/models.py` L139, L203, L210) consultan directamente `ReglasNegocio.ANTICIPACION_MIN_H`, `ReglasNegocio.TOLERANCIA_MAX` y `ReglasNegocio.IVA_PORCENTAJE`. Esa llamada justifica la dependencia `ContratoBase` ┄┄> `ReglasNegocio` (`«use» valida con`).
- **Nota de implementación:** Aunque la clase define `__new__` para mantener una única instancia en memoria (`_instancia`), actualmente el estado mutable reside en atributos de clase (`cls.IVA_PORCENTAJE`, etc.) y el candado `_lock: threading.Lock` está declarado en la clase (`backend/app/modules/configuracion/reglas.py` L20) aunque las lecturas/escrituras se hacen a nivel de atributos de clase. El diagrama reproduce fielmente todos los miembros reales declarados en la clase.

### D8. Convenciones UML y divergencias reales entre Python (`domain/`) y SQLite (`schema.sql`)
- **Visibilidad y miembros estáticos:**
  - `+` (público): campos Pydantic y métodos públicos sin prefijo `_`.
  - `#` (protegido): métodos internos `_validar_fechas`, `_validar_carga_y_capacidad`, `_validar_requerimientos_especiales`, `_validar_coherencia_financiera` en `ContratoBase`, protegidos por convención Python (`_`) para encapsular cada invariante y permitir su uso/extensión desde la jerarquía.
  - `-` (privado): estado interno de control del singleton en `ReglasNegocio` (`-_instancia`, `-_lock`).
  - **Subrayado (`<u>...</u>`):** atributos y métodos de clase (`@classmethod` o variables compartidas de clase en `ReglasNegocio`, `DocumentoTransportistaBase` y `MaquinaEstadosBase` y sus subclases).
- **Divergencias detectadas y documentadas entre modelos Pydantic y SQLite:**
  1. **`input_camionKG` vs. `input_camion_kg`:** En `backend/app/modules/contratos/models.py` (L101) el campo se llama `input_camionKG` (con `# noqa: N815`), mientras que en `schema.sql` (L66) la columna es `input_camion_kg`; `backend/app/modules/contratos/service.py` realiza la traducción en `_contrato_a_parametros` y `_fila_a_contrato`. El diagrama conserva `input_camionKG` por corresponder a la entidad de dominio en Python.
  2. **`usuarios.created_at` solo en SQLite:** La tabla `usuarios` (`schema.sql` L21) almacena `created_at`, pero `UsuarioModelo` (`backend/app/modules/usuarios/models.py` L109–115) no expone ese atributo en memoria.
  3. **`DatosFacturacion` embebido vs. plano:** En Python es un objeto compuesto (`DadorCarga.datos_facturacion`); en SQLite sus tres campos (`razon_social`, `direccion`, `correo_facturacion`) viven directamente en `dadores_carga`.
  4. **Visibilidad de `password_hash` en `UsuarioModelo`:** En `backend/app/modules/usuarios/models.py` (L111), `password_hash: str` es un campo público del modelo Pydantic que incluso se retorna en `backend/app/modules/usuarios/router.py` (`response_model=UsuarioModelo` en `/auth/registro` y `/auth/usuarios`). El diagrama lo refleja honestamente con visibilidad `+` tal como está implementado hoy, evidenciando una oportunidad de mejora (usar un DTO de salida sin hash).

### D9. Elección del formato `.xml` editable (diagrams.net / draw.io)
- **Decisión:** Entregar la fuente editable en formato XML nativo `<mxfile>` de **diagrams.net / draw.io** (`diagrama_clases.xml`), respetando la misma herramienta y paleta cromática (`#18374b`, `#355169`) utilizada por el equipo en `Camiones_contratos/docs/modelado/4-componentes.drawio`.
- **Cómo integrarlo en la carpeta oficial del repositorio (`Camiones_contratos/docs/modelado/`):**
  1. Abrir `diagrama_clases.xml` en [app.diagrams.net](https://app.diagrams.net/) o con la extensión de Draw.io en VS Code y exportar la imagen PNG como `2-clases.png`.
  2. Copiar el editable (como `2-clases.drawio` o `2-clases.xml`), el PNG exportado (`2-clases.png`) y la nota de lectura de la Sección 1 dentro de `Camiones_contratos/docs/modelado/2-clases.md`.

---

## 4. Tabla maestra de las 17 relaciones y multiplicidades

> **Nota UML 2.5:** En UML, las relaciones de **Asociación** y **Composición** llevan multiplicidades en ambos extremos (y en nuestro diagrama todas las tienen). Las relaciones de **Herencia/Generalización** (`──▷`) y **Dependencia** (`┄┄>`) **no llevan multiplicidades** por definición del estándar UML.

| # | Origen | Destino | Tipo UML | Rol / Estereotipo | Mult. Origen | Mult. Destino | Evidencia en código / SQLite |
|---|---|---|---|---|---|---|---|
| 1 | `UsuarioModelo` | `UsuarioBase` | Herencia | — | N/A | N/A | `class UsuarioModelo(UsuarioBase)` (`modelos_usuario.py:109`) |
| 2 | `UsuarioModelo` | `DadorCarga` | Composición | `posee perfil` | `1` | `0..1` | `dadores_carga.user_id` `UNIQUE` + `ON DELETE CASCADE` (`schema.sql:30,36`) |
| 3 | `DadorCarga` | `DatosFacturacion` | Composición | `contiene` | `1` | `1` | `datos_facturacion: DatosFacturacion` (`modelos_onboarding.py:184`) |
| 4 | `DocumentoTransportista` | `DocumentoTransportistaBase` | Herencia | — | N/A | N/A | `class DocumentoTransportista(DocumentoTransportistaBase)` (`modelos_onboarding.py:81`) |
| 5 | `UsuarioModelo` | `DocumentoTransportista` | Composición | `carga` | `1` | `0..5` | `ON DELETE CASCADE` + `UNIQUE(user_id, tipo)` + 5 valores en `TipoDocumento` (`schema.sql:50-51`) |
| 6 | `UsuarioModelo` | `ContratoModelo` | Asociación dirigida | `genera (id_empresa_generadora)` | `1` | `0..*` | `id_empresa_generadora: UUID` obligatorio (`modelos.py:81`) |
| 7 | `UsuarioModelo` | `ContratoModelo` | Asociación dirigida | `adjudicado a (id_transportista)` | `0..1` | `0..*` | `id_transportista: UUID \| None` asignado al adjudicar (`modelos.py:261`) |
| 8 | `ContratoModelo` | `ContratoBase` | Herencia | — | N/A | N/A | `class ContratoModelo(ContratoBase)` (`modelos.py:254`) |
| 9 | `ContratoCrear` | `ContratoBase` | Herencia | — | N/A | N/A | `class ContratoCrear(ContratoBase)` (`modelos.py:248`) |
| 10 | `ContratoModelo` | `PostulacionModelo` | Composición | `recibe (carga_id)` | `1` | `0..*` | `FOREIGN KEY (carga_id) REFERENCES contratos(id) ON DELETE CASCADE` (`schema.sql:98`) |
| 11 | `PostulacionModelo` | `PostulacionBase` | Herencia | — | N/A | N/A | `class PostulacionModelo(PostulacionBase)` (`postulacion.py:73`) |
| 12 | `UsuarioModelo` | `PostulacionModelo` | Asociación dirigida | `envía (transportista_id)` | `1` | `0..*` | `transportista_id: UUID` obligatorio (`postulacion.py:49`) |
| 13 | `ContratoBase` | `ReglasNegocio` | Dependencia | `«use» valida con` | N/A | N/A | `from app.modules.configuracion.reglas import ReglasNegocio` (`modelos.py:31,139,203,210`) |
| 14 | `MaquinaEstadosContrato` | `MaquinaEstadosBase<S>` | Herencia | `«bind» S = EstadoContrato` | N/A | N/A | `class MaquinaEstadosContrato(MaquinaEstadosBase[EstadoContrato])` (`maquina_estados.py:55`) |
| 15 | `MaquinaEstadoPostulacion` | `MaquinaEstadosBase<S>` | Herencia | `«bind» S = EstadoPostulacion` | N/A | N/A | `class MaquinaEstadoPostulacion(MaquinaEstadosBase[EstadoPostulacion])` (`postulacion.py:25`) |
| 16 | `MaquinaEstadosContrato` | `ContratoModelo` | Dependencia | `«gobierna» ciclo de vida` | N/A | N/A | `MaquinaEstadosContrato.cambiar_estado(...)` muta `ContratoModelo.estado` (`maquina_estados.py:100`) |
| 17 | `MaquinaEstadoPostulacion` | `PostulacionModelo` | Dependencia | `«gobierna» transiciones` | N/A | N/A | `EstadoPostulacion` y mapa de transiciones sobre postulaciones (`postulacion.py:25-42`) |

---

## 5. Prueba de coherencia con los demás diagramas del repositorio

La rúbrica exige tomar un concepto central del dominio y verificar que aparece sin contradicciones en los cuatro diagramas y en el código:

- **Trazabilidad de `ContratoModelo` y `ContratoCrear`:**
  - En **`3-secuencia.md`** (`origin/RamaSS`): el Dador de carga envía `POST /contratos` con un payload `ContratoCrear`, `ServicioContrato` verifica `OnboardingService.es_dador_aprobado(id_empresa_generadora)` (que consulta `dadores_carga` / `DadorCarga`), construye `ContratoModelo` en estado `BORRADOR` y lo persiste en SQLite.
  - En **`4-componentes.md` / `4-componentes.drawio`** (`origin/Dev`): `backend/app/modules/contratos/router.py` recibe `ContratoCrear` y delega en `ServicioContrato.crear_contrato()`, el cual usa `ContratoModelo` y `MaquinaEstadosContrato` para operar y persistir mediante `backend/app/db/conexion.py` en `sqlite3`.
  - En **este Diagrama de Clases (`diagrama_clases.xml`)**: `ContratoCrear` y `ContratoModelo` heredan las mismas reglas de `ContratoBase`, `ContratoModelo` vincula `id_empresa_generadora` hacia `UsuarioModelo`, `MaquinaEstadosContrato` gobierna el atributo `estado: EstadoContrato` (con valor inicial `BORRADOR`), y `DadorCarga` refleja el perfil tributario consultado por onboarding antes de permitir la creación.

---

## 6. Verificación contra la rúbrica (Entrega 3 · Criterio "Clases")

| Requisito de la rúbrica | Mínimo exigido | Nivel Logrado (100%) en este entregable | Estado |
|---|---|---|---|
| **Cantidad de clases** | Al menos 5 clases | **15 clases** + **8 enumeraciones** que cubren usuarios, onboarding KYC, contratos, subastas/postulaciones, máquinas de estado y reglas de negocio | Cumplido |
| **Atributos con tipo y visibilidad** | Atributos con tipo y visibilidad | Todos los atributos y operaciones con visibilidad UML (`+`, `#`, `-`), tipo exacto de Python/Pydantic (`UUID`, `str`, `float`, `AwareDatetime`, `StrEnum`, `T \| None`) y subrayado en miembros de clase | Cumplido |
| **Multiplicidades completas** | Multiplicidades en ambos extremos de cada relación | Las 7 relaciones aplicables (4 composiciones y 3 asociaciones) tienen multiplicidad explícita y justificada en ambos extremos (`1`, `0..1`, `0..5`, `0..*`) | Cumplido |
| **Relaciones no simples justificadas** | Al menos una relación distinta de asociación simple, justificada | **7 herencias**, **4 composiciones** (con `ON DELETE CASCADE` documentado) y **3 dependencias** (`«use»`, `«gobierna»`), todas justificadas en la Sección 3 y 4 | Cumplido |
| **Nombres iguales a los del código** | Corresponder a las entidades del código | 100 % de nombres de clases, enums, atributos y métodos idénticos a `Camiones_contratos/domain/*.py` (incluyendo `input_camionKG` y `MaquinaEstadoPostulacion`) | Cumplido |
| **Archivo fuente editable + Nota de lectura** | Fuente editable (`.xml`/`.drawio`) y nota de 5–10 líneas | Fuente editable XML nativa `<mxfile>` (`diagrama_clases.xml`) + Nota de lectura lista (Sección 1) + Justificación exhaustiva (`justificacion_diag_clases.md`) | Cumplido |
