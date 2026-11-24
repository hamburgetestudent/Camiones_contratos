# Criterio 4 · Modularización de las interfaces y dependencias

**Proyecto Camiones_contratos · Hito 3 ISF224 · Rama Cristian**

El caso TD-01 muestra cómo dos servicios de autenticación conservan sus respectivas validaciones y delegan la construcción de la respuesta en una misma operación pública. El caso elegido para comparar ambas versiones es un inicio de sesión con credenciales aceptadas por un validador de prueba que devuelve un perfil vacío (`None`).

## Operaciones que colaboran

| Quién llama | Operación que usa | Datos intercambiados y responsabilidad |
|---|---|---|
| [LoginService.iniciar_sesion](../services/login_service.py#L40) | `validador.validar(usuario, password)` y, si está disponible, `obtener_datos_usuario(usuario)` | El servicio recibe `CredencialesLogin`. El validador inyectado devuelve un booleano y puede aportar el perfil. Si rechaza las credenciales, el servicio lanza `CredencialesInvalidasError`. |
| [LoginService, línea 70](../services/login_service.py#L70) | `construir_respuesta_login(datos_usuario, usuario_solicitado)` | Pasa el perfil disponible y el identificador escrito al iniciar sesión. Devuelve al llamador la respuesta del componente. |
| [UsuarioService, línea 249](../services/usuario_service.py#L249) | La misma función | Tras sus propias validaciones, pasa el usuario autenticado y su correo. Devuelve la misma clase de respuesta. |
| [construir_respuesta_login, línea 21](../services/respuesta_login.py#L21) | [crear_token_acceso](../services/security.py#L37) | En la línea 66 envía un diccionario con el identificador, correo y rol. Seguridad devuelve el token. En la línea 75 el componente incorpora ese token al modelo de salida `RespuestaLogin`. |

Los dos servicios importan el constructor común. Este depende de los modelos de dominio y de la operación de seguridad. Así, cambiar cómo se arma la respuesta tiene un único punto de modificación.

## El mismo caso antes y después

| Versión ejecutada | Cómo se construía la respuesta | Resultado de la prueba |
|---|---|---|
| Antes · `75f7bbf`, padre de la refactorización | Cada servicio llamaba directamente a seguridad y construía su propia respuesta. Ver `services/login_service.py`, líneas 70 y 78, y `services/usuario_service.py`, líneas 148 y 156 de esa revisión. | 1 prueba ejecutada, OK |
| Después · `e85dcc4`, rama Cristian | Ambos servicios llaman al constructor compartido introducido en `9b20d3f`. | La misma prueba pasó. También pasaron las 13 pruebas del archivo de inicio de sesión. |

**Qué se comprobó.** En [test_login_sin_datos_usuario](../tests/usuarios/test_iniciar_sesion.py#L128) el validador acepta las credenciales de prueba de `sinperfil@ejemplo.cl` y devuelve `None` como perfil. La prueba exige rol `USUARIO`, usuario y correo iguales a la entrada, y campos id, nombre y estado en `None`. También decodifica el token y comprueba su identificador (`sub`) y rol.

## Cómo reproducir la comparación en macOS

Desde la raíz del repositorio y con su entorno Python activo, ejecutar este bloque en la terminal de Visual Studio Code. La versión anterior se extrae a una carpeta temporal. La rama abierta y sus archivos locales se conservan.

```bash
caso=tests.usuarios.test_iniciar_sesion.TestIniciarSesion.test_login_sin_datos_usuario
antes=$(mktemp -d)
git archive 75f7bbf | tar -x -C "$antes"
(cd "$antes" && python -m unittest -v "$caso")
python -m unittest -v "$caso"
```

Para revisar también el segundo servicio, los errores de credenciales y el contrato del constructor, ejecutar `python -m unittest -v tests.usuarios.test_iniciar_sesion`.

## Recorrido para la defensa

Abrir la llamada del primer servicio (línea 70), mostrar la segunda llamada (línea 249), entrar a la definición común (línea 21) y terminar en la prueba (línea 128). En Visual Studio Code para Mac, usar ⌘P y escribir la ruta seguida de dos puntos y la línea.
