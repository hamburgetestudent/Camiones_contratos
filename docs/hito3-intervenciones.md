# Hito 3 · Diagnóstico, refactorización y pruebas

Las tres intervenciones conservan el comportamiento de operaciones del backend: revisión administrativa, consulta de habilitación del transportista y acceso por correo. El responsable técnico registrado en Git para las tres es **santiagosanchezgarcia10-byte** (RamaSS). La base de comparación es [883b8d2](https://github.com/hamburgetestudent/Camiones_contratos/commit/883b8d2), que ya contiene los cambios publicados previamente por RamaSS.

## 1. Decisión administrativa sobre documentos y perfiles

**Prioridad alta.** En [OnboardingService.validar_documento y validar_dador](../services/onboarding_service.py), cada operación definía qué estados podía asignar el revisor. Una edición parcial permitiría resolver un perfil y un documento con criterios distintos. El esfuerzo era bajo porque ambos ya aplicaban la misma condición después de localizar el recurso.

Se extrajo una función privada que comprueba el estado solicitado. Los dos servicios siguen localizando el recurso antes de validar y persisten la decisión dentro de su transacción. Se conservan el error, su mensaje y el estado guardado cuando se intenta volver a PENDIENTE. [Cambio I1](https://github.com/hamburgetestudent/Camiones_contratos/commit/0f13942) · [Pruebas de documentos](../tests/onboarding/test_validar_documento.py) · [Pruebas de perfiles](../tests/onboarding/test_validar_perfil_dador.py).

## 2. Estado global y documentos faltantes del transportista

**Prioridad alta, segunda en el orden de ejecución.** En [OnboardingService.obtener_estado_transportista](../services/onboarding_service.py), el método comprobaba la presencia de los documentos requeridos y volvía a calcular esa información al construir la lista de faltantes. Si las comprobaciones evolucionaran por separado, la respuesta podría informar un estado incompatible con su propia lista. La modificación afecta una sola consulta, pero requiere verificar la precedencia del rechazo y el orden de los documentos.

El método calcula los faltantes una vez. Un rechazo prevalece incluso si faltan documentos. La aprobación exige una lista vacía de faltantes y que todos los requeridos estén aprobados. La respuesta mantiene el orden de los tipos requeridos. [Cambio I2](https://github.com/hamburgetestudent/Camiones_contratos/commit/d2c77ed) · [Pruebas del estado y de la lista](../tests/onboarding/test_obtener_estado_transportista.py).

## 3. Normalización del correo en persistencia y acceso

**Prioridad media.** En [guardar_usuario, buscar_usuario_por_email y autenticar_usuario](../services/usuario_service.py), la escritura y la búsqueda repetían el recorte y la conversión a minúsculas. Además, el acceso volvía a recortar el correo al delegar la búsqueda. Una divergencia entre escritura y lectura podría impedir que una persona encuentre su cuenta con el mismo correo. El esfuerzo era bajo y ya existían pruebas de persistencia.

Ambas operaciones llaman a la misma función privada. La autenticación conserva la validación de campos vacíos y delega la normalización del valor de búsqueda. La consulta SQL sigue admitiendo filas existentes con diferencias de formato. [Cambio I3](https://github.com/hamburgetestudent/Camiones_contratos/commit/e19568b) · [Pruebas de persistencia](../tests/persistencia/test_persistencia_usuarios.py) · [Pruebas de acceso](../tests/usuarios/test_autenticar_usuario.py).

## Deuda técnica postergada

**Validación incompleta del formato y la longitud del RUT de empresa.** En el registro del perfil tributario, [`CrearPerfilDadorDTO.validar_rut_formato`](../domain/modelos_onboarding.py) acepta `00000000000-0`, cuyo cuerpo tiene once dígitos. También acepta y devuelve `76--123456-0` porque elimina los guiones para calcular el dígito verificador, pero los conserva en el valor devuelto. Así pueden llegar al perfil identificadores mal formados. Las [pruebas de registro](../tests/test_registro_usuario.py) cubren el dígito verificador incorrecto y las entradas demasiado cortas; faltan casos para el exceso de longitud y los guiones repetidos.

**Prioridad alta.** Ambos casos ya pasan la validación. Se posterga la corrección hasta aclarar con el equipo si el máximo de nueve caracteres incluye el dígito verificador. La descripción de [RN-KYC-05](../REGLAS_DE_NEGOCIO.md#rn-kyc-05-validación-algorítmica-del-rut-chileno-módulo-11) y su mensaje de error cuentan ese límite de forma distinta. Cambiarlo sin resolver esa diferencia podría rechazar perfiles que el equipo considera válidos.

**Seguimiento.** Responsable: santiagosanchezgarcia10-byte (RamaSS). Fecha propuesta de revisión: **2 de diciembre de 2026**. En esa revisión se acordarán el largo permitido y la posición del guion, y se definirán los resultados esperados para el largo máximo, un dígito adicional y un guion repetido.

**Validación duplicada de las extensiones de archivo.** En [los modelos de onboarding](../domain/modelos_onboarding.py), `CargarDocumentoDTO.validar_archivo` y `DocumentoTransportistaBase.validar_archivo` declaran por separado las mismas cuatro extensiones y el mismo mensaje de error. Agregar un formato exige editar ambos validadores. Si solo se actualiza uno, la solicitud de carga puede aceptar un archivo que el modelo del documento rechace.

**Motivo de la postergación y prioridad.** La prioridad es baja porque hoy ambas listas coinciden. El riesgo aparece al cambiar los formatos admitidos. Unificar los validadores requiere comprobar los dos modelos Pydantic por separado y conservar el valor de archivo que devuelve cada uno. Esa tarea queda para una intervención posterior a las tres verificadas en este hito.

**Responsable de seguimiento:** santiagosanchezgarcia10-byte (RamaSS). **Fecha propuesta de revisión:** 2 de diciembre de 2026. En esa revisión se comprobará que ambos modelos acepten un nombre como `licencia.PDF`, rechacen `licencia.exe` con el mismo mensaje y conserven el nombre original. Esos casos servirán para verificar la extracción de una regla común.

**Estimación fija de distancia al explorar cargas.** Cuando un contrato carece de distancia registrada, [el servicio de subastas](../services/subasta_service.py) asigna 150 km a cualquier trayecto entre dos localidades distintas. Por ejemplo, con un máximo de 100 km el filtro excluye todas esas cargas, incluso si alguna ruta real es más corta. Una [prueba de distancia](../tests/subastas/test_estimar_distancia.py) documenta la estimación actual para Santiago y Concepción.

**Prioridad media.** La aproximación afecta la selección de cargas cuando se filtra por distancia y el contrato carece de kilometraje. Se posterga el cambio porque el equipo debe acordar cómo tratar una distancia desconocida antes de alterar los resultados que recibe el transportista.

**Seguimiento.** Se propone que santiagosanchezgarcia10-byte revise esta decisión el **2 de diciembre de 2026**. Para esa revisión se compararán dos cargas con el mismo filtro, una con kilometraje registrado y otra sin él, y se acordará el resultado esperado para ambas.

## Medición reproducible

Se comparó cada commit con su padre. Los conteos son estáticos y abarcan únicamente las operaciones y las funciones extraídas que se describen arriba. Para revisar las dos versiones, ejecutar `git show <commit> -- <archivo>`.

| Intervención | Indicador dentro del alcance | Antes | Después |
|---|---|---:|---:|
| 1 | Condiciones que definen las decisiones de revisión admitidas | 2 | 1 |
| 1 | Lugares donde se define el mensaje por decisión inválida | 2 | 1 |
| 2 | Recorridos escritos sobre DOCUMENTOS_REQUERIDOS_TRANSPORTISTA | 3 | 2 |
| 2 | Comprobaciones explícitas de presencia o ausencia de un tipo en docs_por_tipo | 2 | 1 |
| 3 | Implementaciones Python de la secuencia strip().lower() para el correo | 2 | 1 |
| 3 | Recortes aplicados al correo no vacío durante una autenticación exitosa, incluida la validación inicial | 3 | 2 |

## Evidencia de ejecución

Entorno de verificación: Windows, Python 3.15, FastAPI y SQLite. En la base, el cliente ASGI ejecutó el arranque de la aplicación y obtuvo HTTP 200 en `GET /openapi.json`.

| Revisión | Verificación | Resultado |
|---|---|---|
| 883b8d2 | Suite del backend antes de editar | 210 de 210 |
| [7c823b4](https://github.com/hamburgetestudent/Camiones_contratos/commit/7c823b4) | Tres módulos de caracterización sobre el código original | 13 de 13 |
| Cambio I1 | Suite del backend | 213 de 213 |
| Cambio I2 | Suite del backend | 213 de 213 |
| Cambio I3 | Suite del backend | 213 de 213 |

Desde la raíz, con el entorno Python activo:

```powershell
python -m pip install -r requirements.txt httpx pytest
python -m unittest tests.onboarding.test_validar_perfil_dador tests.onboarding.test_obtener_estado_transportista tests.usuarios.test_autenticar_usuario -v
python -m unittest discover -s tests -t .
```

**Comprobación inicial por otro integrante.** El compañero ejecutó la revisión desde la cuenta local `f4cks`. La salida de Git compartida previamente situó la copia en `883b8d2`. La captura muestra los tres resultados esperados: APROBADO con cinco documentos aprobados, PENDIENTE cuando faltan documentos y RECHAZADO cuando al menos uno está rechazado. Resultado de unittest: `Ran 3 tests in 0.301s`, `OK`. [Ver captura de la ejecución](comprobacion-transportista.png).
