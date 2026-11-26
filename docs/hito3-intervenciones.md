# Hito 3 · Diagnóstico de deuda técnica y refactorización

Revisamos tres operaciones del backend de Camiones Contratos: cómo se aprueba un documento o perfil, cómo se determina si un transportista está habilitado y cómo se busca una cuenta por correo. Para el **criterio 1**, identificamos dónde se repetía una regla, qué problema podía causar y cuánto trabajo requería cambiarla. Para el **criterio 2**, registramos el comportamiento inicial con pruebas y aplicamos cada refactorización en un commit independiente.

**Responsable de las tres intervenciones:** santiagosanchezgarcia10-byte, rama `RamaSS`. **Versión inicial:** [883b8d2](https://github.com/hamburgetestudent/Camiones_contratos/commit/883b8d2). En cada tabla comparamos el commit de la intervención con su padre y contamos solo el código de la operación descrita. Los enlaces a líneas distinguen la versión del cambio de la organización posterior del backend.

## 1. Aprobar o rechazar un documento o un perfil

**Qué encontramos y por qué lo priorizamos.** El administrador revisa tanto documentos de transportistas como perfiles tributarios de dadores de carga. Cada operación tenía su propia condición para admitir únicamente `APROBADO` o `RECHAZADO`, además de su propia copia del mensaje de error. Cambiar una sola copia podía dejar dos criterios para la misma decisión. Le dimos **prioridad alta** y lo hicimos primero porque la regla ya era idéntica y extraerla requería poco esfuerzo.

**Qué cambiamos.** Extrajimos la condición a `_validar_decision_revision()`. Cada operación busca primero el registro, llama al mismo validador y guarda la decisión dentro de su transacción. Si alguien intenta devolver un perfil rechazado a `PENDIENTE`, recibe el mismo error y el perfil sigue rechazado.

| Qué medimos en las dos operaciones | Antes | Después |
|---|---:|---:|
| Condiciones que definen qué decisiones acepta el administrador | 2 | 1 |
| Lugares donde se define el mensaje por decisión inválida | 2 | 1 |

**Dónde verlo.** En `backend/app/modules/onboarding/service.py` se puede seguir la regla y sus dos llamadas. El commit muestra los dos bloques originales que se reemplazaron. [Regla, líneas 42–44](https://github.com/hamburgetestudent/Camiones_contratos/blob/7858b4b/backend/app/modules/onboarding/service.py#L42-L44) · [Revisión del documento, línea 221](https://github.com/hamburgetestudent/Camiones_contratos/blob/7858b4b/backend/app/modules/onboarding/service.py#L221) · [Revisión del perfil, línea 241](https://github.com/hamburgetestudent/Camiones_contratos/blob/7858b4b/backend/app/modules/onboarding/service.py#L241) · [0f13942](https://github.com/hamburgetestudent/Camiones_contratos/commit/0f13942)

**Cómo lo comprobamos.** Las pruebas cubren la aprobación y el rechazo de documentos, el recurso inexistente y el intento de volver a pendiente. En este último caso se vuelve a consultar el perfil para comprobar el estado guardado. [Pruebas de documentos](../backend/tests/onboarding/test_validar_documento.py) · [Prueba del perfil, líneas 44–53](https://github.com/hamburgetestudent/Camiones_contratos/blob/7858b4b/backend/tests/onboarding/test_validar_perfil_dador.py#L44-L53)

## 2. Determinar el estado del transportista y explicar qué documentos faltan

**Qué encontramos y por qué lo priorizamos.** La consulta devuelve dos datos relacionados: el estado global del transportista y la lista de documentos que le faltan. Primero comprobaba si estaban todos los requeridos y luego recorría la lista otra vez para identificar los ausentes. Si esas comprobaciones evolucionaban por separado, la respuesta podía contradecirse. Le dimos **prioridad alta** por su impacto en la habilitación. La abordamos en segundo lugar porque, aunque el cambio se concentra en un método, había que comprobar la prioridad del rechazo y el orden de los faltantes.

**Qué cambiamos.** En `obtener_estado_transportista()` calculamos los faltantes una sola vez y usamos esa lista para decidir el estado y construir la respuesta. Si hay un rechazo, el estado es `RECHAZADO`. Si la lista de faltantes está vacía y todos los requeridos están aprobados, es `APROBADO`. En los demás casos queda `PENDIENTE`.

| Qué medimos dentro del método | Antes | Después |
|---|---:|---:|
| Recorridos escritos sobre la lista de documentos requeridos | 3 | 2 |
| Comprobaciones explícitas de presencia o ausencia de un tipo de documento | 2 | 1 |

**Dónde verlo y cómo lo comprobamos.** La decisión y la respuesta están juntas en `backend/app/modules/onboarding/service.py`. La prueba más ilustrativa carga solo el seguro y lo rechaza: espera `RECHAZADO` y comprueba cuáles son los otros cuatro documentos faltantes y en qué orden aparecen. [Cálculo y respuesta, líneas 120–142](https://github.com/hamburgetestudent/Camiones_contratos/blob/7858b4b/backend/app/modules/onboarding/service.py#L120-L142) · [Prueba, líneas 49–59](https://github.com/hamburgetestudent/Camiones_contratos/blob/7858b4b/backend/tests/onboarding/test_obtener_estado_transportista.py#L49-L59) · [d2c77ed](https://github.com/hamburgetestudent/Camiones_contratos/commit/d2c77ed)

## 3. Usar el mismo formato de correo al guardar y buscar una cuenta

**Qué encontramos y por qué lo priorizamos.** El guardado y la búsqueda quitaban espacios y convertían el correo a minúsculas por separado. Durante el inicio de sesión también se recortaba el correo antes de pasarlo a la búsqueda. Si registro y acceso trataran el mismo correo de forma distinta, el usuario podría tener una cuenta y aun así no encontrarla al entrar. La prioridad fue **media**: ambas reglas todavía coincidían, el cambio era pequeño y ya había pruebas de persistencia.

**Qué cambiamos en el hito.** En `services/usuario_service.py` extrajimos `_normalizar_correo()` y la usamos tanto al guardar como al buscar. La autenticación siguió rechazando campos vacíos y delegó la limpieza a la búsqueda. La consulta SQL conservó el tratamiento de correos ya almacenados. [Función y búsqueda, líneas 48–59](https://github.com/hamburgetestudent/Camiones_contratos/blob/e19568b/services/usuario_service.py#L48-L59) · [Guardado, línea 87](https://github.com/hamburgetestudent/Camiones_contratos/blob/e19568b/services/usuario_service.py#L87) · [Autenticación, línea 182](https://github.com/hamburgetestudent/Camiones_contratos/blob/e19568b/services/usuario_service.py#L182) · [e19568b](https://github.com/hamburgetestudent/Camiones_contratos/commit/e19568b)

| Qué medimos en el commit de la intervención | Antes | Después |
|---|---:|---:|
| Implementaciones Python de `strip().lower()` para el correo en guardado y búsqueda | 2 | 1 |
| Recortes del correo durante un acceso exitoso, incluida la comprobación inicial de campo vacío | 3 | 2 |

**Cómo lo comprobamos y dónde verlo hoy.** La prueba inicia sesión con `"  JUAN.CHOFER@TRANSPORTE.CL  "` y comprueba que obtiene la misma cuenta. Después del hito la persistencia pasó a `backend/app/modules/usuarios/dao.py`. En la revisión `7858b4b` el guardado y la búsqueda vuelven a contener la limpieza por separado. Por eso la tabla mide el resultado del commit original; para explicar el estado posterior hay que mostrar las dos líneas del DAO. [Prueba de acceso, líneas 42–46](https://github.com/hamburgetestudent/Camiones_contratos/blob/7858b4b/backend/tests/usuarios/test_autenticar_usuario.py#L42-L46) · [Pruebas de persistencia](../backend/tests/persistencia/test_persistencia_usuarios.py) · [Guardado, línea 47](https://github.com/hamburgetestudent/Camiones_contratos/blob/7858b4b/backend/app/modules/usuarios/dao.py#L47) · [Búsqueda, línea 84](https://github.com/hamburgetestudent/Camiones_contratos/blob/7858b4b/backend/app/modules/usuarios/dao.py#L84)

## Evidencia de ejecución

La verificación original se hizo en Windows con Python 3.15, FastAPI y SQLite. Antes de editar, se inició la aplicación con el cliente ASGI y `GET /openapi.json` respondió HTTP 200.

| Cuándo se verificó | Qué se ejecutó | Resultado |
|---|---|---|
| Antes de editar, [883b8d2](https://github.com/hamburgetestudent/Camiones_contratos/commit/883b8d2) | Suite completa del backend | 210 de 210 |
| Antes de refactorizar, [7c823b4](https://github.com/hamburgetestudent/Camiones_contratos/commit/7c823b4) | Tres módulos con las nuevas pruebas de caracterización sobre la implementación original | 13 de 13 |
| Después de la intervención 1, [0f13942](https://github.com/hamburgetestudent/Camiones_contratos/commit/0f13942) | Suite completa | 213 de 213 |
| Después de la intervención 2, [d2c77ed](https://github.com/hamburgetestudent/Camiones_contratos/commit/d2c77ed) | Suite completa | 213 de 213 |
| Después de la intervención 3, [e19568b](https://github.com/hamburgetestudent/Camiones_contratos/commit/e19568b) | Suite completa | 213 de 213 |

**Comprobación por otro integrante.** El compañero que usó la cuenta local `f4cks` comprobó la versión inicial `883b8d2`. Obtuvo los tres resultados esperados: pendiente con documentación incompleta, aprobado con cinco documentos aprobados y rechazado con al menos uno rechazado. La salida fue `Ran 3 tests in 0.301s`, `OK`. [Captura de la ejecución](comprobacion-transportista.png)

Para revisar una medición histórica, ejecutar `git show <commit>` y comparar las líneas eliminadas y añadidas. Para ejecutar las pruebas con la **estructura actual** de la rama, desde la raíz y con el entorno Python activo:

```powershell
python -m pip install -r requirements.txt httpx pytest
python -m pytest backend/tests/onboarding/test_validar_perfil_dador.py backend/tests/onboarding/test_obtener_estado_transportista.py backend/tests/usuarios/test_autenticar_usuario.py
python -m pytest backend/tests
```

## Deuda técnica postergada

El responsable de seguimiento de los tres pendientes es **santiagosanchezgarcia10-byte** y la fecha propuesta de revisión es el **2 de diciembre de 2026**.

| Pendiente y prioridad | Qué ocurre y por qué se postergó | Qué revisar el 2 de diciembre |
|---|---|---|
| **Formato y longitud del RUT · Alta** | El validador acepta `00000000000-0` y devuelve `76--123456-0` con ambos guiones. La descripción de RN-KYC-05 y el mensaje de error cuentan el largo máximo de forma distinta. Antes de restringir el registro hay que acordar qué formatos se admitirán. | Aclarar si el máximo incluye el dígito verificador y dónde puede ir el guion. Definir casos para el máximo, un dígito extra y guiones repetidos, además de los casos existentes de entradas cortas y dígito incorrecto. [Validador](../backend/app/modules/onboarding/models.py#L134-L164) · [Regla RN-KYC-05](../REGLAS_DE_NEGOCIO.md#rn-kyc-05-validación-algorítmica-del-rut-chileno-módulo-11) · [Pruebas de registro](../backend/tests/usuarios/test_registro_usuario.py) |
| **Extensiones de archivo duplicadas · Baja** | La solicitud de carga y el modelo del documento repiten las cuatro extensiones y el mensaje de error. Hoy coinciden; el riesgo aparece al agregar un formato en un solo lugar. Se priorizaron las tres intervenciones anteriores. | Probar ambos modelos con `licencia.PDF` y `licencia.exe`. Verificar que conservan el nombre original cuando aceptan el archivo y dan el mismo mensaje cuando lo rechazan, antes de extraer la regla común. [Ambos validadores](../backend/app/modules/onboarding/models.py#L43-L70) |
| **Distancia estimada al buscar cargas · Media** | Cuando falta el kilometraje y las localidades difieren, el filtro usa 150 km. Un máximo de 100 km excluye así una carga que podría estar más cerca. Cambiar la estimación exige acordar cómo mostrar rutas de distancia desconocida. | Comparar dos cargas bajo el mismo filtro, una con kilometraje registrado y otra sin él, y acordar qué debe ver el transportista. [Estimación](../backend/app/modules/subastas/service.py#L38-L50) · [Filtro](../backend/app/modules/subastas/service.py#L114-L121) · [Prueba Santiago–Concepción](../backend/tests/subastas/test_estimar_distancia.py) |
