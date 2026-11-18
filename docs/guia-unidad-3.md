
# Guía Unidad 3 — Refactorización y modularización

## TD-01 — Refactorización del módulo de autenticación

**Responsable:** Cristian Palma
**Rama de trabajo:** `Cristian`
**Prioridad:** Alta
**Estado:** Implementación y pruebas completadas. Pendiente de revisión e integración mediante PR.

### 1. Identificación del problema

Se identificó duplicación de código en los siguientes archivos:

- `services/usuario_service.py`
- `services/login_service.py`

Ambos servicios contenían lógica para convertir los datos de rol y estado del usuario, preparar los datos del token de autenticación y construir la respuesta `RespuestaLogin`.

Esta duplicación constituye una oportunidad de mejora, debido a que cualquier modificación futura en la estructura de la respuesta debía realizarse en ambos lugares, aumentando el riesgo de inconsistencias y la deuda técnica.

### 2. Objetivo de la refactorización

Centralizar la construcción de las respuestas de autenticación en un único componente reutilizable, manteniendo el comportamiento original del sistema.

La intervención no modifica las reglas de validación de credenciales ni el mecanismo existente de generación de tokens.

### 3. Solución implementada

Se creó el archivo:

`services/respuesta_login.py`

Este módulo contiene la función:

`construir_respuesta_login()`

La función concentra la preparación de los datos del usuario, los atributos de la respuesta y la generación del token mediante el componente de seguridad existente.

Los servicios `UsuarioService` y `LoginService` ahora utilizan esta función compartida.

Se mantienen las validaciones y las excepciones originales de cada servicio.

### 4. Contrato del componente reutilizable

**Nombre:** `construir_respuesta_login`

**Ubicación:** `services/respuesta_login.py`

**Entradas:**

- `datos_usuario: UsuarioModelo | None`
- `usuario_solicitado: str`

**Salida:**

- Objeto `RespuestaLogin` con token Bearer, rol, identificador, nombre, correo, estado y mensaje de autenticación.

**Comportamiento:**

- Si existe información del usuario, utiliza sus datos para construir la respuesta.
- Si no existen datos adicionales del perfil, conserva el comportamiento previsto de `LoginService`, utilizando el rol predeterminado `USUARIO`.
- Utiliza `crear_token_acceso()` de `services/security.py`.
- Conserva el identificador de respuesta correspondiente a cada servicio.

**Errores:**

- La validación de credenciales permanece en el servicio que realiza la autenticación.
- `LoginService` mantiene la excepción `CredencialesInvalidasError`.
- `UsuarioService` mantiene sus excepciones HTTP originales.
- Los errores de creación del token o validación del modelo pueden propagarse desde sus componentes correspondientes.

**Ejemplo de utilización:**

En `UsuarioService`:

`construir_respuesta_login(datos_usuario=usuario, usuario_solicitado=usuario.email)`

En `LoginService`:

`construir_respuesta_login(datos_usuario=datos_usuario, usuario_solicitado=credenciales.usuario)`

### 5. Comparación antes y después

| Indicador | Antes | Después |
|---|---|---|
| Lugares con construcción directa de `RespuestaLogin` en los dos servicios | 2 | 0 |
| Funciones compartidas para construir la respuesta | 0 | 1 |
| Servicios que utilizan la nueva función compartida | 0 | 2 |
| Pruebas automatizadas ejecutadas | 183 | 184 |
| Pruebas fallidas | 0 | 0 |

La construcción de respuestas que anteriormente se encontraba duplicada en ambos servicios se centralizó en un componente compartido.

La cantidad de pruebas aumentó porque se incorporó una prueba de caracterización antes de completar la refactorización.

### 6. Pruebas y verificación

Antes de modificar la lógica de los servicios se ejecutó la batería de pruebas del proyecto, obteniendo 183 pruebas aprobadas.

Posteriormente se incorporó una prueba de caracterización en:

`tests/usuarios/test_iniciar_sesion.py`

La nueva prueba verifica el inicio de sesión válido cuando no se dispone de información adicional del perfil del usuario.

La prueba fue registrada en el commit:

`d753e6f` — `test(auth): agrega prueba de caracterizacion TD-01`

Después de integrar el componente reutilizable en ambos servicios se ejecutó:

`python -m unittest discover -t . -s tests`

**Resultado final: 184 pruebas ejecutadas y aprobadas (OK).**

También se ejecutó:

`git diff --check`

El comando no reportó errores de espacios.

Estas pruebas aportan evidencia de que los escenarios automatizados existentes continúan funcionando después de la refactorización.

### 7. Relación con las clases de la Unidad 3

**Clase 3.1 — Refactorización sistemática**

Se realizaron pruebas antes y después de modificar el código y se mantuvo el comportamiento esperado en los escenarios comprobados.

**Clase 3.2 — Code smells y deuda técnica**

Se identificó la duplicación de la construcción de respuestas de autenticación y se eliminó esa responsabilidad repetida de ambos servicios.

**Clase 3.3 — Componentes reutilizables**

Se creó una función compartida con entradas, salida y responsabilidades definidas, utilizada por dos servicios distintos.

### 8. Archivos involucrados

- `services/respuesta_login.py` — Nuevo componente compartido.
- `services/usuario_service.py` — Integración del componente.
- `services/login_service.py` — Integración del componente.
- `tests/usuarios/test_iniciar_sesion.py` — Prueba de caracterización.
- `docs/guia-unidad-3.md` — Documentación de la intervención.

### 9. Evidencias pendientes de integración

- Registrar el commit final de refactorización TD-01.
- Publicar la rama correspondiente cuando el equipo lo indique.
- Crear o asociar el Pull Request hacia `Dev`.
- Registrar la revisión de pares y la ejecución de CI.
- Integrar las intervenciones TD-02 y TD-03 realizadas por los demás integrantes.

---

## TD-02 — Pendiente de documentación por el equipo

Esta sección será completada por el integrante responsable.

## TD-03 — Pendiente de documentación por el equipo

Esta sección será completada por el integrante responsable.
