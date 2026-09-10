# [FE/BE] Implementación de módulo de Onboarding y Verificación de Documentación (KYC / Fleet Compliance) con Mock Data

**Título:** `[FE/BE] Implementación de módulo de Onboarding y Verificación de Documentación (KYC / Fleet Compliance) con Mock Data`

## Descripción
Implementar el flujo de carga y validación de documentación para los dos tipos de usuarios de la plataforma (Transportista y Dador de Carga), según el módulo 2 del roadmap. En esta fase no se requiere integración con base de datos real ni con APIs externas de validación tributaria; toda la persistencia debe manejarse de forma simulada en memoria.

---

## Etiquetas (Labels)
`feature`, `backend`, `frontend`, `mock-data`, `onboarding`, `kyc`

---

## Requerimientos Técnicos (Backend)

### 1. Persistencia y Mock Auth
* Crear un DAO/repositorio en memoria para **Usuarios** (`UsuarioDAOInMemory`), **Documentos del Transportista** (`DocumentoDAOInMemory`) y **Perfiles de Dador de Carga** (`DadorCargaDAOInMemory`).
* Estructurar el modelo de **Usuario** básico para habilitar las pruebas de onboarding:
  * `id` (`UUID`)
  * `nombre` (`string`)
  * `rol` (`enum`: `TRANSPORTISTA`, `DADOR_CARGA`, `ADMIN_BACKOFFICE`)

### 2. Modelo de Datos — Documentación del Transportista (`DocumentoTransportista`)
* `id` (`UUID`): Identificador único del documento (asignación automática en creación).
* `user_id` (`UUID`): Referencia al usuario transportista.
* `tipo` (`enum`): Tipo de documento:
  * `LICENCIA_CONDUCIR`
  * `PADRON_VEHICULO`
  * `REVISION_TECNICA`
  * `SEGURO_CARGA`
  * `ANTECEDENTES`
* `estado` (`enum`): Estado de validación (`PENDIENTE`, `APROBADO`, `RECHAZADO`). Por defecto: `PENDIENTE`.
* `archivo` (`string`): Ruta o referencia simulada al archivo cargado (ej: `uploads/doc_123.pdf`).
* `created_at` (`datetime`): Fecha y hora de carga (asignación automática en creación).

### 3. Modelo de Datos — Dador de Carga (`DadorCarga`)
* `id` (`UUID`): Identificador único.
* `user_id` (`UUID`): Referencia al usuario dador de carga.
* `rut_id_empresa` (`string`): Identificación tributaria (RUT/ID de empresa). Debe validarse formato básico.
* `datos_facturacion` (`object`): Razón social (`string`), dirección (`string`), correo de facturación (`string`).
* `estado_validacion` (`enum`): `PENDIENTE`, `APROBADO`, `RECHAZADO`. Por defecto: `PENDIENTE`.

### 4. Especificación de Endpoints (Faltantes en la propuesta original)
Se deben implementar los siguientes endpoints en un nuevo router `/onboarding`:

#### Transportista:
* `POST /onboarding/transportista/documentos`: Permite cargar un documento simulado. 
  * *Payload:* `tipo` (Enum), `archivo` (string).
  * *Headers:* `X-User-Id` (UUID del transportista).
* `GET /onboarding/transportista/documentos`: Retorna la lista de documentos cargados por el transportista actual.
  * *Headers:* `X-User-Id` (UUID).
* `GET /onboarding/transportista/estado`: Retorna el estado global del onboarding del transportista.
  * **Regla de Negocio:** El onboarding del transportista se considera `APROBADO` si y solo si tiene los **5 documentos** requeridos (`LICENCIA_CONDUCIR`, `PADRON_VEHICULO`, `REVISION_TECNICA`, `SEGURO_CARGA`, `ANTECEDENTES`) y todos están en estado `APROBADO`. Si alguno está `RECHAZADO`, el estado global es `RECHAZADO`. De lo contrario, está `PENDIENTE`.

#### Dador de Carga:
* `POST /onboarding/dador/perfil`: Registra los datos de facturación e ID de empresa.
  * *Payload:* `rut_id_empresa` (string), `datos_facturacion` (objeto).
  * *Headers:* `X-User-Id` (UUID).
* `GET /onboarding/dador/perfil`: Obtiene los datos tributarios y el `estado_validacion` actual.
  * *Headers:* `X-User-Id` (UUID).

#### Backoffice/Admin (Flujo de Aprobación):
* `GET /onboarding/admin/documentos`: Listar todos los documentos de transportistas pendientes de revisión.
* `PATCH /onboarding/admin/documentos/{documento_id}/validar`: Aprobar o rechazar un documento específico.
  * *Payload:* `estado` (`APROBADO` o `RECHAZADO`).
* `GET /onboarding/admin/dadores`: Listar todos los dadores de carga pendientes de validación tributaria.
* `PATCH /onboarding/admin/dadores/{dador_id}/validar`: Aprobar o rechazar el perfil del dador de carga.
  * *Payload:* `estado_validacion` (`APROBADO` o `RECHAZADO`).

### 5. Integración y Bloqueos de Negocio
* **Bloqueo para el Dador de Carga:** Modificar el servicio `ContratoService.crear_contrato` (o el router correspondiente) para validar que el `id_empresa_generadora` corresponda a un Dador de Carga cuyo `estado_validacion` sea `APROBADO`. Si no lo está, retornar un error `HTTP 403 Forbidden`.
* **Bloqueo para el Transportista:** Modificar el servicio `SubastaService.postular_a_carga` para consultar el estado global de onboarding del `transportista_id` en el servicio de onboarding en lugar de usar el parámetro simulado `onboarding_aprobado: bool` en el router. Retornar error `HTTP 403 Forbidden` si no está aprobado.

---

