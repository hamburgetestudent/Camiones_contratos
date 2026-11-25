# Panel de administración

El rol `ADMIN_BACKOFFICE` entra a **Inicio**, **Gestión de contratos**, **Gestión de cuentas** e **Historial de acciones**. Los tres roles usan la misma barra lateral y el mismo encabezado. El menú toma sus accesos del rol que devuelve FastAPI al validar la sesión. La revisión documental y tributaria continúa disponible en el backend para sus integraciones existentes.

## Recorrido del administrador

1. Iniciar sesión. El resumen muestra contratos actualmente publicados y visibles, cuentas que pueden iniciar sesión y acciones administrativas completadas hoy. Cada indicador abre la consulta correspondiente. El día y las horas del historial se muestran en UTC.
2. Abrir **Gestión de contratos**, seleccionar **Ver detalle** y comprobar la ruta, el identificador y el estado. **Eliminar contrato** se ofrece únicamente en `PUBLICADO`. La confirmación identifica el contrato y exige un motivo.
3. Tras la baja, el detalle permite consultar su historial. **Incluir eliminados** recupera el contrato en el listado administrativo. La carga deja de admitir postulaciones, adjudicaciones y cambios de estado. Conserva su estado operativo y sus relaciones.
4. En **Gestión de cuentas**, la baja de un dador o transportista impide iniciar sesión y usar una sesión anterior. **Incluir eliminadas** permite recuperar su ficha. Sus contratos siguen con sus estados y participantes originales.
5. **Historial de acciones** admite filtros por fechas, nombre o ID del responsable, acción, resultado, tipo e identificador del elemento. El detalle muestra motivo, antes, después y causa del rechazo. Inicio muestra las últimas diez operaciones, incluidos los rechazos.

Una cuenta en revisión puede iniciar sesión en el modelo actual. Por eso el contador de cuentas activas incluye las cuentas en revisión y aprobadas que siguen habilitadas para acceder. El contador diario excluye los intentos rechazados.

## Datos y concurrencia

Al abrir una base existente, `backend/app/db/conexion.py` agrega de forma idempotente la columna `eliminado` a contratos y usuarios, con valor inicial 0. El esquema agrega `acciones_admin` y `sesiones_cerradas`. Los datos existentes y sus claves siguen en sus tablas originales.

El servicio reserva la escritura en SQLite con `BEGIN IMMEDIATE` antes de comprobar el rol y releer el estado del elemento. Si otro proceso adjudica el contrato primero, la baja se rechaza. Si la baja ocurre primero, la carga desaparece de las consultas operativas que usan contratos y subastas. Una segunda confirmación registra un rechazo y genera una sola baja efectiva.

La modificación y su acción completada se confirman juntas. Si falla la escritura del historial, SQLite revierte la modificación. Un rechazo de negocio guarda su causa y no altera el elemento. El historial expone únicamente operaciones de lectura. Los valores antes y después contienen el estado y el indicador de baja.

La identidad del responsable se obtiene de la sesión y de la cuenta vigente. Un usuario autenticado sin permiso que intenta una baja válida recibe 403 y su intento queda registrado. Una petición sin sesión válida recibe 401. Los errores de formato HTTP/Pydantic se devuelven antes de iniciar una operación de negocio. El mecanismo de cierre de sesión almacena únicamente una huella del token hasta su expiración.

## Integración

| Ubicación | Responsabilidad |
|---|---|
| `frontend/src/paginas/login/` | Autenticación y entrada al panel. |
| `frontend/src/paginas/panel/roles.js`, `panel.js`, `estado.js` y `ui.js` | Opciones por rol, navegación con teclado, barra colapsable, sesión, estado compartido y utilidades de interfaz (módulos ES). |
| `frontend/src/paginas/panel/vistas/administracion/` (`index.js`, `inicio.js`, `listados.js`, `historial.js`, …) | Resumen, listados, confirmaciones y consultas al historial. |
| `backend/app/modules/admin/router.py` y `backend/app/modules/usuarios/sesion.py` | API del panel, permisos y verificación de sesiones. |
| `backend/app/modules/admin/service.py` | Consultas, bajas y registro dentro de una transacción. |
| `backend/app/modules/contratos/service.py`, `subasta_service.py` y `usuario_service.py` | Aplicación de la baja en los flujos operativos habituales. |
| `backend/app/db/schema.sql` y `backend/app/db/conexion.py` | Esquema y actualización automática de bases existentes. |

