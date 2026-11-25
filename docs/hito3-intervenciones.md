# Hito 3 · Diagnóstico, refactorización y pruebas

Las tres intervenciones conservan el comportamiento de operaciones del backend: revisión administrativa, consulta de habilitación del transportista y acceso por correo. El responsable técnico registrado en Git para las tres es **santiagosanchezgarcia10-byte** (RamaSS). La base de comparación es [883b8d2](https://github.com/hamburgetestudent/Camiones_contratos/commit/883b8d2), que ya contiene los cambios publicados previamente por RamaSS.

## 1. Decisión administrativa sobre documentos y perfiles

**Prioridad alta.** En [OnboardingService.validar_documento y validar_dador](../backend/app/modules/onboarding/service.py), cada operación definía qué estados podía asignar el revisor. Una edición parcial permitiría resolver un perfil y un documento con criterios distintos. El esfuerzo era bajo porque ambos ya aplicaban la misma condición después de localizar el recurso.

Se extrajo una función privada que comprueba el estado solicitado. Los dos servicios siguen localizando el recurso antes de validar y persisten la decisión dentro de su transacción. Se conservan el error, su mensaje y el estado guardado cuando se intenta volver a PENDIENTE. [Cambio I1](https://github.com/hamburgetestudent/Camiones_contratos/commit/0f13942) · [Pruebas de documentos](../backend/tests/onboarding/test_validar_documento.py) · [Pruebas de perfiles](../backend/tests/onboarding/test_validar_perfil_dador.py).

## 2. Estado global y documentos faltantes del transportista

**Prioridad alta, segunda en el orden de ejecución.** En [OnboardingService.obtener_estado_transportista](../backend/app/modules/onboarding/service.py), el método comprobaba la presencia de los documentos requeridos y volvía a calcular esa información al construir la lista de faltantes. Si las comprobaciones evolucionaran por separado, la respuesta podría informar un estado incompatible con su propia lista. La modificación afecta una sola consulta, pero requiere verificar la precedencia del rechazo y el orden de los documentos.

El método calcula los faltantes una vez. Un rechazo prevalece incluso si faltan documentos. La aprobación exige una lista vacía de faltantes y que todos los requeridos estén aprobados. La respuesta mantiene el orden de los tipos requeridos. [Cambio I2](https://github.com/hamburgetestudent/Camiones_contratos/commit/d2c77ed) · [Pruebas del estado y de la lista](../backend/tests/onboarding/test_obtener_estado_transportista.py).

## 3. Normalización del correo en persistencia y acceso

**Prioridad media.** En [guardar_usuario, buscar_usuario_por_email y autenticar_usuario](../backend/app/modules/usuarios/service.py), la escritura y la búsqueda repetían el recorte y la conversión a minúsculas. Además, el acceso volvía a recortar el correo al delegar la búsqueda. Una divergencia entre escritura y lectura podría impedir que una persona encuentre su cuenta con el mismo correo. El esfuerzo era bajo y ya existían pruebas de persistencia.

Ambas operaciones llaman a la misma función privada. La autenticación conserva la validación de campos vacíos y delega la normalización del valor de búsqueda. La consulta SQL sigue admitiendo filas existentes con diferencias de formato. [Cambio I3](https://github.com/hamburgetestudent/Camiones_contratos/commit/e19568b) · [Pruebas de persistencia](../backend/tests/persistencia/test_persistencia_usuarios.py) · [Pruebas de acceso](../backend/tests/usuarios/test_autenticar_usuario.py).

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
python -m unittest discover -s backend/tests -t backend
```

**Comprobación inicial por otro integrante.** El compañero ejecutó la revisión desde la cuenta local `f4cks`. La salida de Git compartida previamente situó la copia en `883b8d2`. La captura muestra los tres resultados esperados: APROBADO con cinco documentos aprobados, PENDIENTE cuando faltan documentos y RECHAZADO cuando al menos uno está rechazado. Resultado de unittest: `Ran 3 tests in 0.301s`, `OK`. [Ver captura de la ejecución](comprobacion-transportista.png).