| Método y ruta | Uso |
|---|---|
| `GET /auth/sesion`, `POST /auth/logout` | Consultar la identidad vigente o cerrar la sesión actual. |
| `GET /admin/resumen` | Indicadores y actividad reciente en una sola lectura coherente. |
| `GET /admin/elementos/{tipo}` | Listar contratos o cuentas. Tipos válidos: `contrato`, `cuenta`. Filtros: `incluir_eliminados`, `estado`. |
| `POST /admin/elementos/{tipo}/{elemento_id}/eliminar` | Solicitar baja enviando `{"motivo":"Publicación duplicada","confirmado":true}`. |
| `GET /admin/historial` | Consultar eventos con `desde`, `hasta`, `administrador`, `accion`, `resultado`, `tipo` y `elemento_id`. |

Las llamadas a las rutas de negocio requieren el encabezado `Authorization: Bearer <token>` emitido por `POST /auth/login`. Para mantener las sesiones válidas entre reinicios o entre varios procesos de FastAPI, configura la misma clave privada en `JWT_SECRET_KEY`. En su ausencia se genera una clave local al proceso. Los eventos permanecen en SQLite en ambos casos.

## Cómo verificar

Desde la raíz, con las dependencias del proyecto y pytest instalados, ejecuta los siguientes comandos.

```powershell
python -m pytest backend/tests/admin/test_panel_admin.py -v
python -m pytest -q
```

La primera orden prepara una base temporal y comprueba todos los estados, cambio de estado antes de confirmar, repetición, filtros y rollback. También verifica una sesión ya emitida, un intento sin permisos y la recuperación de la cuenta, el contrato y el historial en un proceso Python nuevo.

La prueba de interfaz abre en Edge las mismas páginas HTML que carga Electron, inicia su propio FastAPI en un puerto libre y usa SQLite temporal. Requiere Node, Python, Playwright y Edge. Desde la carpeta `frontend`, instala las dependencias fijadas en el proyecto y ejecuta la prueba.

```powershell
npm ci
npm run test:panel
```

Puede indicarse otro ejecutable de Python con la variable `PYTHON`. El recorrido comprueba el login de los tres roles, los indicadores, volver desde la confirmación, eliminar una cuenta, consultar su historial, abrir el menú estrecho con teclado y cerrar sesión.

## Cancelación administrativa de un contrato

Se permite pasar a `CANCELADO` únicamente desde `PUBLICADO`, `EN_SUBASTA` o `EN_POSTULACION`, con motivo y confirmación. Los borradores siguen bajo gestión del dador. La adjudicación marca el límite porque ya hay un transportista seleccionado y otras ofertas descartadas. En tránsito o tras la entrega, una incidencia sigue el flujo de disputa; su resolución es independiente de este permiso. Un elemento eliminado o un contrato en estado terminal queda disponible para consulta.

Cancelar interrumpe una convocatoria válida. El contrato sigue visible como cancelado y conserva las ofertas. Eliminar lógicamente retira una publicación (por ejemplo, un duplicado) y exige el estado actual `PUBLICADO`. El cierre del plazo para ofertas es una tercera situación que todavía puede permitir una adjudicación.

`POST /admin/elementos/contrato/{id}/cancelar` recibe `motivo` y `confirmado`. Si un administrador solicita `CANCELADO` por `PATCH /contratos/{id}/estado`, se aplica la misma política. Ambas rutas releen el estado dentro de la transacción y registran el evento `cancelar_contrato` con su resultado. Los indicadores y filtros de auditoría incluyen estas operaciones.

En **Gestión de contratos → Ver detalle**, **Cancelar contrato** y **Eliminar contrato** tienen confirmaciones distintas. Tras cancelar se abre la ficha visible con estado `CANCELADO`. En **Historial de acciones**, el filtro **Cancelar contrato** permite revisar el motivo y el estado anterior.

## Protección de cuentas internas

El administrador puede dar de baja cuentas de transportistas y dadores de carga. Su propia cuenta, la de otro administrador y la última cuenta administrativa están protegidas, independientemente de cuántas sigan activas. El backend rechaza cada intento y conserva su motivo en el historial.

El rol administrativo es interno y no se obtiene por autorregistro. Protegerlo evita que un par retire el acceso de otro o deje la plataforma sin responsable. Si un administrador deja el equipo, el responsable de las cuentas internas debe gestionar el relevo fuera del panel.
